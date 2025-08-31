import requests
import uuid
import json
from datetime import datetime, timedelta
import traceback
import sys

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
APP_REGISTRATION_AUTOMATION_CLIENT_SECRET = config["APP_REGISTRATION_AUTOMATION_CLIENT_SECRET"]

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


# -----------------------------
# MAIN CODE
ACCESS_TOKEN = generate_access_token_for_app_registration_automation(
    MSENTRA_DEFAULT_TENANT_ID,
    APP_REGISTRATION_AUTOMATION_CLIENT_ID,
    APP_REGISTRATION_AUTOMATION_CLIENT_SECRET)
print("ACCESS_TOKEN", ACCESS_TOKEN)

sys.exit(0)  # Added for just validating access token generation

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
GRAPH_URL = "https://graph.microsoft.com/v1.0"
# -----------------------------

# -----------------------------
# 1. CREATE BACKEND API APP
# -----------------------------
api_read_id = str(uuid.uuid4())
api_write_id = str(uuid.uuid4())
admin_role_id = str(uuid.uuid4())
user_role_id = str(uuid.uuid4())

print("api_read_id", api_read_id)
print("api_write_id", api_write_id)
print("admin_role_id", admin_role_id)
print("user_role_id", user_role_id)

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

try:
    print(f"Backend Payload: {backend_payload}")
    backend_app = create_application(backend_payload)
    backend_sp = create_service_principal(backend_app["appId"])
    print(f"Backend API created: {BACKEND_API_NAME}")

    backend_secret = create_client_secret(
        backend_app["id"], "BackendAPISecret")
    print("Backend client secret created. Value:",
          backend_secret["secretText"])

    # -----------------------------
    # 2. CREATE REACT SPA APP
    # -----------------------------
    spa_payload = {
        "displayName": SPA_APP_NAME,
        "signInAudience": "AzureADMyOrg",
        "web": {
            "redirectUris": SPA_REDIRECT_URIS
        },
        "requiredResourceAccess": [
            {
                "resourceAppId": backend_app["appId"],
                "resourceAccess": [
                    {"id": api_read_id, "type": "Scope"},
                    {"id": api_write_id, "type": "Scope"}
                ]
            }
        ]
    }

    print(f"SPA Payload: {spa_payload}")
    spa_app = create_application(spa_payload)
    spa_sp = create_service_principal(spa_app["appId"])
    print(f"SPA App created: {SPA_APP_NAME}")

    spa_secret = create_client_secret(spa_app["id"], "SPASecret")
    print("SPA client secret created. Value:", spa_secret["secretText"])

    # -----------------------------
    # 3. ASSIGN ADMIN ROLE TO MULTIPLE USERS
    # -----------------------------
    for user_email in USERS_TO_ASSIGN:
        try:
            user_id = get_user_object_id(user_email)
            assign_app_role(backend_sp["id"], user_id, admin_role_id)
            print(f"Assigned Admin role to {user_email}")
        except Exception as e:
            print(f"Error assigning role to {user_email}: {e}")
except Exception as e:
    print(f"Error executing main code", e)
