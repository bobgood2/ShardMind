import dis
import os
import numpy as np
import faiss
import json
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import who_search
import when_search
import traceback

app = Flask(__name__)

#constants
k_months = 3            # the number of months to precache embeddings, and to allow complete searches if possible
k_group = 300           # the number of scattered embeddings we are willing to read from disk before doing an approximate search
k_take_multiplier = 40  # take is multiplied by this if we need to filter after a search over a large corpus

# Path to the saved FAISS index
index_file_path = r'C:\download\email_index.faiss'
mapping_file_path = r'c:\download\email_index_mappings'
emails_dir = 'C:\download\emails'
posting_list_dir = 'C:\download\email_posting_lists'

indexed_embeddings = r'C:\download\emails_indexed_embeddings'
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the mapping
with open(mapping_file_path, 'r') as f:
    filenames = json.load(f)

# Load the FAISS index
print ("loading index")    
index = faiss.read_index(index_file_path)

# Define the dimension of embeddings (should match your embeddings' dimension)
embedding_dim = 384

print ("loading ages")    
when_search = when_search.WhenSeach()

when_search.read_when('C:\download\email_when.json')

k_recent = when_search.items_over_n_months(k_months)

print ("loading people info")    
who_search = who_search.WhoSeach()

who_search.read_who('C:\download\email_who.json')

posting_list_cache = {}
def read_posting_list(fn):
    if fn in posting_list_cache:
        return posting_list_cache[fn]
    with open(os.path.join(posting_list_dir, fn), 'r') as f:
        try:
            item = json.load(f)["posting_list"]
            posting_list_cache[fn]=item
            return item
        except:
            return []
expected_embedding_dim=384
embedding_cache = {}
def read_embedding(index):
    if index in embedding_cache:
        return embedding_cache[index]
    file_path=os.path.join(indexed_embeddings, str(index)+".npy")
    embedding = np.load(file_path)
    if embedding.shape[0] != expected_embedding_dim:
        raise ValueError("mismatched embedding shape")
    embedding_cache[index]=embedding
    return embedding

# preload cache
print (f"preloading embeddings cache {k_recent}")    
for idx in range(k_recent):
    read_embedding(idx)

bool_posting_lists=["isRead", "isDraft", "hasAttachments"]
def add_bool_posting_lists(posting_lists, neg_posting_lists, query):
    for item in bool_posting_lists:
        if item in query:
            val=query[item]
            if val==False:
                neg_posting_lists.append(read_posting_list(item))
            else:
                posting_lists.append(read_posting_list(item))
 
def change_extension_and_path(filename, new_path, new_extension):
    # Get the base name without the extension
    base_name = os.path.splitext(os.path.basename(filename))[0]
    # Construct the new filename
    new_filename = os.path.join(new_path, base_name + new_extension)
    return new_filename

def get_raw_emails(idx):
    fn = filenames[int(idx)]
    file_path = change_extension_and_path(fn, emails_dir, ".json")
    with open(file_path, 'r') as file:
        return json.load(file)
    
def euclidean_distance(a, b):
    return np.linalg.norm(a - b)

def short_search(query_embedding, union_set, take):
    distances=[]
    for index in union_set:
        embedding = read_embedding(index)
        dist = euclidean_distance(query_embedding, embedding)
        distances.append((dist, index))
        
    distances.sort(key=lambda x: x[0])
    if len(distances)>take:
        distances=distances[:take]
    return distances

def post_filter_search(query_embedding, union_set, take):
    fdistances, findices = index.search(query_embedding, take*k_take_multiplier)
    filtered = [(float(dist), int(idx)) for idx, dist in zip(findices[0], fdistances[0])]

    filtered.sort(key=lambda x: x[0])
    if len(filtered)>take:
        filtered=filtered[:take]
    return filtered
   
@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.json
        print(query)
        posting_lists_names, backup_text = who_search.request(query)
        posting_lists=[read_posting_list(item) for item in posting_lists_names]
        neg_posting_lists=[]
        
        add_bool_posting_lists(posting_lists, neg_posting_lists, query)
        union_set = set()
        for s in posting_lists:
            union_set.update(s)

        for s in neg_posting_lists:
            union_set.difference_update(s)
            
        #inclusive ranges
        first, last=when_search.request(query)
        
        # if there is a union set, then apply range.  there might not be a union set
        if union_set and first<=last:
            union_set = {x for x in union_set if first <= x <= last}
        if not union_set and first<=last:
            union_set=set(range(first, last + 1))

        # Get the query string from the JSON data
        query_text = query.get('text', '')        
        if len(query_text)==0:
            query_text = backup_text
        # Generate the embedding for the query string
        query_embedding = model.encode([query_text], convert_to_tensor=True).cpu().numpy().reshape(1, -1)
        
        # Check if the query embedding has the correct dimension
        if query_embedding.shape[1] != embedding_dim:
            return jsonify({'error': f'Invalid embedding dimension. Expected {embedding_dim}, got {query_embedding.shape[1]}'})
        
        # Number of nearest neighbors to search for
        take = int(request.json.get('take', 5))
        
        if (len(union_set)<k_group or max(union_set)<k_recent):
            # go through one by one and calculate
            print(f"small scenario: {len(union_set)}")
            distances = short_search(query_embedding, union_set, take)
            pass 
        elif not union_set:
            print(f"normal scenario: {len(union_set)}")
            # do a normal search5z
            fdistances, findices = index.search(query_embedding, take)
            distances = [(float(dist), int(idx)) for idx, dist in zip(findices[0], fdistances[0])]
            distances.sort(key=lambda x: x[0])
        else:
            print(f"mixed scenario: {len(union_set)}")
            # do a broader search and then post-filter  ughhh5
            # maybe we can have a shorter index built for the last few months or so...
            distances = post_filter_search(query_embedding, union_set, take)
            pass

        # Perform the search
        
        results = []
        # Prepare the response
        for dist, idx in distances:
            raw_email=get_raw_emails(idx)
            result= {'id': int(idx), 'email': raw_email, 'distance':float(dist)}
            results.append(result)
            
        return jsonify(results)
    
    except Exception as e:
        stack_trace = traceback.format_exc()
        return jsonify({'error': str(e), 'stack': stack_trace}), 400

if __name__ == '__main__':
    print("starting server")
    app.run(debug=True, host='0.0.0.0', port=5001)
