import sys
import os
sys.path.append(os.getcwd())
import numpy as np
import faiss
import json
import shutil
from datetime import datetime
from Config import config

# read
with open(config.EMAILS_MAPPING_FILE, 'r') as file:
    sorted_filenames = json.load(file)

for i, fn in enumerate(sorted_filenames):
    src_file = os.path.join(config.EMAILS_EMBEDDINGS_DIR, fn)
    dest_file = os.path.join(config.EMAILS_INDEXED_EMBEDDINGS_DIR, f"{i}.npy")
    if i%100==0:
        print(i)
        
    # Copy the file to the new location with the new name
    shutil.copy(src_file, dest_file)
