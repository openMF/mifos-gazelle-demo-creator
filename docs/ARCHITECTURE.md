# Architecture & Repository Structure

This document explains the app’s structure, key modules, flows, and how to extend or modify features.

## High-Level Overview

The application is a Textual-based TUI with multiple screens:
- Login
- Main menu
- Demo creator (form to create demos)
- Demo details (view/edit/delete created demos)
- Upload form (sync deletions + upload to JFrog)
- Deploy DPG (configure and trigger deployment)
- Deploy logs (stream live logs, cancel/cleanup)

State like current user/email is stored in the App until runtime, demo data is persisted as JSON files and tracked in metadata.

## Repository Layout

```
mifos-gazelle-demo-creator/
│
├── demo_creator/
│   ├── __init__.py
│   ├── app.py                    # Initializes the Textual app, screen routing
│   ├── schema.py                 # JSON schema for demo data; DPG_DEFAULT_CONFIG
│   ├── utils.py                  # IO helpers: filenames, metadata load/save, snapshots, JFrog threads
│   ├── config.py                 # Centralized environment-sensitive variables
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── login_screen.py
│   │   ├── main_menu_screen.py
│   │   ├── demo_creator_screen.py
│   │   ├── demo_detail_screen.py
│   │   ├── upload_form_screen.py
│   │   ├── deploy_dpg_screen.py
│   │   ├── deploy_logs_screen.py
│   │   └── confirm_dialog_screen.py
│   └── assets/                   # TCSS styles per screen
│       ├── base.tcss
│       ├── confirm_dialog.tcss
│       ├── demo_creator.tcss
│       ├── demo_detail.tcss
│       ├── deploy_dpg.tcss
│       ├── deploy_logs.tcss
│       ├── login_form.tcss
│       ├── main_menu.tcss
│       └── upload_form.tcss
│
├── scripts/
│   └── install_dependencies.sh   # Installs Python tooling (uv, just) if missing
│   
├── Justfile                      # Common tasks: setup, run
├── main.py                       # Entry point; constructs and runs the app
├── pyproject.toml                
├── README.md
├── SETUP.md
├── ARCHITECTURE.md
└── LICENSE
```

## Data Model and Storage

- Per-demo JSON file saved under `demos/latest/`
- `metadata.json` keeps an index of demos: ID, name, description, tags, counts, timestamps, versions, deleted flag
- Snapshots: On create/edit, a dated snapshot is taken for traceability (`YYYY-MM-DD/HH-MM-SS/`)

Key JSON fields (per demo):
- `demoId` (UUID)
- `demoName`
- `steps` (indexed dict: "1", "2", ...)
- `tags` (list of strings)
- Optional: `demoDescription`

## Configuration (demo_creator/config.py)

- Deployment:
  - `GAZELLE_ARTIFACTS_DIR`, `GAZELLE_REPO_DIR`, `INI_OUTPUT_FILENAME`
  - `GAZELLE_GIT_URL`, `GAZELLE_BRANCH_NAME`, `GAZELLE_DEPLOY_CMD_TMPL`
- Logs:
  - `LOG_DISPLAY_LIMIT`, `LOG_STORE_LIMIT`

Only environment/directory/command settings live here, UI text remains in code.

## Screens (Responsibilities)

- **login_screen.py**
  - Minimal form for username/email; sets `app.current_user` and `app.current_email`
  - Takes to main menu after validation

- **main_menu_screen.py**
  - Shows user info and actions: Create, Upload, Deploy
  - Lists demos in a DataTable, sorted by updated time from `metadata.json`
  - On row select, opens DemoDetailScreen

- **demo_creator_screen.py**
  - Multi-step form to build a demo (name, description, tags, steps)
  - Validates against `schema` then writes a JSON file to `demos/latest/`
  - Updates metadata and triggers a dated snapshot

- **demo_detail_screen.py**
  - Displays demo data and steps
  - Edit mode allows editing the demo file
  - Save validates JSON, updates file/metadata, snapshots
  - Delete removes the file and marks metadata as deleted

- **upload_form_screen.py**
  - Inputs: JFrog username, API key/password, repo URL
  - Two-phase: sync deletions, then upload current demos
  - Uses threaded functions from utils with UI callbacks/cancel

- **deploy_dpg_screen.py**
  - Loads existing INI (if present) or generate default from `DPG_DEFAULT_CONFIG` in `schema.py`
  - View/edit config; Save writes INI to `INI_OUTPUT_FILENAME`
  - Deploy asks for confirmation and pushes DeployLogsScreen

- **deploy_logs_screen.py**
  - Ensures artifact and repo directories exist
  - Clones/pulls Gazelle repo, then executes deploy command
  - Streams live logs, supports cancel via SIGINT and cleanup

- **confirm_dialog_screen.py**
  - Reusable Yes/No dialog with confirm/cancel callbacks

## Utilities (demo_creator/utils.py)

Common helper functions (representative examples):
- `get_demo_file_name(demo_name)`: slugifies to a stable filename
- `update_metadata(...)` / `load_metadata()` / `save_metadata(...)`: manage `metadata.json`
- `snapshot_latest_to_dated(date_str, time_str, latest_dir)`: copy snapshot for versioning
- `threaded_upload_to_jfrog(...)` / `threaded_delete_from_jfrog(...)`: background IO with cancel flags and UI callbacks

## Schema (demo_creator/schema.py)

- JSON schema for demo validation (`validate(instance, schema)`)
- `DPG_DEFAULT_CONFIG`: default sections/keys for deployment INI generation

## Entry Points

- `main.py`: Entrypoint invoking the app (may import and run `demo_creator/app.py`)
- `app.py`: Creates the Textual App, registers initial screens, and sets CSS or theme defaults (depending on your organization)

## Data Flows

- **Create Demo** → Form → Schema validate → Save JSON → Update `metadata.json` → Snapshot  
- **Edit Demo** → Load file → Update & validate → Save → Update metadata → Snapshot  
- **Upload** → Sync deletions remotely → Upload active demos → Report combined status  
- **Deploy** → Edit/Save INI → Clone/Pull → Run command → Stream logs → Allow cancel/cleanup  

## Styling

Each screen has its own TCSS to avoid selector collisions:
- Use unique IDs for static elements that are referenced in code
- Prefer classes for dynamic/repeated widgets
- Keep color variables consistent across assets for a unified theme

## Extending the App

- **Add a new screen** → Place in `screens/` with matching TCSS under `assets/`, register it in navigation.  
- **Add a configuration value** → Define in `config.py`, reference in screens/utilities.  
- **Extend schema or metadata** → Update definitions in `schema.py` and corresponding logic in `utils.py` and UI.  
- **Contrib tasks** → New workflows/scripts can be added into `Justfile` for consistency.  
