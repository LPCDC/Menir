# scripts/fetch_status.py
import requests
import base64
import json

TOKEN = "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"  # Your PAT
REPO = "LPCDC/Menir"
BRANCH = "release/menir-aio-v5.0-boot-local"
FILE = "status/status_update.json"

url = f"https://api.github.com/repos/{REPO}/contents/{FILE}?ref={BRANCH}"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "LPCDC-Menir"
}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"FETCH_ERROR {response.status_code} {response.json().get('message', 'Unknown')}")
else:
    content = base64.b64decode(response.json()["content"]).decode("utf-8")
    print(content)