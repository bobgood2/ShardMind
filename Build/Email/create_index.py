import sys
import os
sys.path.append(os.getcwd())
import numpy as np
import faiss
import json
from datetime import datetime
import shutil
from Config import config

# create_index depends on build.
# creates the index and the index_mappings

def load_embeddings_from_directory(directory, expected_embedding_dim):
    embeddings_list = []
    filenames = []
    ages = []
    cnt = 0
    for file_name in os.listdir(directory):
        if file_name.endswith('.npy'):
            cnt += 1
            if cnt % 100 == 0:
                print(f"{cnt}")
            file_path = os.path.join(directory, file_name)
            embedding = np.load(file_path)
            if embedding.shape[0] != expected_embedding_dim:
                print(f"Skipping {file_name}: Expected dimension {expected_embedding_dim}, got {embedding.shape[0]}")
                continue
            
            try:
                with open(config.metadata_path(file_path), 'r') as file:
                    metadata = json.load(file)
            except:
                continue
            time_string = metadata["receivedDateTime"]
            time_format = '%Y-%m-%dT%H:%M:%SZ'
            given_time = datetime.strptime(time_string, time_format)
            age = (datetime.now() - given_time).total_seconds()

            embeddings_list.append(embedding)
            filenames.append(file_name)
            ages.append(age)

    embeddings = np.vstack(embeddings_list)
    if embeddings.shape[1] != expected_embedding_dim:
        print(f"error: Expected dimension {expected_embedding_dim}, got {embeddings.shape[1]}")
        raise ValueError

    return embeddings, filenames, ages  # Combine into a single NumPy array and include ages

def sort_by_age(embeddings, filenames, ages):
    sorted_indices = np.argsort(ages)
    sorted_embeddings = embeddings[sorted_indices]
    sorted_filenames = [filenames[i] for i in sorted_indices]
    return sorted_embeddings, sorted_filenames

# Directory containing the .npy embedding files
embeddings, filenames, ages = load_embeddings_from_directory(config.EMAILS_EMBEDDINGS_DIR, 384)

print(f"Loaded {len(embeddings)} embeddings with shape {embeddings.shape}")

sorted_embeddings, sorted_filenames = sort_by_age(embeddings, filenames, ages)

# calculate size for 3 months
max_short_age = 3 *31*24*3600
short_size=len(sorted_embeddings)
for idx in range(len(sorted_embeddings)):
    short_size=idx
    if ages[idx]>max_short_age:
        break
    
# Create a FAISS index
d = sorted_embeddings.shape[1]
nlist = 100  # Number of clusters
quantizer = faiss.IndexFlatL2(d)  # Quantizer
index = faiss.IndexIVFFlat(quantizer, d, nlist)

# Train the index
index.train(sorted_embeddings)

# Add embeddings to the index
index.add(sorted_embeddings)

print("FAISS index created and embeddings added")

# Save the index
faiss.write_index(index, config.EMAILS_INDEX_FILE)

# Create a recent FAISS index
d = sorted_embeddings.shape[1]
nlist = 100  # Number of clusters
quantizer = faiss.IndexFlatL2(d)  # Quantizer
index = faiss.IndexIVFFlat(quantizer, d, nlist)

# Train the index
index.train(sorted_embeddings)

# Add embeddings to the index
index.add(sorted_embeddings)

print("FAISS index created and embeddings added")

# Save the index
faiss.write_index(index, config.EMAILS_INDEX_FILE)


with open(config.EMAILS_MAPPING_FILE, 'w') as f:
    json.dump(sorted_filenames, f)
    
print(f"FAISS index saved to {config.EMAILS_INDEX_FILE}")

for i, fn in enumerate(sorted_filenames):
    src_file = os.path.join(config.EMAILS_EMBEDDINGS_DIR, fn)
    dest_file = os.path.join(config.EMAILS_INDEXED_EMBEDDINGS_DIR, f"{i}.npy")
    if i%100==0:
        print(i)
        
    # Copy the file to the new location with the new name
    shutil.copy(src_file, dest_file)
    
print(f"sorted embeddings saved")
