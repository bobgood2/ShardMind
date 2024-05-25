import requests
import json
import sys

# URL of the API
url = "http://127.0.0.1:5001/search"

# Check if the query text was passed as a command line argument
if len(sys.argv) > 1:
    query_text = sys.argv[1]
else:
    query_text = input("Enter your query string: ")

# Request payload
payload = {
    "text": query_text,
    "k": 5
}

# Set headers
headers = {
    "Content-Type": "application/json"
}

# Make the request
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Print the response
print(response.json())
