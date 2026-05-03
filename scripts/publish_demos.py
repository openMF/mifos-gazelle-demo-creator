#!/usr/bin/env python3
"""
Publish demos from demos/latest/ to mifos-gazelle-demo-runtime/public/examples/
Run with: just publish
"""
import json
import shutil
from pathlib import Path


def load_env():
    env_file = Path(__file__).parent.parent / ".env"
    env = {}
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()
    return env


def publish():
    env = load_env()
    runtime_path = env.get("DEMO_RUNTIME_PATH", "../mifos-gazelle-demo-runtime")

    base_dir = Path(__file__).parent.parent
    demos_dir = base_dir / "demos" / "latest"
    metadata_file = demos_dir / "metadata.json"
    runtime_examples_dir = (base_dir / runtime_path / "public" / "examples").resolve()

    if not runtime_examples_dir.exists():
        print(f"Error: demo-runtime not found at {runtime_examples_dir}")
        print("Make sure DEMO_RUNTIME_PATH is set correctly in .env")
        return

    if not metadata_file.exists():
        print("Error: No demos found. Create a demo first using just run")
        return

    with open(metadata_file) as f:
        metadata = json.load(f)

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
