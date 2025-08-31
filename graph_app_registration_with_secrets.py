import requests
import uuid
import json
from datetime import datetime, timedelta
import traceback
import sys
import urllib3
import time
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# -----------------------------
# CONFIGURATION
# -----------------------------
ENVIRONMENT = "local"  # local / dev / test / prod
# Load environment config
with open("app_config.json") as f:
    config = json.load(f)
env_config = config["environments"][ENVIRONMENT]
print("env_config", env_config)

USERS_TO_ASSIGN = env_config["users_to_assign"]
SPA_REDIRECT_URIS = env_config["spa_redirect_uris"]

BACKEND_API_NAME = config["backend_api_name"]
SPA_APP_NAME = config["spa_app_name"]

SECRET_EXPIRY_DAYS = config.get("secret_expiry_days", 365)

MSENTRA_DEFAULT_TENANT_ID = config["MSENTRA_DEFAULT_TENANT_ID"]
APP_REGISTRATION_AUTOMATION_CLIENT_ID = config["APP_REGISTRATION_AUTOMATION_CLIENT_ID"]
APP_REGISTRATION_AUTOMATION_CLIENT_SECRET = os.environ.get(
    "APP_REGISTRATION_AUTOMATION_CLIENT_SECRET")

print("MSENTRA_DEFAULT_TENANT_ID", MSENTRA_DEFAULT_TENANT_ID)
print("APP_REGISTRATION_AUTOMATION_CLIENT_ID",
      APP_REGISTRATION_AUTOMATION_CLIENT_ID)
print("APP_REGISTRATION_AUTOMATION_CLIENT_SECRET",
      APP_REGISTRATION_AUTOMATION_CLIENT_SECRET)

print("USERS_TO_ASSIGN", USERS_TO_ASSIGN)
print("SPA_REDIRECT_URIS", SPA_REDIRECT_URIS)

print("SPA_APP_NAME", SPA_APP_NAME)
print("BACKEND_API_NAME", BACKEND_API_NAME)
print("SECRET_EXPIRY_DAYS", SECRET_EXPIRY_DAYS)

APP_REGISTRATION_AUTOMATION_CLIENT_ID = config["APP_REGISTRATION_AUTOMATION_CLIENT_ID"]

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------


def generate_access_token_for_app_registration_automation(MSENTRA_DEFAULT_TENANT_ID,
                                                          APP_REGISTRATION_AUTOMATION_CLIENT_ID,
                                                          APP_REGISTRATION_AUTOMATION_CLIENT_SECRET):
    try:
        token_url = f"https://login.microsoftonline.com/{MSENTRA_DEFAULT_TENANT_ID}/oauth2/v2.0/token"
        data = {
            "client_id": APP_REGISTRATION_AUTOMATION_CLIENT_ID,
            "scope": "https://graph.microsoft.com/.default",
            "client_secret": APP_REGISTRATION_AUTOMATION_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }

        # disables SSL verification)
        response = requests.post(token_url, data=data, verify=False)
        response.raise_for_status()
        access_token = response.json()["access_token"]

        return access_token
    except Exception as e:
        print(f"Error while generating Access Token for Microsoft Graph API calls", e)
        # traceback.print_exc()


def create_application(payload):
    try:
        response = requests.post(
            # disables SSL verification)
            f"{GRAPH_URL}/applications", headers=HEADERS, json=payload, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error executing Creating Application", e)
        # traceback.print_exc()


def create_service_principal(app_id):
    try:
        payload = {"appId": app_id}
        response = requests.post(
            # disables SSL verification
            f"{GRAPH_URL}/servicePrincipals", headers=HEADERS, json=payload, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error while creating Service Principal", e)


def get_user_object_id(user_principal_name):
    try:
        response = requests.get(
            # disables SSL verification)
            f"{GRAPH_URL}/users/{user_principal_name}", headers=HEADERS, verify=False)
        response.raise_for_status()
        return response.json()["id"]
    except Exception as e:
        print(f"Error while getting User Object", e)


def assign_app_role(sp_id, principal_id, app_role_id):
    try:
        payload = {
            "principalId": principal_id,
            "resourceId": sp_id,
            "appRoleId": app_role_id
        }
        response = requests.post(f"{GRAPH_URL}/servicePrincipals/{sp_id}/appRoleAssignments",
                                 headers=HEADERS, json=payload, verify=False)  # disables SSL verification)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error while Assigning App Roles", e)


def create_client_secret(app_id, display_name="auto-generated"):
    try:
        expiry_date = (datetime.utcnow() +
                       timedelta(days=SECRET_EXPIRY_DAYS)).isoformat() + "Z"
        payload = {
            "displayName": display_name,
            "endDateTime": expiry_date
        }
        response = requests.post(
            # disables SSL verification)
            f"{GRAPH_URL}/applications/{app_id}/addPassword", headers=HEADERS, json=payload, verify=False)
        response.raise_for_status()
        return response.json()  # returns secret value and id
    except Exception as e:
        print(f"Error while creating Client Secret", e)


def delete_app(app_id):
    try:
        response = requests.delete(
            f"{GRAPH_URL}/applications/{app_id}", headers=HEADERS, verify=False)
        if response.status_code in [204, 200]:
            print(f"Deleted application {app_id}")
        else:
            print(f"Failed to delete application {app_id}: {response.text}")
    except Exception as e:
        print(f"Error deleting application {app_id}: {e}")


def delete_service_principal(sp_id):
    try:
        response = requests.delete(
            f"{GRAPH_URL}/servicePrincipals/{sp_id}", headers=HEADERS, verify=False)
        if response.status_code in [204, 200]:
            print(f"Deleted service principal {sp_id}")
        else:
            print(
                f"Failed to delete service principal {sp_id}: {response.text}")
    except Exception as e:
        print(f"Error deleting service principal {sp_id}: {e}")


def remove_app_role_assignments(sp_id):
    try:
        # Get all app role assignments for the SP
        response = requests.get(
            f"{GRAPH_URL}/servicePrincipals/{sp_id}/appRoleAssignments", headers=HEADERS, verify=False)
        response.raise_for_status()
        assignments = response.json().get("value", [])
        for assign in assignments:
            assign_id = assign["id"]
            resp = requests.delete(
                f"{GRAPH_URL}/servicePrincipals/{sp_id}/appRoleAssignments/{assign_id}", headers=HEADERS, verify=False)
            if resp.status_code in [204, 200]:
                print(f"Removed app role assignment {assign_id} from {sp_id}")
    except Exception as e:
        print(f"Error removing app role assignments from {sp_id}: {e}")


def cleanup_backend_and_spa():
    print("Cleaning up resources...")
    remove_app_role_assignments(BACKEND_SP_ID)
    delete_service_principal(BACKEND_SP_ID)
    delete_service_principal(SPA_SP_ID)
    delete_app(BACKEND_ID)
    delete_app(SPA_ID)
    print("Cleanup completed.")


# -----------------------------
# MAIN EXECUTION
# -----------------------------
# Step 0: Generate access token
ACCESS_TOKEN = generate_access_token_for_app_registration_automation(
    MSENTRA_DEFAULT_TENANT_ID,
    APP_REGISTRATION_AUTOMATION_CLIENT_ID,
    APP_REGISTRATION_AUTOMATION_CLIENT_SECRET
)

if not ACCESS_TOKEN:
    print("Failed to generate access token. Exiting.")
    sys.exit(1)

print("ACCESS_TOKEN generated successfully")

# Initialize headers and Graph URL
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
GRAPH_URL = "https://graph.microsoft.com/v1.0"

# Step 1: Create Backend API App
api_read_id = str(uuid.uuid4())
api_write_id = str(uuid.uuid4())
admin_role_id = str(uuid.uuid4())
user_role_id = str(uuid.uuid4())

backend_payload = {
    "displayName": BACKEND_API_NAME,
    "signInAudience": "AzureADMyOrg",
    "api": {
        "requestedAccessTokenVersion": 2,
        "oauth2PermissionScopes": [
            {
                "id": api_read_id,
                "adminConsentDisplayName": "Read access",
                "adminConsentDescription": "Allows reading data",
                "userConsentDisplayName": "Read access",
                "userConsentDescription": "Allows reading data",
                "value": "API.Read",
                "type": "User",
                "isEnabled": True
            },
            {
                "id": api_write_id,
                "adminConsentDisplayName": "Write access",
                "adminConsentDescription": "Allows writing data",
                "userConsentDisplayName": "Write access",
                "userConsentDescription": "Allows writing data",
                "value": "API.Write",
                "type": "User",
                "isEnabled": True
            }
        ]
    },
    "appRoles": [
        {
            "id": admin_role_id,
            "allowedMemberTypes": ["User"],
            "description": "Admin role for API",
            "displayName": "Admin",
            "isEnabled": True,
            "value": "Admin"
        },
        {
            "id": user_role_id,
            "allowedMemberTypes": ["User"],
            "description": "User role for API",
            "displayName": "User",
            "isEnabled": True,
            "value": "User"
        }
    ]
}

backend_app = create_application(backend_payload)
print("backend_app--->", backend_app)
if not backend_app:
    print("Failed to create backend application. Exiting.")
    sys.exit(1)
BACKEND_APP_ID = backend_app.get("appId")
BACKEND_ID = backend_app.get("id")

print("BACKEND_APP_ID--->", BACKEND_APP_ID)
backend_sp = create_service_principal(BACKEND_APP_ID)
print("backend_sp--->", backend_sp)
if not backend_sp:
    print("Failed to create backend service principal. Exiting.")
    sys.exit(1)
print("backend_sp", backend_sp)
BACKEND_SP_ID = backend_sp.get("id")
print("BACKEND_SP_ID--->", BACKEND_SP_ID)

backend_secret = create_client_secret(
    backend_app.get("id"), "BackendAPISecret")
if not backend_secret:
    print("Failed to create backend client secret. Exiting.")
    sys.exit(1)

print(f"Backend API '{BACKEND_API_NAME}' created successfully")
print("Backend client secret:", backend_secret.get("secretText"))

# Step 2: Create SPA App
spa_payload = {
    "displayName": SPA_APP_NAME,
    "signInAudience": "AzureADMyOrg",
    "web": {
        "redirectUris": SPA_REDIRECT_URIS
    },
    "requiredResourceAccess": [
        {
            "resourceAppId": BACKEND_APP_ID,
            "resourceAccess": [
                {"id": api_read_id, "type": "Scope"},
                {"id": api_write_id, "type": "Scope"}
            ]
        }
    ]
}

spa_app = create_application(spa_payload)
if not spa_app:
    print("Failed to create SPA application. Exiting.")
    sys.exit(1)
SPA_APP_ID = spa_app.get("appId")
SPA_ID = spa_app.get("id")

spa_sp = create_service_principal(SPA_APP_ID)
if not spa_sp:
    print("Failed to create SPA service principal. Exiting.")
    sys.exit(1)
SPA_SP_ID = spa_sp.get("id")

spa_secret = create_client_secret(spa_app.get("id"), "SPASecret")
if not spa_secret:
    print("Failed to create SPA client secret. Exiting.")
    sys.exit(1)

print(f"SPA App '{SPA_APP_NAME}' created successfully")
print("SPA client secret:", spa_secret.get("secretText"))

# Step 3: Assign Admin Role to Users
for user_email in USERS_TO_ASSIGN:
    user_id = get_user_object_id(user_email)
    if not user_id:
        print(f"Failed to get object ID for user {user_email}. Skipping.")
        continue

    result = assign_app_role(backend_sp.get("id"), user_id, admin_role_id)
    if not result:
        print(f"Failed to assign admin role to {user_email}.")
    else:
        print(f"Assigned Admin role to {user_email}")

# Call at the end
# time.sleep(20)
# cleanup_backend_and_spa()
