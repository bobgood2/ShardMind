import pytrie
import json
import re
from itertools import combinations

def sanitize_filename(input_tuple, max_length=250):
    # Combine the tuple elements into a single string
    combined_string = "_".join(input_tuple)
    
    # Define a regular expression pattern to match illegal filename characters
    illegal_chars_pattern = r'[<>:"/\\|?*()@\' \x00-\x1F]'
    
    # Replace illegal characters with an underscore
    sanitized_string = re.sub(illegal_chars_pattern, '_', combined_string)
    
    # Truncate the string if it's longer than the maximum allowed length
    if len(sanitized_string) > max_length:
        sanitized_string = sanitized_string[:max_length]
    
    # Add the .json extension
    filename = sanitized_string + ".json"
    
    return filename


class WhoSeach(pytrie.Trie):
    def __init__(self):
        super(WhoSeach, self).__init__()
        self.match={}
        self.data=[]
                
    def read_who(self, fname):
        with open(fname, 'r') as file:
            json_data = json.load(file)
            self.data=json_data
            for index in range(len(json_data)):
                item= json_data[index]
                self.index(index, item[0].lower(), item[1].lower())
            pass

    def index(self,index, item0, item1):
        if len(item0.split())>1 and len(item0)>4:
            self.match[item0]=index
        self.match[item1]=index
        for word in item0.split():
            if len(word)>0:
                self.insert(word, index)
        self.insert(item1, index)
    
    def insert(self, key, value):
        if key in self:
            self[key].add(value)
        else:
            self[key] = {value}
    
    def search(self, prefixu, take=5):
        prefix = prefixu.lower()
        if prefix in self.match:
            return self.data[self.match[prefix]]

        sets = []
        parts = prefix.split()
        for part in prefix.split():
            if len(part)>0:
                presults = set([])
                for key in self.iterkeys(part):
                    presults.update(self[key])
                if len(presults)>0:
                    sets.append(presults)

        if len(sets)==0:
            return []
        elif len(sets)==1:
            result=sets[0]
        else:
            result = self.progressive_union_of_intersections(sets)                
                
        list=[(self.data[item], self.score(self.data[item]), item) for item in result]
        sorted_list = sorted(list, key=lambda x: x[1], reverse=True)
        if len(sorted_list)>take:
            sorted_list = sorted_list[:take]
        return [self.summarize(item[0]) for item in sorted_list]

    def summarize(self, item):
        item0=item[0]
        item1=item[1]
        result = {}
        for sub in item[3]:
            grp=sub[0]
            fname = sanitize_filename((grp, item0, item1))
            result[grp]=fname
        return result            
               
    def score(self, item):
        total=0
        for loc in item[3]:
            if loc[0]=='sender':
                total+= loc[1]*1
            if loc[0]=='from':
                total+= loc[1]*3
            elif loc[0]=='toRecipients':
                total+= loc[1]*2
            elif loc[0]=='ccRecipients':
                total+= loc[1]
            elif loc[0]=='bccRecipients':
                total+= loc[1]*.5
            elif loc[0]=='replyTo':
                total+= loc[1]*2
            else:
                total+=loc[1]
        return total
    
    def progressive_union_of_intersections(self, sets):
        # Step 1: Start with the intersection of all sets
        full_intersection = set.intersection(*sets)
    
        if full_intersection:
            return full_intersection

        # Step 2: If empty, progressively check intersections excluding one set, two sets, etc.
        num_sets = len(sets)
    
        for r in range(num_sets - 1, 0, -1):
            all_intersections = []
            for subset in combinations(sets, r):
                current_intersection = set.intersection(*subset)
                if current_intersection:
                    all_intersections.append(current_intersection)
            if all_intersections:
                union_of_intersections = set.union(*all_intersections)
                if union_of_intersections:
                    return union_of_intersections

        # Step 3: If no intersection found, return the union of all sets
        return set.union(*sets)
    
    def request(self, request):
        posting_lists=[]
        grps=['sender','from','toRecipients','ccRecipients','bccRecipients','replyTo']
        all_text=[]
        for grp in grps:
            if grp in request:
                text= request[grp]
                for sub in text.split(','):
                    all_text.append(sub)
                    results = self.search(sub.strip())
                    for result in results:
                        if grp in result:
                            posting_lists.append(result[grp])
        return posting_lists, " ".join(all_text)
        

if __name__ == "__main__":
    # Example usage
    search = WhoSeach()

    search.read_who('C:\download\email_who.json')

    r2, lo=search.request({'from': 'bob, nitin', 'ccRecipients': 'shob'})
    print(r2)  # Output: {1, 2, 3}

    print(search.search('bob'))  # Output: {1, 2, 3}

    print(search.search('bob g'))  # Output: {1, 2, 3}
    print(search.search('shobana qqq b'))  # Output: {1, 2, 3}
    print(search.search('banana'))  # Output: {4}
    print(search.search('nitin'))  # Output: {4}
    print(search.search('a'))  # Output: {1, 2, 3}