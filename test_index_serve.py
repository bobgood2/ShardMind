import requests
import json
import sys

def send_log_message(message):
    url = 'http://localhost:8080/log'
    headers = {'Content-Type': 'application/json'}
    data = {'message': str(message)}

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

# Check if the query text was passed as a command line argument
if len(sys.argv) > 1:
    query_text = sys.argv[1]
else:
    query_text = input("Enter your query string: ")

send_log_message(query_text)


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

send_log_message(response.json())

