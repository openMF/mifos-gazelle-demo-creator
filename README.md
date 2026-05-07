# Mifos Gazelle Demo Creator (TUI)

> A terminal user interface (TUI) to author, manage, sync, and deploy demos for the Mifos Gazelle ecosystem.

- **Setup:** see [SETUP.md](./docs/SETUP.md)
- **User Guide:** see [USER_GUIDE.md](./docs/USER_GUIDE.md)
- **Architecture & repo layout:** see [ARCHITECTURE.md](./docs/ARCHITECTURE.md)

## Features

- Create demo files with steps, descriptions, and tags
- View, edit, and delete demos with versioned metadata
- Sync and publish demos locally using `just publish` or upload to Artifactory via JFrog
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
NOTE: run `source ~/.bashrc` command OR run `just` command in new terminal to avoid `bash: just: command not found error`

## Workflow

After setting up the project, follow these steps to create a demo and view it in Demo Runtime:

```bash
# Step 1 - Create a demo in the TUI
just run

# Step 2 - Sync your demo to mifos-gazelle-demo-runtime
just publish

# Step 3 - View your demo in Demo Runtime
# Navigate to mifos-gazelle-demo-runtime repo and run:
npm start
```

> Note: `just publish` requires mifos-gazelle-demo-runtime to be cloned.
> Set the path in `.env` file (see `.env.example`).

## Usage

- **Login:** enter username and email
- **Main Menu:** Create Demo, Upload Demo, Deploy DPG
- **Create Demo:** add steps (title, URL, details), tags, submit to save
- **Demo Details:** inspect/edit/delete demos
- **Publish:** run `just publish` to sync demos locally to demo-runtime, or use Upload Demo to push to JFrog
- **Deploy:** edit config, confirm, and watch logs

## Configuration

Edit `demo_creator/config.py` for:
- Gazelle repo settings and deploy command
- Log display/store limits

## Repository Structure

See [ARCHITECTURE.md](./ARCHITECTURE.md) for a detailed breakdown of modules, screens, and flows.

## License

Mozilla Public License 2.0 (MPL-2.0)