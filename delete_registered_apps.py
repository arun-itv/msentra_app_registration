import requests
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJub25jZSI6IjRqbll5dndfQ1lCQ2VtOTN5a2I0LTlMT0xXbm16aktwVkhZNnZwY2MySUUiLCJhbGciOiJSUzI1NiIsIng1dCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSIsImtpZCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20vIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvMjA1YWVlMTItMTA1OS00NjI4LTkwYjgtODZhM2JjZTM3M2M1LyIsImlhdCI6MTc1NjYxMjk4OSwibmJmIjoxNzU2NjEyOTg5LCJleHAiOjE3NTY2MTgzMTYsImFjY3QiOjAsImFjciI6IjEiLCJhY3JzIjpbInAxIl0sImFpbyI6IkFaUUFhLzhaQUFBQTBtS21hK3lLaGl4eE1JWXhCbjZJZUdjODI0Ri9mLzduMjdhVDg1aGJ6SEJ5Q3hYWFBGM3BtVWtaME9manorMm5XTk9XSVRJN3pJS3F1Nmt3L1lZYm9kdDlIRnNXKzh6djdKTzJmRG55UDN0RWdpbm9ZRFcxQk9hOWxULzlmcmNJQThCU2xHL3c5TXliZ3Ryb3JyaDJSajE0RHo2S1lFMTFwNG4vQmFNTHJsL0ZCVVRYbThyMXZ6d0VrQ24wbGdFLyIsImFsdHNlY2lkIjoiMTpsaXZlLmNvbTowMDAzNDAwMUQ3RjMwMEQ2IiwiYW1yIjpbInB3ZCIsIm1mYSJdLCJhcHBfZGlzcGxheW5hbWUiOiJBenVyZVBvcnRhbCBDb25zb2xlIEFwcCIsImFwcGlkIjoiYjY3N2MyOTAtY2Y0Yi00YThlLWE2MGUtOTFiYTY1MGE0YWJlIiwiYXBwaWRhY3IiOiIwIiwiZW1haWwiOiJyZWFjaGFydW5pbnN0YW50QGdtYWlsLmNvbSIsImZhbWlseV9uYW1lIjoiVmVudWdvcGFsIiwiZ2l2ZW5fbmFtZSI6IkFydW4iLCJpZHAiOiJsaXZlLmNvbSIsImlkdHlwIjoidXNlciIsImlwYWRkciI6IjEyNC4xNTMuMTIyLjIzIiwibmFtZSI6IkFydW4gVmVudWdvcGFsIiwib2lkIjoiZjE2NGRkYzktYzZlOC00MWI1LWE2MDktNTM1YjNhODliODhjIiwicGxhdGYiOiIzIiwicHVpZCI6IjEwMDMyMDA0ODQ1OEE4QUYiLCJyaCI6IjEuQWNZQUV1NWFJRmtRS0VhUXVJYWp2T056eFFNQUFBQUFBQUFBd0FBQUFBQUFBQURwQUQ3R0FBLiIsInNjcCI6IkF1ZGl0TG9nLlJlYWQuQWxsIERpcmVjdG9yeS5SZWFkV3JpdGUuQWxsIGVtYWlsIEdyb3VwLlJlYWRXcml0ZS5BbGwgSWRlbnRpdHlQcm92aWRlci5SZWFkV3JpdGUuQWxsIG9wZW5pZCBwcm9maWxlIFVzZXIuSW52aXRlLkFsbCIsInNpZCI6IjAwN2VhZGM5LWRlOTktOWEyNy0zYzI2LTQzY2NkNjJiYTNlZSIsInNpZ25pbl9zdGF0ZSI6WyJrbXNpIl0sInN1YiI6IlpNd1JZdUVZM2VBOHN5d1lpVkNwNGFZMTFjM0k0ZGh0WkNVbF8wWDdXUm8iLCJ0ZW5hbnRfcmVnaW9uX3Njb3BlIjoiQVMiLCJ0aWQiOiIyMDVhZWUxMi0xMDU5LTQ2MjgtOTBiOC04NmEzYmNlMzczYzUiLCJ1bmlxdWVfbmFtZSI6ImxpdmUuY29tI3JlYWNoYXJ1bmluc3RhbnRAZ21haWwuY29tIiwidXRpIjoicU9mVS0xdzNxMEdEZlVXNjZYWExBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiNjJlOTAzOTQtNjlmNS00MjM3LTkxOTAtMDEyMTc3MTQ1ZTEwIiwiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il0sInhtc19mdGQiOiIwVjFXeU9yMU5pTjFid2NRMkVJckJPM1Zld01qc2w4Nkd6RmxEdFJMOEFFQmFtRndZVzVsWVhOMExXUnpiWE0iLCJ4bXNfaWRyZWwiOiIxIDE0IiwieG1zX3N0Ijp7InN1YiI6Ilk4dVBVZm9zejdEMEc1XzZaNGxkUGIzUmV6ZFViY3haSmhDaFpyYkEtMVEifSwieG1zX3RjZHQiOjE3NDQ3NzY0ODh9.RXqVtkcESyB0TZnz-dNSVvqWQqyhzwURVzT5MfsWOavAGVGzx2SNk2N6wjLDRg4LzOFSdmWNid9My24k66BM9XBHsCY7Dq30c1lDZeon9Mg9U4dKnSy83UsMBvbovY_vAI6xMVzm6WFI76SYoWX-Luhqx-9Iw_wNUffmX7r1_-UZ-c6o4QFSOQ2RaVupfpQg_VzH8VPom9kx8wLboSa7Qn5TvtQShCm9k4vQcTI6G_pX1DeY6HatCXlmoNH0TCyAXzZeE0j_kNtgj9OfZrQXSkPM_5D2zU5_pdWY38RenZWSOBTVsm9y-IIU0nSr1DdahzjcfzGvpI4YBwdkp7gwtA"
ENVIRONMENT = "local"  # local / dev / test / prod
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
GRAPH_URL = "https://graph.microsoft.com/v1.0"

# Load environment config
with open("app_config.json") as f:
    config = json.load(f)
env_config = config["environments"][ENVIRONMENT]

BACKEND_API_NAME = config["backend_api_name"]
SPA_APP_NAME = config["spa_app_name"]

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------


def get_app_by_name(display_name):
    """Fetch applications matching displayName"""
    url = f"{GRAPH_URL}/applications?$filter=displayName eq '{display_name}'"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    apps = response.json().get("value", [])
    return apps[0] if apps else None


def get_service_principal(app_id):
    """Fetch service principal for a given appId"""
    url = f"{GRAPH_URL}/servicePrincipals?$filter=appId eq '{app_id}'"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    sps = response.json().get("value", [])
    return sps[0] if sps else None


def delete_service_principal(sp_id):
    """Delete service principal"""
    url = f"{GRAPH_URL}/servicePrincipals/{sp_id}"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code in [204, 404]:
        print(f"Service Principal {sp_id} deleted or not found")
    else:
        print(f"Error deleting SP {sp_id}: {response.text}")


def delete_application(app_id):
    """Delete application"""
    url = f"{GRAPH_URL}/applications/{app_id}"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code in [204, 404]:
        print(f"Application {app_id} deleted or not found")
    else:
        print(f"Error deleting app {app_id}: {response.text}")


# -----------------------------
# DELETE BACKEND API APP
# -----------------------------
backend_app = get_app_by_name(BACKEND_API_NAME)
if backend_app:
    backend_sp = get_service_principal(backend_app["appId"])
    if backend_sp:
        delete_service_principal(backend_sp["id"])
    delete_application(backend_app["id"])
else:
    print(f"No backend app found with name {BACKEND_API_NAME}")

# -----------------------------
# DELETE SPA APP
# -----------------------------
spa_app = get_app_by_name(SPA_APP_NAME)
if spa_app:
    spa_sp = get_service_principal(spa_app["appId"])
    if spa_sp:
        delete_service_principal(spa_sp["id"])
    delete_application(spa_app["id"])
else:
    print(f"No SPA app found with name {SPA_APP_NAME}")

print("All configured apps deleted successfully.")
