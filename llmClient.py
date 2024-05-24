import argparse
from msal import PublicClientApplication, SerializableTokenCache
import json
import os
import atexit
import requests

class LLMClient:

    _ENDPOINT = 'https://fe-26.qas.bing.net/sdf/'
    _SCOPES = ['api://68df66a4-cad9-4bfd-872b-c6ddde00d6b2/access']
    _API = 'chat/completions'

    def __init__(self, endpoint):
        self._cache = SerializableTokenCache()
        atexit.register(lambda: 
            open('.llmapi.bin', 'w').write(self._cache.serialize())
            if self._cache.has_state_changed else None)

        self._app = PublicClientApplication('68df66a4-cad9-4bfd-872b-c6ddde00d6b2', authority='https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47', token_cache=self._cache)
        if os.path.exists('.llmapi.bin'):
            self._cache.deserialize(open('.llmapi.bin', 'r').read())
        if endpoint != None:
            LLMClient._ENDPOINT = endpoint
        LLMClient._ENDPOINT += self._API

    def send_request(self, model_name, request):
        # get the token
        token = self._get_token()

        # populate the headers
        headers = {
            'Content-Type':'application/json', 
            'Authorization': 'Bearer ' + token, 
            'X-ModelType': model_name }

        body = str.encode(json.dumps(request))
        response = requests.post(LLMClient._ENDPOINT, data=body, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}. Response: {response.text}")
        return response.json()

    def _get_token(self):
        accounts = self._app.get_accounts()
        result = None

        if accounts:
            # Assuming the end user chose this one
            chosen = accounts[0]

            # Now let's try to find a token in cache for this account
            result = self._app.acquire_token_silent(LLMClient._SCOPES, account=chosen)

    
        if not result:
            # So no suitable token exists in cache. Let's get a new one from AAD.
            flow = self._app.initiate_device_flow(scopes=LLMClient._SCOPES)

            if "user_code" not in flow:
                raise ValueError(
                    "Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))

            print(flow["message"])

            result = self._app.acquire_token_by_device_flow(flow)

        return result["access_token"]

parser = argparse.ArgumentParser(description='Async API Example')
parser.add_argument('--endpoint', type=str, help='Endpoint URL')
parser.add_argument('--scenario', type=str, help='Scenario ID')

args = parser.parse_args()

endpoint = args.endpoint
scenario_id = args.scenario


llm_client = LLMClient(endpoint)
request_data = {
  "messages":[
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ],
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 800
}

request_data_json_mode = {
  "messages":[
    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ],
  "response_format":{ "type": "json_object" },
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 800
}

request_data_reproducible_output = {
  "messages":[
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ],
  "seed":42, # parameter that makes the output reproducible
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 800
}

request_data_parallel_function_calling = {
    "messages": [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ],
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 800
}

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

response = llm_client.send_request('dev-gpt-4-turbo-chat-completions', request_data)
print(response)

response = llm_client.send_request('dev-gpt-4-turbo-chat-completions', request_data_json_mode)
print(response)

response = llm_client.send_request('dev-gpt-4-turbo-chat-completions', request_data_reproducible_output)
print(response)

response = llm_client.send_request('dev-gpt-4-turbo-chat-completions', request_data_parallel_function_calling)
print(response)




