import re
import json
import os
from sentence_transformers import SentenceTransformer
import numpy as np

# Preprocess text
def preprocess_text(text):
    return re.sub(r'\W+', ' ', text).lower()

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')


def scan_directory_for_json_files(directory):
    for file in os.listdir(directory):
        if file.endswith('.json'):
            yield os.path.join(directory, file)
            
def get_filename_only(file_path):
    filename_with_extension = os.path.basename(file_path)
    filename, _ = os.path.splitext(filename_with_extension)
    return filename

def embeddings_path(file_path):
    dirname = os.path.dirname(file_path)
    filename_with_extension = os.path.basename(file_path)
    filename, _ = os.path.splitext(filename_with_extension)
    return os.path.join(f"{dirname}_embeddings", f"{filename}.npy")

def metadata_path(file_path):
    dirname = os.path.dirname(file_path)
    filename_with_extension = os.path.basename(file_path)
    filename, _ = os.path.splitext(filename_with_extension)
    return os.path.join(f"{dirname}_metadata", f"{filename}.json")
    
def write_metadata(email, path):
    email_metadata = {
        'receivedDateTime': email.get('receivedDateTime'),
        'subject': email.get('subject'),
        'sender': email.get('sender', {}).get('emailAddress', {}).get('address')
    }
    with open(metadata_path(path), 'w') as f:
        json.dump(email_metadata, f)

def read_json_files(directory):
    for file_path in scan_directory_for_json_files(directory):
        if not os.path.exists(metadata_path(file_path)) or not os.path.exists(embeddings_path(file_path)):
            print (file_path)
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                write_metadata(json_data, file_path)
                yield (file_path, json_data)
            
def get_weighted_embedding(email, weights):
    subject_embedding = model.encode([preprocess_text(email.get("subject", ""))])[0] * weights['subject']
    sender_embedding = model.encode([preprocess_text(email.get("sender", {}).get("emailAddress", {}).get("address", ""))])[0] * weights['sender']
    body_preview_embedding = model.encode([preprocess_text(email.get("bodyPreview", ""))])[0] * weights['bodyPreview']
    body_content_embedding = model.encode([preprocess_text(email.get("body", {}).get("content", ""))])[0] * weights['bodyContent']
    
    combined_embedding = (
        subject_embedding + sender_embedding + body_preview_embedding + body_content_embedding
    ) / sum(weights.values())
    return combined_embedding

def preprocess_emails_from_directory(directory):
    for (path, email) in read_json_files(directory):
        yield (path, get_weighted_embedding(email, weights))

weights = {
    'subject': 3,
    'sender': 2,
    'bodyPreview': 2,
    'bodyContent': 1
}
emails_dir = 'C:\download\emails'

for (path, embedding) in preprocess_emails_from_directory(emails_dir):
    epath = embeddings_path(path)
    np.save(epath, embedding)
    
