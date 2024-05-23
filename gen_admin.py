import os
import urllib.parse

# Ensure environment variables are set
CLIENT_ID = os.getenv('CLIENT_ID')
TENANT_ID = os.getenv('TENANT_ID')
REDIRECT_URI = 'http://localhost:8000/getAToken'  # Replace with your redirect URI
SCOPE = (
    'User.Read Calendars.Read Calendars.Read.Shared Channel.ReadBasic.All '
    'Chat.Read ChatMessage.Read Contacts.Read Contacts.Read.Shared '
    'Files.Read Files.Read.All Mail.Read Notes.Read Notes.Read.All '
    'OnlineMeetingArtifact.Read.All OnlineMeetings.Read People.Read '
    'Sites.Read.All Tasks.Read Tasks.Read.Shared TeamsActivity.Read'
)

if not CLIENT_ID or not TENANT_ID or not REDIRECT_URI:
    raise ValueError("Ensure CLIENT_ID, TENANT_ID, and REDIRECT_URI are set as environment variables")

# Construct the admin consent URL
admin_consent_url = (
    f"https://login.microsoftonline.com/{TENANT_ID}/adminconsent?"
    f"client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&scope={urllib.parse.quote(SCOPE)}"
)

print("Share this URL with an admin to grant permissions:")
print(admin_consent_url)
