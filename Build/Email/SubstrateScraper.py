import os
import requests
import json

import subprocess
import os
import jwt

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
  

# Define the Microsoft Graph endpoint to fetch emails
endpoint = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages"

# Define headers for the HTTP request
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Function to get the next link from the checkpoint file
def get_next_link(checkpoint_file):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            return f.read().strip()
    return None

# Function to save the next link to the checkpoint file
def save_next_link(checkpoint_file, next_link):
    with open(checkpoint_file, 'w') as f:
        f.write(next_link)

wcnt=0
last_t = None
# Function to save an email to a file
def save_email(email, directory):
    global wcnt, last_t
    email_id = email['id']
    file_path = os.path.join(directory, f"{email_id}.json")
    with open(file_path, 'w') as f:
        last_t = email["receivedDateTime"]
        json.dump(email, f, indent=4)
        wcnt+=1

# Function to get all emails incrementally
def get_emails_incrementally(endpoint, headers, checkpoint_file, directory):
    next_link = get_next_link(checkpoint_file) or endpoint
    while next_link:
        response = requests.get(next_link, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for email in data.get('value', []):
                save_email(email, directory)
            next_link = data.get('@odata.nextLink', None)  # Get the next page link
            if next_link:
                save_next_link(checkpoint_file, next_link)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break

# Directory to save emails and checkpoint file
email_directory = r'c:\download\emails'
checkpoint_file = r'c:\download\emails\checkpoint.txt'

checkpoint_file = 'checkpoint.txt'

# Create the directory if it doesn't exist
if not os.path.exists(email_directory):
    os.makedirs(email_directory)

# Fetch emails incrementally
get_emails_incrementally(endpoint, headers, checkpoint_file, email_directory)

print(f"Emails have been saved to the '{email_directory}' directory.")
print(f"{wcnt} files written")
print(f"{last_t} last time")
