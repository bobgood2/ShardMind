import os
import numpy as np
import faiss
import json
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Path to the saved FAISS index
index_file_path = r'C:\download\email_index'
mapping_file_path = r'c:\download\email_index_mappings'
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the mapping
with open(mapping_file_path, 'r') as f:
    filenames = json.load(f)


# Load the FAISS index
index = faiss.read_index(index_file_path)

# Define the dimension of embeddings (should match your embeddings' dimension)
embedding_dim = 384


@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        
        # Get the query string from the JSON data
        query_text = data.get('text', '')        
        # Generate the embedding for the query string
        query_embedding = model.encode([query_text], convert_to_tensor=True).cpu().numpy().reshape(1, -1)
        
        # Check if the query embedding has the correct dimension
        if query_embedding.shape[1] != embedding_dim:
            return jsonify({'error': f'Invalid embedding dimension. Expected {embedding_dim}, got {query_embedding.shape[1]}'})
        
        # Number of nearest neighbors to search for
        k = int(request.json.get('k', 5))
        
        # Perform the search
        distances, indices = index.search(query_embedding, k)
        
        # Prepare the response
        results = [{'index': int(idx), 'fn': filenames[int(idx)], 'distance': float(dist)} for idx, dist in zip(indices[0], distances[0])]
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
