from flask import Flask, request, redirect
import requests
import os

app = Flask(__name__)

# Retrieve environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TENANT_ID = os.getenv('TENANT_ID')
REDIRECT_URI = 'http://localhost:8000/getAToken'

if not CLIENT_ID or not CLIENT_SECRET or not TENANT_ID:
    raise ValueError("Ensure CLIENT_ID, CLIENT_SECRET, and TENANT_ID are set as environment variables - ask bob to give you a batch file")

@app.route('/')
def home():
    return 'Welcome! Go to /login to authenticate.'

@app.route('/login')
def login():
    authorization_url = (
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?"
        f"client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
        f"&response_mode=query&scope=User.Read Calendars.Read Files.Read.All&state=12345"
    )
    return redirect(authorization_url)

@app.route('/getAToken')
def get_a_token():
    code = request.args.get('code')
    if not code:
        return 'Authorization code not found. Please try logging in again.', 400

    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    token_response_json = token_response.json()

    if 'access_token' in token_response_json:
        access_token = token_response_json['access_token']
        return f"Access token acquired: {access_token}"
    else:
        return f"Failed to acquire access token: {token_response_json}"

if __name__ == '__main__':
    app.run(port=8000)
