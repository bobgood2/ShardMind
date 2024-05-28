import os
import numpy as np
import faiss
import json
import shutil
from datetime import datetime

mapping_file_path = r'C:\download\email_index_mappings'
indexed_embeddings = r'C:\download\emails_indexed_embeddings'
embeddings = r'C:\download\emails_embeddings'

# read
with open(mapping_file_path, 'r') as file:
    sorted_filenames = json.load(file)

for i, fn in enumerate(sorted_filenames):
    src_file = os.path.join(embeddings, fn)
    dest_file = os.path.join(indexed_embeddings, f"{i}.npy")
    if i%100==0:
        print(i)
        
    # Copy the file to the new location with the new name
    shutil.copy(src_file, dest_file)
