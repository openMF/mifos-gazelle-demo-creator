import requests
from requests.auth import HTTPBasicAuth

def upload_to_jfrog(username: str, password: str, url: str, filepath: str = "demos/demo_output.json") -> tuple[bool, str]:
    try:
        with open(filepath, "rb") as f:
            response = requests.put(
                url,
                data=f,
                auth=HTTPBasicAuth(username, password),
                timeout=10
            )
        if response.status_code in (200, 201):
            return True, "✅ Upload successful!"
        else:
            return False, f"❌ Upload failed: {response.status_code} - {response.text.strip()}"
    except Exception as e:
        return False, f"❌ Error: {e}"
