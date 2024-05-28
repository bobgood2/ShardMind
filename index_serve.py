import os
import numpy as np
import faiss
import json
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import who_search
import when_search

app = Flask(__name__)

# Path to the saved FAISS index
index_file_path = r'C:\download\email_index.faiss'
mapping_file_path = r'c:\download\email_index_mappings'
posting_list_dir = 'C:\download\email_posting_lists'
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the mapping
with open(mapping_file_path, 'r') as f:
    filenames = json.load(f)


# Load the FAISS index
index = faiss.read_index(index_file_path)

# Define the dimension of embeddings (should match your embeddings' dimension)
embedding_dim = 384

when_search = when_search.WhenSeach()

when_search.read_when('C:\download\email_when.json')

who_search = who_search.WhoSeach()

who_search.read_who('C:\download\email_who.json')
cache = {}
def read_posting_list(fn):
    if fn in cache:
        return cache[fn]
    with open(os.path.join(posting_list_dir, fn), 'r') as f:
        item = json.load(f)
        cache[fn]=item
        return item
    

bool_posting_lists=["isRead", "isDraft", "hasAttachments"]
def add_bool_posting_lists(posting_lists, neg_posting_lists, query):
    for item in bool_posting_lists:
        if item in query:
            val=query[item]
            if val==False:
                neg_posting_lists.append(read_posting_list(item))
            else:
                posting_lists.append(read_posting_list(item))
            
   
@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        query = jsonify(data)
        posting_lists, backup_text = who_search.request(query)
        neg_posting_lists=[]
        
        add_bool_posting_lists(posting_lists, neg_posting_lists, query)
        union_set = set()
        for s in posting_lists:
            union_set.update(s)

        for s in neg_posting_lists:
            union_set.difference_update(s)
            
        #inclusive ranges
        first, last=when_search.get_time_range(query)
        
        # if there is a union set, then apply range.  there might not be a union set
        if union_set and first<=last:
            union_set = {x for x in union_set if first <= x <= last}
        if not union_set and first<=last:
            union_set=set(range(first, last + 1))

        # Get the query string from the JSON data
        query_text = data.get('text', '')        
        if len(query_text)==0:
            query_text = backup_text
        # Generate the embedding for the query string
        query_embedding = model.encode([query_text], convert_to_tensor=True).cpu().numpy().reshape(1, -1)
        
        # Check if the query embedding has the correct dimension
        if query_embedding.shape[1] != embedding_dim:
            return jsonify({'error': f'Invalid embedding dimension. Expected {embedding_dim}, got {query_embedding.shape[1]}'})
        
        # Number of nearest neighbors to search for
        take = int(request.json.get('take', 5))
        
        if (len(union_set<300)):
            # go through one by one and calculate
            pass 
        elif not union_set:
            # do a normal search
            distances, indices = index.search(query_embedding, take)
        else:
            # do a broader search and then post-filter  ughhh
            # maybe we can have a shorter index built for the last month or so...
            pass

        # Perform the search
        
        # Prepare the response
        results = [{'index': int(idx), 'fn': filenames[int(idx)], 'distance': float(dist)} for idx, dist in zip(indices[0], distances[0])]
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
