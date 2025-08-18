import os
import subprocess
from textual.screen import Screen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Input, Button, Footer
from textual.app import ComposeResult
from demo_creator.screens.ConfirmDialogScreen import ConfirmDialogScreen
from demo_creator.schema import DPG_DEFAULT_CONFIG
from demo_creator.screens.DeployLogsScreen import DeployLogsScreen

# =========================
# Artifact folder setup
# =========================
GAZELLE_ARTIFACTS_DIR = os.path.abspath("gazelle_artifacts")
GAZELLE_REPO_DIR = os.path.join(GAZELLE_ARTIFACTS_DIR, "mifos-gazelle")
INI_OUTPUT_FILENAME = os.path.join(GAZELLE_ARTIFACTS_DIR, "mifos-gazelle-config.ini")

GAZELLE_GIT_URL = "https://github.com/yashsharma127/mifos-gazelle.git"
GAZELLE_BRANCH_NAME = "gsoc/yash-dev"
GAZELLE_DEPLOY_CMD_TMPL = ["sudo", "./run.sh", "-f", "{ini_path}"]

def ini_text(config: dict) -> str:
    lines = []
    for section, params in config.items():
        lines.append(f'[{section}]')
        for k, v in params.items():
            lines.append(f'{k} = {v}')
        lines.append('')
    return "\n".join(lines)

class DeployDPGScreen(Screen):
    CSS_PATH = "../assets/deploy_dpg.tcss"

    def __init__(self):
        super().__init__()
        self.config = {section: dict(params) for section, params in DPG_DEFAULT_CONFIG.items()}
        self.edit_mode = False
        self.inputs = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="deploy_dpg_container"):
            yield Static("Deploy DPGs", id="deploy_dpg_title")
            with Horizontal(id="top_buttons_row"):
                yield Button("Edit", id="edit_btn")
                yield Button("Deploy", id="deploy_btn", disabled=False)
                yield Button("Cancel", id="cancel_btn", disabled=True)
            yield Static("", id="status_label")
            yield ScrollableContainer(id="deploy_config_scroll")
            yield Footer()

    def on_mount(self) -> None:
        self.render_view()

    def render_view(self):
        self.edit_mode = False
        self.query_one("#edit_btn", Button).disabled = False
        self.query_one("#deploy_btn", Button).disabled = False
        self.query_one("#cancel_btn", Button).disabled = True

        scroll = self.query_one("#deploy_config_scroll", ScrollableContainer)
        scroll.remove_children()

        for section, params in self.config.items():
            scroll.mount(Static(f"{section}", classes="section_header"))
            for key, val in params.items():
                row = Horizontal(
                    Static(f"{key}:", classes="label"),
                    Static(str(val), classes="ini_value"),
                    classes="ini_row"
                )
                scroll.mount(row)
        scroll.refresh()

    def render_edit(self):
        self.edit_mode = True
        self.query_one("#edit_btn", Button).disabled = True
        self.query_one("#deploy_btn", Button).disabled = False
        self.query_one("#cancel_btn", Button).disabled = False

        scroll = self.query_one("#deploy_config_scroll", ScrollableContainer)
        scroll.remove_children()
        self.inputs = {}

        for section, params in self.config.items():
            scroll.mount(Static(f"{section}", classes="section_header"))
            self.inputs[section] = {}
            for key, val in params.items():
                inp = Input(value=str(val), classes="ini_input")
                self.inputs[section][key] = inp
                row = Horizontal(
                    Static(f"{key}:", classes="label"),
                    inp,
                    classes="ini_row"
                )
                scroll.mount(row)
        scroll.refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "edit_btn":
            self.render_edit()
            self.query_one("#status_label", Static).update("")
        elif btn_id == "deploy_btn":
            if self.edit_mode:
                self.save_edits()
            self.ask_deploy_confirmation()
        elif btn_id == "cancel_btn":
            self.render_view()
            self.query_one("#status_label", Static).update("Edit cancelled.")

    def save_edits(self):
        new_config = {}
        for section, fields in self.inputs.items():
            new_config[section] = {}
            for key, inp in fields.items():
                new_config[section][key] = inp.value.strip()
        self.config = new_config
        self.render_view()
        self.query_one("#status_label", Static).update("[green]Config updated. Ready to deploy.")

    def ask_deploy_confirmation(self):
        def on_confirm():
            ini_path = self.write_config_ini()
            # IMPORTANT: use the new logs screen
            self.app.push_screen(
                DeployLogsScreen(
                    ini_path=ini_path,
                    repo_dir=GAZELLE_REPO_DIR,
                    git_url=GAZELLE_GIT_URL,
                    branch_name=GAZELLE_BRANCH_NAME,
                    deploy_cmd_template=GAZELLE_DEPLOY_CMD_TMPL,
                    artifact_dir=GAZELLE_ARTIFACTS_DIR,
                    prev_screen=self,  # for back navigation
                )
            )
        def on_cancel():
            self.query_one("#status_label", Static).update("Deployment cancelled.")

        dialog = ConfirmDialogScreen(
            "Proceed to deploy DPGs with these settings?\nThis will clone the Gazelle repo (if needed) and start deployment.",
            on_confirm=on_confirm,
            on_cancel=on_cancel
        )
        self.app.push_screen(dialog)

    def write_config_ini(self) -> str:
        # Ensure the artifacts directory exists
        os.makedirs(GAZELLE_ARTIFACTS_DIR, exist_ok=True)
        out_path = INI_OUTPUT_FILENAME
        with open(out_path, "w") as f:
            f.write(ini_text(self.config))
        self.query_one("#status_label", Static).update(f"Wrote config file: {out_path}")
        return out_path

    def deploy_dpgs(self, ini_path):
        try:
            # Ensure the artifacts directory exists
            os.makedirs(GAZELLE_ARTIFACTS_DIR, exist_ok=True)
            if not os.path.exists(GAZELLE_REPO_DIR):
                self.query_one("#status_label", Static).update("Cloning mifos-gazelle...")
                subprocess.run([
                    "git", "clone", "--branch", GAZELLE_BRANCH_NAME, GAZELLE_GIT_URL, GAZELLE_REPO_DIR
                ], check=True)
                self.query_one("#status_label", Static).update("[green]Repo cloned.")

            self.query_one("#status_label", Static).update("Starting deployment (this may take a while)...")
            cmd = [a if a != "{ini_path}" else ini_path for a in GAZELLE_DEPLOY_CMD_TMPL]
            proc = subprocess.run(
                cmd,
                cwd=GAZELLE_REPO_DIR,  # repo dir where run.sh is
                capture_output=True,
                text=True,
                timeout=1800
            )
            if proc.returncode == 0:
                self.query_one("#status_label", Static).update(
                    f"[green]Deployment successful!\n{proc.stdout[:350]}"
                )
            else:
                self.query_one("#status_label", Static).update(
                    f"[red]Deployment failed:\n{proc.stderr[:350]}"
                )
        except Exception as e:
            self.query_one("#status_label", Static).update(f"[red]Deployment error: {e}")
