import requests
import json
import sys
import uuid
guid = uuid.uuid4()

def send_log_message(guid, title, message):
    url = 'http://localhost:8080/log'
    headers = {'Content-Type': 'application/json'}
    data = {'guid': str(guid), 'title':title, 'message': str(message)}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 204:
            print("Log message sent successfully.")
        else:
            pass
    except requests.exceptions.RequestException as e:
        pass


# URL of the API
url = "http://127.0.0.1:5001/search"

query_text = "faiss"
# Check if the query text was passed as a command line argument
if len(sys.argv) > 1:
    query_text = sys.argv[1]
send_log_message(guid, 'query', query_text)


# Request payload
payload = {
    "text": query_text,
    "after": "2024-05-01T12:00:00Z",
    "from": "joh",
    "take": 5
}

# Set headers
headers = {
    "Content-Type": "application/json"
}

# Make the request
response = requests.post(url, headers=headers, data=json.dumps(payload))
j = response.json()
for item in j:
    d = item["distance"]
    id = item["id"]
    email = item["email"]
    subj = email["subject"]
    frm = email["from"]
    print(f"{id}: {d}: {subj} {str(frm)}")
    pass

# Print the response
#print(response.json())

send_log_message(guid, 'response', response.json())

