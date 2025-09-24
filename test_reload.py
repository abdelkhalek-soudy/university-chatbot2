import requests
import json

# Test the reload knowledge API
url = "http://127.0.0.1:5000/api/reload-knowledge"
headers = {
    "Content-Type": "application/json"
}
data = {
    "path": "C:/Users/pc/Downloads/Badya _ Memphis  bank (1).xlsx",
    "KNOWLEDGE_MAX_CHARS": 50000
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
