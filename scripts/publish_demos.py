#!/usr/bin/env python3
"""
Publish demos from demos/latest/ to mifos-gazelle-demo-runtime/public/examples/
Run with: just publish
"""
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from demo_creator.utils import load_metadata



def load_env():
    env_file = Path(__file__).parent.parent / ".env"
    env = {}
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip().strip("\x27\x22")
                    env[key.strip()] = value
    return env


def publish():
    env = load_env()
    runtime_path = env.get("DEMO_RUNTIME_PATH", "../mifos-gazelle-demo-runtime")

    base_dir = Path(__file__).parent.parent
    demos_dir = base_dir / "demos" / "latest"
    runtime_examples_dir = (base_dir / runtime_path / "public" / "examples").resolve()

    if not runtime_examples_dir.exists():
        print(f"Error: demo-runtime not found at {runtime_examples_dir}")
        print("Make sure DEMO_RUNTIME_PATH is set correctly in .env")
        return

    try:
        metadata = load_metadata()
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return

    active_demos = [d for d in metadata["demos"] if not d["deleted"]]

    if not active_demos:
        print("No active demos to publish")
        return

    published = []
    for demo in active_demos:
        src = demos_dir / demo["file_name"]
        dst = runtime_examples_dir / f"{demo['demoId']}.json"

        if src.exists():
            shutil.copy2(src, dst)
            published.append(demo)
            print(f"Published: {demo['name']}")
        else:
            print(f"File not found: {demo['file_name']}")

    runtime_metadata = {"demos": published}
    runtime_metadata_file = runtime_examples_dir / "metadata.json"
    with open(runtime_metadata_file, "w") as f:
        json.dump(runtime_metadata, f, indent=2)

    print(f"Updated metadata.json with {len(published)} demos")
    print("Done! Run npm run dev in mifos-gazelle-demo-runtime to see your demos.")


if __name__ == "__main__":
    publish()
