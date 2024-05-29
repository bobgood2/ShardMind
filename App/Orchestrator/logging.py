import requests
import json
import sys
import uuid
import threading
from datetime import datetime, timedelta

def nowstamp():
    now = datetime.now()
    return now.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z' 

def thenstamp(then):
    return then.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z'  

def time_add(then, n):
    return then + timedelta(seconds=n)

def send_log_message(data):
    url = 'http://localhost:8080/log'
    headers = {'Content-Type': 'application/json'}
    print(data)

    def send_request():
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 204:
                pass
            else:
                print(f"response_code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"exception {e}")

    # Run the request in a separate thread
    thread = threading.Thread(target=send_request)
    thread.start()
    
#logging.send_log_message({
#     'guid': guid,
#     'title': "user query",
#     'timestamp': logging.thenstamp(t1),
#     'duration': 0,
#     'query': "the quick brown fox",
#     })
# m1 = {
#     'guid': guid,
#     'title': "user query",
#     'timestamp': thenstamp(t1),
#     'duration': 0,
#     'query': "the quick brown fox",
#     }
# m2 = {
#     'guid': guid,
#     'title': "search_email",
#     'timestamp': thenstamp(t2),
#     'duration': 1.15,
#     'search': {'text': 'the quick brown fox', 
#                 'after':nowstamp()},
#     'result': [{'email':{}, 'distance':9.8}]           
#     }
# 
# m3 = {
#     'guid': guid,
#     'title': "LLM",
#     'timestamp': thenstamp(t3),
#     'duration': 1.8,
#     'prompt': "prompt here",
#     'output': 'search_email(text=)'
# }
# 
# send_log_message(m1)
# send_log_message(m2)
# send_log_message(m3)
# 