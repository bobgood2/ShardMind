import json
import os
from sentence_transformers import SentenceTransformer
import faiss

posting_list_dir = 'C:\download\email_posting_lists'

who_data = {}
who_ref_list = {}
fcnt=0
for file_path in os.listdir(posting_list_dir):
    if file_path.endswith('.json'):
        fcnt+=1
        if fcnt%100==0:
            print(fcnt)
        with open(os.path.join(posting_list_dir, file_path), 'r') as file:
            json_data = json.load(file)
            token = json_data["token"]
            pcnt = len(json_data["posting_list"])
            if len(token)==3:
                who = (token[1], token[2])
                if len(who[0]) > 2 and who[0][0] == '.' and who[0][1] == ' ':
                    who = (who[0][2:], who[1])
                if who not in who_data:
                    who_data[who]=0
                    who_ref_list[who]=[]
                who_data[who]+=pcnt 
                who_ref_list[who].append((token[0],pcnt))

who_list = [(key[0], key[1], value, who_ref_list[key]) for key, value in who_data.items()]
         
email_who_file = 'C:\download\email_who.json'
with open(email_who_file, 'w') as f:
    json.dump(who_list, f)

# 128 dim model:    
model = SentenceTransformer('paraphrase-MiniLM-L12-v2')
# Initialize the SentenceTransformer model (384 dimensions)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Combine name and email for embedding
texts = [f"{entry[0]} {entry[1]}" for entry in who_list]

# Generate embeddings for each entry
embeddings = model.encode(texts, convert_to_tensor=True).cpu().numpy()

# Create a FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save the FAISS index and the data
index_file_path = 'c:\download\email_who_index.faiss'

faiss.write_index(index, index_file_path)
print(f"FAISS index saved to {index_file_path}")

