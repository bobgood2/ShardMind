import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

class WhenSeach():
    def __init__(self):
        self.data=[]
                
    def read_when(self, fname):
        with open(fname, 'r') as file:
            json_data = json.load(file)
            self.data=[self.timestamp(item) for item in json_data]

    def timestamp(self, date_string):
        try:
            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")    
        except:
            try:
                return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")    
            except:
                print(f"could not parse date string {date_string}")
            
    def reverse_bisect_left(self, a, x, lo=0, hi=None):
        if hi is None:
            hi = len(a)
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] > x:  # Reverse logic for descending order
                lo = mid + 1
            else:
                hi = mid
        return lo

    def get_time_point(self, datestr, after):
        stamp=self.timestamp(datestr)
        point = self.reverse_bisect_left(self.data, stamp)
        if after:
            while point<len(self.data)-1 and self.data[point]==self.data[point+1]:
                point+=1
        else:
            while point>1 and self.data[point]==self.data[point-1]:
                point-=1
        return point
    
    def request(self, query):
        start = len(self.data)-1
        end = 0
        if "after" in query:
            start = self.get_time_point(query["after"], True)
        if "before" in query:
            end = self.get_time_point(query["before"], False)
        if start>=len(self.data):
            start=len(self.data)-1
        return end,start

    def items_over_n_months(self, n_months):
        current_date = datetime.now()
        past_date = current_date - relativedelta(months=n_months) 
        return self.reverse_bisect_left(self.data, past_date)

if __name__ == "__main__":
    # Example usage
    when_search = WhenSeach()

    when_search.data = [
                       when_search.timestamp('2023-01-01T17:00:00Z'),
                       when_search.timestamp('2023-01-01T16:00:00Z'),
                       when_search.timestamp('2023-01-01T16:00:00Z'),
                       when_search.timestamp('2023-01-01T15:00:00Z'),
                       when_search.timestamp('2023-01-01T15:00:00Z'),
                       when_search.timestamp('2023-01-01T14:00:00Z'),
                       when_search.timestamp('2023-01-01T14:00:00Z'),
                       ] 


    print(when_search.request({'after': '2023-01-01T15:00:00Z', 'before': '2023-01-01T15:00:00Z'}))  # Output: {1, 2, 3}
    print(when_search.request({'after': '2023-01-01T15:00:00Z', 'before': '2023-01-01T16:00:00Z'}))  # Output: {1, 2, 3}
    print(when_search.request({'after': '2023-01-01T14:00:00Z', 'before': '2023-01-01T17:00:00Z'}))  # Output: {1, 2, 3}
    print(when_search.request({'after': '2023-01-01T12:00:00Z', 'before': '2023-01-01T18:00:00Z'}))  # Output: {1, 2, 3}
    print(when_search.request({'afterx': '2023-01-01T12:00:00Z', 'beforex': '2023-01-01T18:00:00Z'}))  # Output: {1, 2, 3}
    pass