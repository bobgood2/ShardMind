import os
import requests
import json
from datetime import datetime

import subprocess
import os
import jwt

def get_token():
    TOKEN_FILE = 'access_token.txt'
    def get_access_token():
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                token = f.readlines()
                return token[0]
        return None


    # Use the access token in your script
    access_token = get_access_token()
    if access_token:
        #token_bytes = access_token.encode('utf-8')
        #decoded_token = jwt.decode(token_bytes, options={"verify_signature": False})
        #
        #print(decoded_token)
        print(f"Access Token: {access_token}")
        # Use the access token as needed
    else:
        print("No access token available.")
    return access_token
  
def GetFolder(pfi):
    access_token=get_token()

    # Define the Microsoft Graph endpoint to fetch emails
    endpoint = f"https://graph.microsoft.com/v1.0/me/mailFolders/{pfi}"

    # Define headers for the HTTP request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(endpoint, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        folder_metadata = response.json()
        return folder_metadata['displayName']
        print("Folder Metadata:", folder_metadata)
    else:
        # Print the error if the request failed
        print(f"Error: {response.status_code}")
        print(response.json())
        raise ValueError


EMAIL_FOLDERS_FILE = 'C:\download\emails_folders.json'
def write_folders():
    with open(EMAIL_FOLDERS_FILE, 'w') as f:
        json.dump(folders, f)
        
with open(EMAIL_FOLDERS_FILE, 'r') as file:
    folders = json.load(file)

#write_folders()

def scan_directory_for_json_files(directory):
    for file in os.listdir(directory):
        if file.endswith('.json'):
            yield os.path.join(directory, file)
            
def read_json_files(directory):
    for file_path in scan_directory_for_json_files(directory):
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            yield (file_path, json_data)


emails_dir = 'C:\download\emails'

parentfolders = set([])

num=0;
smallest_age=10000
for (path, email) in read_json_files(emails_dir):
    if 'parentFolderId' in email:
        num+=1
        if num%100==0:
            print(f"{num} {len(parentfolders)} {smallest_age} {last_age}")
        pfi = email['parentFolderId']
        if pfi not in folders:
            folders[pfi]=GetFolder(pfi)
            write_folders()
        parentfolders.add(pfi)
        time_string = email["receivedDateTime"]
        time_format = '%Y-%m-%dT%H:%M:%SZ'
        given_time = datetime.strptime(time_string, time_format)
        age = (datetime.now() - given_time).total_seconds()
        last_age = age/3600/24/365 
        if last_age<smallest_age:
            smallest_age=last_age


