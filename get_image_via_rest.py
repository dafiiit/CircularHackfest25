import requests
from requests.auth import HTTPBasicAuth

# Replace with your camera's IP and credentials
camera_ip = "192.168.136.100"
username = "Service"
password = "1234"

# REST API snapshot URL (adjust if needed)
snapshot_url = f"http://{camera_ip}/api/snapshot"

# Make the POST request to trigger a snapshot
response = requests.post(snapshot_url, auth=HTTPBasicAuth(username, password))

if response.status_code == 200:
    print("Snapshot triggered successfully.")
    # The response may contain JSON info about the snapshot or direct image data.
    # If JSON with image URL or base64, handle accordingly.
    # For now, let's print the JSON response:
    print(response.json())
else:
    print(f"Failed to trigger snapshot. Status code: {response.status_code}")
    print(response.text)
