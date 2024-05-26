import re
import json
import os
from sentence_transformers import SentenceTransformer
import numpy as np

from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import numpy as np

# Function to strip HTML tags
def strip_html(html_content):
    # Parse HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Get text
    text = soup.get_text()

    # Clean up text by removing leading/trailing whitespace and unnecessary newlines
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
    return cleaned_text

#   "hasAttachments": false,
#    "subject": "Shared Platform Weekly Update: 6/13",
#    "parentFolderId": "AAMkAGNjYjZlNmUxLWIzNGYtNDc3Ni04YTI3LTcwODFjOGZkMzkwMAAuAAAAAABxT_rxjLfGQoiJhM1u-etjAQBlLqkxdm26QJmVjZdJ5nCIAAAAfGyrAAA=",
#    "conversationId": "AAQkAGNjYjZlNmUxLWIzNGYtNDc3Ni04YTI3LTcwODFjOGZkMzkwMAAQAFgG4_rWu0QckykR_H0gOjI=",
#    "conversationIndex": "AdHFund2WAbj6ta7RByTKRH4fSA6MgAADKhA",
#    "isRead": false,
#    "isDraft": false,
#    "inferenceClassification": "focused",
#    "sender": {  dont use sender
#        "emailAddress": {
#            "name": "David Ku",
#            "address": "davidku@microsoft.com"
#        }
#    },
#    "from": {
#        "emailAddress": {
#            "name": "David Ku",
#            "address": "davidku@microsoft.com"
#        }
#    },
#    "toRecipients": [
#        {
#            "emailAddress": {
#                "name": "ASG Shared Platform FTE's",
#                "address": "ASGSPALL@microsoft.com"
#            }
#        }
#    ],
#    "ccRecipients": [
#        {
#            "emailAddress": {
#                "name": "IPG LT",
#                "address": "IPGLT@microsoft.com"
#            }
#        }
#    ],
#    "bccRecipients": [],
#    "replyTo": [],
#    "isRead": false,
#    "isDraft": false,
#    "inferenceClassification": "focused",
#    "flag": {
#        "flagStatus": "notFlagged"
 

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

def get_name_addr(item):
    who=item["emailAddress"]
    name = who["name"]
    addr=''
    if "address" in who:
        addr = who["address"]
    return name, addr
        
def write_metadata(email, path):
    email_metadata = {
        'receivedDateTime': email.get('receivedDateTime'),
        'subject': email.get('subject'),
        'sender': email.get('sender', {}).get('emailAddress', {}).get('address'),
        'from':  get_name_addr(email.get('from', {})),
        'toRecipients': [get_name_addr(item) for item in email.get('toRecipients', {})],
        'ccRecipients': [get_name_addr(item) for item in email.get('ccRecipients', {})],
        'bccRecipients': [get_name_addr(item) for item in email.get('bccRecipients', {})],
        'replyTo': [get_name_addr(item) for item in email.get('replyTo', {})],
        'isRead': email.get('isRead', {}),
        'isDraft': email.get('isDraft"', {}),
        'hasAttachments': email.get('hasAttachments', {})
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
    body_content_embedding = model.encode([preprocess_text(strip_html(email.get("body", {}).get("content", "")))])[0] * weights['bodyContent']
    
    combined_embedding = (
        subject_embedding + sender_embedding + body_preview_embedding + body_content_embedding
    ) / sum(weights.values())
    return combined_embedding

def preprocess_emails_from_directory(directory):
    for (path, email) in read_json_files(directory):
        try:
            emb=get_weighted_embedding(email, weights)
            yield (path, emb )
        except Exception as e:
            print (f"error in {emb}")

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
    
