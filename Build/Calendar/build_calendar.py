import sys
import os
sys.path.append(os.getcwd())
import re
import json
from Config import config
from sentence_transformers import SentenceTransformer
import numpy as np
import traceback

from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import numpy as np

# Build depends on scraper output.
# it creates embeddings and metaata

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

 

# Preprocess text
def preprocess_text(text):
    try:
        return re.sub(r'\W+', ' ', text).lower()
    except:
        return ""
    
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


def get_name_addr(item):
    who=item["emailAddress"]
    name = who["name"]
    addr=''
    if "address" in who:
        addr = who["address"]
    return name, addr
        

def read_json_files():
    for file_path in scan_directory_for_json_files(config.CALENDAR_RAW_DIR):
        if not os.path.exists(embeddings_path(file_path)):
            print (file_path)
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                yield (file_path, json_data)
            
def get_weighted_embedding(meeting, weights):
    subject_embedding = model.encode([preprocess_text(meeting.get("Subject", ""))])[0] * weights['Subject']
    body_content = json.loads(meeting.get("Body","{}")).get("Content","")
    
    body_content_embedding = model.encode([preprocess_text(strip_html(body_content))])[0] * weights['Body']
    
    combined_embedding = (
        subject_embedding + body_content_embedding
    ) / sum(weights.values())
    return combined_embedding

def preprocess_meetings_from_directory():
    for (path, email) in read_json_files():
        try:
            emb=get_weighted_embedding(email, weights)
            yield (path, emb )
        except Exception as e:
            stack_trace = traceback.format_exc()
            print (f"error in {e} {stack_trace}")

weights = {
    'Subject': 1,
    'Body': 1,
}

def embeddings_path(file_path):
    return config.change_dir_and_ext(file_path,config.CALENDAR_EMBEDDINGS_DIR, '.npy') 


for (path, embedding) in preprocess_meetings_from_directory():
    epath = embeddings_path(path)
    np.save(epath, embedding)
    
