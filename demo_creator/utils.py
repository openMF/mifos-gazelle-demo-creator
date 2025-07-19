import requests
from requests.auth import HTTPBasicAuth
import re
import shutil
import glob
import os
import json
from datetime import datetime, timezone
from demo_creator.schema import metadata_schema
from jsonschema import validate, ValidationError

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

def get_demo_file_name(demo_name: str) -> str:
    safe_name = demo_name.strip().lower()
    safe_name = re.sub(r"\s+", "_", safe_name)
    safe_name = re.sub(r"[^a-z0-9_]", "", safe_name)
    return safe_name + ".json"

def snapshot_latest_to_dated(date_str, time_str, latest_dir="demos/latest"):
    dated_dir = os.path.join("demos", date_str, time_str)
    os.makedirs(dated_dir, exist_ok=True)
    for src_path in glob.glob(os.path.join(latest_dir, "*.json")):
        dest_path = os.path.join(dated_dir, os.path.basename(src_path))
        shutil.copy(src_path, dest_path)

METADATA_FILE = "demos/latest/metadata.json"

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"demos": []}

def save_metadata(metadata):
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)

def update_metadata(demo_data, file_name, username):
    metadata = load_metadata()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    now_str = now.isoformat().replace("+00:00", "Z")    # CORRECT FORMAT FOR ALL FIELDS
    demo_id = demo_data["demoId"]
    name = demo_data["demoName"]
    description = demo_data.get("demoDescription", "")
    steps_count = len(demo_data["steps"])   

    # Try to find by demoId, else new
    entry = None
    for d in metadata["demos"]:
        if d["demoId"] == demo_id:
            entry = d
            break

    if entry:
        # Update fields
        entry["name"] = name
        entry["file_name"] = file_name
        entry["description"] = description
        entry["steps_count"] = steps_count
        entry["updated_at"] = now_str      # USE THE STRING
        entry["last_modified_by"] = username
        entry["deleted"] = False
        entry["version"] += 1
    else:
        entry = {
            "demoId": demo_id,  # Store demoId in metadata as well!
            "name": name,
            "file_name": file_name,
            "description": description,
            "version": 1,
            "steps_count": steps_count,
            "created_at": now_str,          # USE THE STRING
            "updated_at": now_str,          # USE THE STRING
            "created_by": username,
            "last_modified_by": username,
            "deleted": False,
            "tags": []
        }
        metadata["demos"].append(entry)

    # 🚩 Validate the metadata dict before saving
    try:
        validate(instance=metadata, schema=metadata_schema)
    except ValidationError as ve:
        print(f"[red]❌ Metadata validation error: {ve}")
        raise       # Optionally: handle more gracefully in production

    save_metadata(metadata)
