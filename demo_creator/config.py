import os

# === deploy_dpg_screen.py ===
GAZELLE_ARTIFACTS_DIR = os.path.abspath("gazelle_artifacts")
GAZELLE_REPO_DIR = os.path.join(GAZELLE_ARTIFACTS_DIR, "mifos-gazelle")
INI_OUTPUT_FILENAME = os.path.join(GAZELLE_ARTIFACTS_DIR, "mifos-gazelle-config.ini")
GAZELLE_GIT_URL = "https://github.com/openMF/mifos-gazelle.git"
GAZELLE_BRANCH_NAME = "dev"
GAZELLE_DEPLOY_CMD_TMPL = ["sudo", "./run.sh", "-f", "{ini_path}"]

# === deploy_logs_screen.py ===
LOG_DISPLAY_LIMIT = 100
LOG_STORE_LIMIT = 200
