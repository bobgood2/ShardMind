import os
import numpy as np
import faiss
import json

def load_embeddings_from_directory(directory, expected_embedding_dim):
    embeddings_list = []
    filenames = []
    cnt=0
    for file_name in os.listdir(directory):
        if file_name.endswith('.npy'):
            cnt+=1
            if cnt%100==0:
                print(cnt)
            file_path = os.path.join(directory, file_name)
            embedding = np.load(file_path)
            if embedding.shape[0] != expected_embedding_dim:
                print(f"Skipping {file_name}: Expected dimension {expected_embedding_dim}, got {embedding.shape[0]}")
                continue

            embeddings_list.append(embedding)
            filenames.append(file_name)

    embeddings = np.vstack(embeddings_list)
    if embeddings.shape[1] != expected_embedding_dim:
        print(f"error: Expected dimension {expected_embedding_dim}, got {embeddings.shape[1]}")
        raise ValueError

    return embeddings, filenames  # Combine into a single NumPy array

# Directory containing the .npy embedding files
embeddings_dir = r'C:\download\emails_embeddings'
embeddings, filenames = load_embeddings_from_directory(embeddings_dir, 384)

print(f"Loaded {len(embeddings)} embeddings with shape {embeddings.shape}")

# Create a FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])  # Using L2 distance

# Add embeddings to the index
index.add(embeddings)

print("FAISS index created and embeddings added")

# Path to save the FAISS index
index_file_path = r'C:\download\email_index'
mapping_file_path = r'C:\download\email_index_mappings'

# Save the index
faiss.write_index(index, index_file_path)

with open(mapping_file_path, 'w') as f:
    json.dump(filenames, f)

print(f"FAISS index saved to {index_file_path}")
