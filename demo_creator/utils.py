import requests
from requests.auth import HTTPBasicAuth
import re
import shutil
import glob
import os
import threading
import json
from datetime import datetime, timezone
from demo_creator.schema import metadata_schema
from jsonschema import validate, ValidationError


def threaded_delete_from_jfrog(
    username, password, repo_url, deleted_files, ui_callback=None, cancel_flag=None
):
    def _run():
        report = []
        overall_success = True
        for fname in deleted_files:
            if cancel_flag and cancel_flag():
                report.append(f"⏩ Cancelled by user.")
                overall_success = False
                break
            delete_url = repo_url.rstrip("/") + "/latest/" + fname
            try:
                # HEAD request to check if file exists before DELETE
                head_resp = requests.head(
                    delete_url, auth=HTTPBasicAuth(username, password), timeout=10
                )

                if head_resp.status_code == 404:
                    # File does not exist, skip DELETE and reporting
                    continue

                # File exists, proceed with DELETE
                response = requests.delete(
                    delete_url, auth=HTTPBasicAuth(username, password), timeout=10
                )
                print(f"DELETE {delete_url} -> {response.status_code}")  # DEBUG PRINT

                if response.status_code in (200, 202, 204):
                    msg = f"✅ {fname} deleted from remote."
                    report.append(msg)
                else:
                    msg = f"❌ Error deleting {fname}: {response.status_code} - {response.text.strip()} DELETE URL: {delete_url}"
                    report.append(msg)
                    overall_success = False
            except Exception as e:
                msg = f"❌ Exception deleting {fname}: {str(e)}"
                report.append(msg)
                overall_success = False
        status = "\n".join(report)
        if ui_callback:
            ui_callback(overall_success, status)

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def upload_to_jfrog(
    username: str,
    password: str,
    repo_url: str,
    folder: str = "demos/",
    progress_callback=None,
    cancel_flag=None,
) -> tuple[bool, str]:
    report = []
    overall_success = True

    # Read metadata for deleted files in 'latest' only, skip those from uploading
    metadata_path = os.path.join(folder, "latest", "metadata.json")
    deleted_files = []
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            deleted_files = [
                demo["file_name"]
                for demo in metadata.get("demos", [])
                if demo.get("deleted", False)
            ]
        except Exception as e:
            report.append(f"❌ Error reading metadata.json for deletions: {str(e)}")
            overall_success = False

    # Find all files in 'demos/' tree (subfolders included)
    files = [
        f
        for f in glob.glob(os.path.join(folder, "**"), recursive=True)
        if os.path.isfile(f)
    ]
    if not files:
        return False, f"❌ No files found in {folder}"

    for file_path in files:
        if cancel_flag and cancel_flag():
            report.append(f"⏩ Cancelled by user.")
            overall_success = False
            break

        # Build relative remote path (from demos/)
        rel_path = os.path.relpath(file_path, folder)

        # If it's in latest/ and is marked deleted, skip
        if (
            rel_path.startswith("latest/")
            and os.path.basename(rel_path) in deleted_files
        ):
            continue

        # Build remote URL: repo_url + "/" + rel_path (preserves timestamped folder structure)
        upload_url = repo_url.rstrip("/") + "/" + rel_path.replace("\\", "/")
        try:
            with open(file_path, "rb") as f:
                response = requests.put(
                    upload_url,
                    data=f,
                    auth=HTTPBasicAuth(username, password),
                    timeout=30,
                )
            if response.status_code in (200, 201):
                msg = f"✅ {rel_path}: OK"
                report.append(msg)
            else:
                msg = f"❌ {rel_path}: {response.status_code} - {response.text.strip()}"
                report.append(msg)
                overall_success = False
        except Exception as e:
            msg = f"❌ {rel_path}: Error - {e}"
            report.append(msg)
            overall_success = False

        if progress_callback:
            progress_callback(rel_path, response.status_code in (200, 201), msg)

    status = "\n".join(report)
    return overall_success, status


def threaded_upload_to_jfrog(
    username: str,
    password: str,
    repo_url: str,
    folder: str = "demos/",
    ui_callback=None,
    cancel_flag=None,
):
    def _run():
        success, status = upload_to_jfrog(
            username, password, repo_url, folder, cancel_flag=cancel_flag
        )
        if ui_callback:
            ui_callback(success, status)

    t = threading.Thread(target=_run, daemon=True)
    t.start()


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
    now_str = now.isoformat().replace("+00:00", "Z")
    demo_id = demo_data["demoId"]
    name = demo_data["name"] if "name" in demo_data else demo_data["demoName"]
    description = demo_data.get("demoDescription", "")
    steps_count = len(demo_data["steps"])

    entry = None
    for d in metadata["demos"]:
        if d["demoId"] == demo_id:
            entry = d
            break

    if entry:
        entry["name"] = name
        entry["file_name"] = file_name
        entry["description"] = description
        entry["steps_count"] = steps_count
        entry["updated_at"] = now_str
        entry["last_modified_by"] = username
        entry["deleted"] = False
        entry["version"] += 1
        entry["tags"] = demo_data.get("tags", [])
    else:
        entry = {
            "demoId": demo_id,
            "name": name,
            "file_name": file_name,
            "description": description,
            "version": 1,
            "steps_count": steps_count,
            "created_at": now_str,
            "updated_at": now_str,
            "created_by": username,
            "last_modified_by": username,
            "deleted": False,
            "tags": demo_data.get("tags", []),
        }
        metadata["demos"].append(entry)

    try:
        validate(instance=metadata, schema=metadata_schema)
    except ValidationError as ve:
        print(f"[red]❌ Metadata validation error: {ve}")
        raise

    save_metadata(metadata)
