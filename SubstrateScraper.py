
import msal
import requests

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TENANT_ID = os.getenv('TENANT_ID')

# Ensure the variables are set
if not CLIENT_ID or not CLIENT_SECRET or not TENANT_ID:
    raise ValueError("Please set the CLIENT_ID, CLIENT_SECRET, and TENANT_ID environment variables.")

EMAIL_SCOPE = ['https://graph.microsoft.com/.default']

# MSAL Confidential Client Application
app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_credential=CLIENT_SECRET,
)

# Acquire a token
result = app.acquire_token_for_client(scopes=EMAIL_SCOPE)

if 'access_token' in result:
    access_token = result['access_token']
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Get emails from the inbox
    response = requests.get(
        'https://graph.microsoft.com/v1.0/me/messages',
        headers=headers
    )

    if response.status_code == 200:
        emails = response.json()['value']
        for email in emails:
            print("Subject:", email['subject'])
            print("Received:", email['receivedDateTime'])
            print("From:", email['from']['emailAddress']['address'])
            print("Body:", email['body']['content'])
            print("\n")
    else:
        print("Error:", response.status_code, response.text)
else:
    print("Error acquiring token:", result.get('error_description'))

