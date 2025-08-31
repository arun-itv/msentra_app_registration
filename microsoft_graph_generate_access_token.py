import requests

# Tenant ID for MS Entra Default Directory reacharuninstant@gmail.com
TENANT_ID = "205aee12-1059-4628-90b8-86a3bce373c5"
# Register an app AppRegistrationAutomation in the MS Entra Default Tenant and use its client ID
CLIENT_ID = "a08031ee-9c7e-4a8a-a132-a96f23669aef"
CLIENT_SECRET = "b5S8Q~kR5hYIGIVtU1HR.kBFPVeCRoCBUYeRRaMo"

token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
data = {
    "client_id": CLIENT_ID,
    "scope": "https://graph.microsoft.com/.default",
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials"
}

# disables SSL verification)
response = requests.post(token_url, data=data, verify=False)
response.raise_for_status()
access_token = response.json()["access_token"]

print("Access token:", access_token[:40] + "...")  # just preview
