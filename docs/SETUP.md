# Setup

> This guide walks through installing prerequisites, setting up the environment, and running the TUI.


## Prerequisites

- **Python 3.8+**  
- **Git** (recommended for version control, pulls, and deployments)  
- A terminal supporting **Textual** (Linux and macOS recommended)  
- On Windows: use **Git Bash** or **WSL** for a smoother Unix-like experience  


## One-Command Bootstrap

From the project root:

```
bash ./scripts/install_dependencies.sh
```

This script:
- Verifies **Python** and **pip**
- Installs **uv** (fast Python package manager)
- Installs **just** (command runner)
- Updates **PATH** for `just` on Unix-based shells

If you encounter “permission denied,” run:

```
chmod +x ./scripts/install_dependencies.sh
bash ./scripts/install_dependencies.sh
```

## Project Setup

Using `just`:

```
# Create virtual environment and install dependencies
just setup

# Run the TUI
just run

# or: .venv/bin/python main.py
```


## Manual Setup (alternative)

```
# Create venv
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies with uv (if installed)
uv pip install -e .

# Or with pip
python -m pip install -e . (If editable install is not desired: python -m pip install .)

# Run
python main.py
```

## Configuration

Configuration lives in [`demo_creator/config.py`](./demo_creator/config.py).  

### Deployment/Gazelle
- `GAZELLE_ARTIFACTS_DIR`  
- `GAZELLE_REPO_DIR`  
- `INI_OUTPUT_FILENAME`  
- `GAZELLE_GIT_URL`  
- `GAZELLE_BRANCH_NAME`  
- `GAZELLE_DEPLOY_CMD_TMPL` (includes `{ini_path}` placeholder)  

### Logs
- `LOG_DISPLAY_LIMIT`  
- `LOG_STORE_LIMIT`  

> Note: No secrets are stored in the codebase.  
> JFrog credentials are entered at runtime via the **Upload screen**. 

## Running

```
just run
```
or
```
.venv/bin/python main.py
```

## Common Tasks

```
just setup     # create venv + install deps
just run       # run the TUI
just clean     # clean virtualenv and all cache
just format    just format # Format the code (requires dev dependencies)
just lint      # Lint the code (requires dev dependencies)
```

## Troubleshooting

- Script permission denied:
  - `chmod +x ./scripts/install_dependencies.sh`
- Styles not applying:
  - Confirm `CSS_PATH` in each screen matches file paths in `demo_creator/assets/`
- Duplicate ID error (Textual):
  - Avoid reusing widget IDs in dynamic forms, rely on classes when possible
- Windows issues:
  - Prefer Git Bash or WSL, ensure PowerShell installs for uv/just completed
- Deploy failures:
  - Verify `GAZELLE_GIT_URL` and `GAZELLE_BRANCH_NAME` in `config.py`
  - Ensure `git` is installed and network access is available