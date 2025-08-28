# User Guide

> This guide provides step-by-step instructions for the main workflows in the Mifos Gazelle Demo Creator TUI.

---

## Create demo

Prerequisites:
- Logged in (username and email entered on the Login screen).

Steps:
1) From Main Menu, select “Create Demo”.
2) Fill fields:
   - **Demo Name:** Short identifier shown in lists
   - **Demo Description:** One or two sentences describing the demo
   - **Required DPGs:** Comma-separated DPG names to categorize (currently demo runtime supports **mifosx, phee and vnext**)
   - **Steps:** Add one or more steps. Each step supports
     - **Title:** Short heading
     - **URL:** Link associated with the step
     - **Details:** Demo instructions
3) Submit to save. The app validates and writes a JSON file under demos/latest/ and updates metadata.

Result:
- New demo appears in the Main Menu list, with timestamps and version set in metadata.

---

## Edit demo

Steps:
1) From **Main Menu**, select a demo row to open **“Demo Details”**.
2) Click **Edit** to modify name, description, tags, or steps.
3) Save to validate, write JSON, and snapshot for version history.

Result:
- Changes are persisted; a dated snapshot is created for traceability.

---

## Delete demo

Steps:
1) Open **“Demo Details”** for the target demo.
2) Choose Delete and confirm.
3) The file is removed locally and metadata marks it as deleted.

Result:
- The demo is removed from `demos/latest`, deletion will be synchronized during Upload.

---

## Upload demo

Purpose:
- Synchronize local deletions and upload current demos to the remote repository (e.g., JFrog Artifactory).

Steps:
1) From Main Menu, select **“Upload Demo”**.
2) Enter credentials (username and API key/password) and repository URL.
3) Start upload:
   - Phase 1: Sync remote deletions based on metadata
   - Phase 2: Upload all the demos

Result:
- Status is displayed for each operation. Credentials are not stored; inputs are taken at runtime.

---

## Deploy DPG

Purpose:
- Configure and run Mifos Gazelle deployments with live logs.

Steps:
1) From Main Menu, choose **“Deploy DPG”**.
2) Review configuration sections. To change values, click **Edit**, modify fields, and **Save** to write the INI.
   - If no INI exists yet, the app will materialize defaults on first Deploy.
3) Click Deploy and confirm. The app ensures the repo is cloned/pulled, then runs the deploy command with the selected INI.

Notes:
- If privileged commands are required, ensure **sudo credentials** are cached in the terminal (e.g., run `sudo -v` before launching the TUI).
- Logs stream live; Cancel attempts a graceful stop.
- Since both deployment and TUI runs in same terminal, it can hang the terminal.

Result:
- Deploy progress is shown; on completion, the status indicates success or failure. Artifacts and repo are kept locally for subsequent runs.

---

## Troubleshooting


- **“TUI breaks on sudo run for the mifos-gazelle script”** Remember to run the script under terminal's sudo session, but refrain from running demo creator as sudo.

- **“Permission denied editing files after deploy”** Avoid launching the entire TUI with sudo. If any deploy steps are elevated, normalize ownership post-run for repo, artifacts, and the INI.

- **“Upload fails authentication”** Re-enter credentials on the Upload screen; credentials are not persisted.

