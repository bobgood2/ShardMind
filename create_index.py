import os
import numpy as np
import faiss
import json
import datetime

def metadata_path(file_path):
    dirname = os.path.dirname(file_path)
    before_underscore = dirname.split('_')[0]
    filename_with_extension = os.path.basename(file_path)
    filename, _ = os.path.splitext(filename_with_extension)
    return os.path.join(f"{before_underscore}_metadata", f"{filename}.json")

def load_embeddings_from_directory(directory, expected_embedding_dim):
    embeddings_list = []
    filenames = []
    ages = []
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
            
            try:
                with open(metadata_path(file_path), 'r') as file:
                    metadata = json.load(file)
            except:
                continue
            time_string = metadata["receivedDateTime"]
            time_format = '%d/%m/%Y %H:%M:%S'
            given_time = datetime.strptime(time_string, time_format)
            age = (datetime.now() - given_time).total_seconds()

            embeddings_list.append(embedding)
            filenames.append(file_name)
            ages.append(age)

    embeddings = np.vstack(embeddings_list)
    if embeddings.shape[1] != expected_embedding_dim:
        print(f"error: Expected dimension {expected_embedding_dim}, got {embeddings.shape[1]}")
        raise ValueError

    return embeddings, filenames  # Combine into a single NumPy array

def sort_by_age(embeddings, filenames, ages):
    sorted_indices = np.argsort(ages)
    sorted_embeddings = embeddings[sorted_indices]
    sorted_filenames = [filenames[i] for i in sorted_indices]
    return sorted_embeddings, sorted_filenames

# Directory containing the .npy embedding files
embeddings_dir = r'C:\download\emails_embeddings'
embeddings, filenames = load_embeddings_from_directory(embeddings_dir, 384)

print(f"Loaded {len(embeddings)} embeddings with shape {embeddings.shape}")

sorted_embeddings, sorted_filenames = sort_by_age(embeddings, filenames, ages)

# Create a FAISS index
index = faiss.IndexFlatL2(sorted_embeddings.shape[1])  # Using L2 distance

# Add embeddings to the index
index.add(sorted_embeddings)

print("FAISS index created and embeddings added")

# Path to save the FAISS index
index_file_path = r'C:\download\email_index'
mapping_file_path = r'C:\download\email_index_mappings'

# Save the index
faiss.write_index(index, index_file_path)

with open(mapping_file_path, 'w') as f:
    json.dump(sorted_filenames, f)

print(f"FAISS index saved to {index_file_path}")