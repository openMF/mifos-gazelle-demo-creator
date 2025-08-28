# Mifos Gazelle Demo Creator (TUI)

> A terminal user interface (TUI) to author, manage, sync, and deploy demos for the Mifos Gazelle ecosystem.

- **Setup:** see [SETUP.md](./docs/SETUP.md)
- **User Guide:** see [USER_GUIDE.md](./docs/USER_GUIDE.md)
- **Architecture & repo layout:** see [ARCHITECTURE.md](./docs/ARCHITECTURE.md)

## Features

- Create demo files with steps, descriptions, and tags
- View, edit, and delete demos with versioned metadata
- Sync deletions and upload demos to Artifactory
- Configure and deploy DPG environments with live logs using mifos-gazelle

## Quick Start

```
git clone https://github.com/openMF/mifos-gazelle-demo-creator.git
cd mifos-gazelle-demo-creator

# Install system tools (Python, uv, just) if missing
bash ./scripts/install_dependencies.sh

# Project setup
just setup

# Run the TUI app
just run
# or: .venv/bin/python main.py
```

## Usage

- **Login:** enter username and email
- **Main Menu:** Create Demo, Upload Demo, Deploy DPG
- **Create Demo:** add steps (title, URL, details), tags, submit to save
- **Demo Details:** inspect/edit/delete demos
- **Upload:** sync deletions and upload to JFrog
- **Deploy:** edit config, confirm, and watch logs

## Configuration

Edit `demo_creator/config.py` for:
- Gazelle repo settings and deploy command
- Log display/store limits

## Repository Structure

See [ARCHITECTURE.md](./ARCHITECTURE.md) for a detailed breakdown of modules, screens, and flows.

## License

Mozilla Public License 2.0 (MPL-2.0)