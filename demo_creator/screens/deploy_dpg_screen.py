import os
import subprocess
import configparser
from textual.screen import Screen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Input, Button, Footer
from textual.app import ComposeResult
from demo_creator.screens.confirm_dialog_screen import ConfirmDialogScreen
from demo_creator.screens.deploy_logs_screen import DeployLogsScreen
from demo_creator.schema import DPG_DEFAULT_CONFIG
from textual.binding import Binding
from demo_creator.config import (
    GAZELLE_ARTIFACTS_DIR,
    GAZELLE_REPO_DIR,
    INI_OUTPUT_FILENAME,
    GAZELLE_GIT_URL,
    GAZELLE_BRANCH_NAME,
    GAZELLE_DEPLOY_CMD_TMPL,
)


def ini_text(config: dict) -> str:
    lines = []
    for section, params in config.items():
        lines.append(f"[{section}]")
        for k, v in params.items():
            lines.append(f"{k} = {v}")
        lines.append("")
    return "\n".join(lines)


def parse_ini_to_dict(ini_path):
    config = configparser.ConfigParser()
    config.optionxform = str  # preserve case
    config.read(ini_path)
    out = {}
    for section in config.sections():
        out[section] = dict(config.items(section))
    return out

def save_dict_to_ini(config_dict, ini_path):
    config = configparser.ConfigParser()
    config.optionxform = str  # preserve case
    for section, params in config_dict.items():
        config[section] = {str(k): str(v) for k, v in params.items()}
    os.makedirs(os.path.dirname(ini_path), exist_ok=True)
    with open(ini_path, "w") as f:
        config.write(f)


class DeployDPGScreen(Screen):
    CSS_PATH = "../assets/deploy_dpg.tcss"
    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.config = self.load_or_default_config()
        self.edit_mode = False
        self.inputs = {}

    def load_or_default_config(self):
        if os.path.exists(INI_OUTPUT_FILENAME):
            try:
                return parse_ini_to_dict(INI_OUTPUT_FILENAME)
            except Exception as e:
                print(f"Could not parse config INI file, loading defaults. Error: {e}")
        return {section: dict(params) for section, params in DPG_DEFAULT_CONFIG.items()}

    def compose(self) -> ComposeResult:
        with Vertical(id="dpg_container"):
            yield Static("Deploy DPGs", id="dpg_title")
            with Horizontal(id="dpg_top_buttons_row"):
                yield Button("Edit", id="dpg_edit_btn")
                yield Button("Save", id="dpg_save_btn", disabled=True)
                yield Button("Cancel", id="dpg_cancel_btn", disabled=True)
                yield Button("Deploy", id="dpg_deploy_btn", disabled=False)
            yield Static("", id="dpg_status_label")
            yield ScrollableContainer(id="dpg_config_scroll")
            yield Footer()

    def on_mount(self) -> None:
        self.config = self.load_or_default_config()
        self.render_view()

    def render_view(self):
        self.edit_mode = False
        self.query_one("#dpg_edit_btn", Button).disabled = False
        self.query_one("#dpg_save_btn", Button).disabled = True
        self.query_one("#dpg_cancel_btn", Button).disabled = True
        self.query_one("#dpg_deploy_btn", Button).disabled = False

        scroll = self.query_one("#dpg_config_scroll", ScrollableContainer)
        scroll.remove_children()

        for section, params in self.config.items():
            scroll.mount(Static(f"{section}", classes="dpg_section_header"))
            for key, val in params.items():
                row = Horizontal(
                    Static(f"{key}:", classes="dpg_label"),
                    Static(str(val), classes="dpg_ini_value"),
                    classes="dpg_ini_row",
                )
                scroll.mount(row)
        scroll.refresh()

    def render_edit(self):
        self.edit_mode = True
        self.query_one("#dpg_edit_btn", Button).disabled = True
        self.query_one("#dpg_save_btn", Button).disabled = False
        self.query_one("#dpg_cancel_btn", Button).disabled = False
        self.query_one("#dpg_deploy_btn", Button).disabled = True

        scroll = self.query_one("#dpg_config_scroll", ScrollableContainer)
        scroll.remove_children()
        self.inputs = {}

        for section, params in self.config.items():
            scroll.mount(Static(f"{section}", classes="dpg_section_header"))
            self.inputs[section] = {}
            for key, val in params.items():
                inp = Input(value=str(val), classes="dpg_ini_input")
                self.inputs[section][key] = inp
                row = Horizontal(
                    Static(f"{key}:", classes="dpg_label"), inp, classes="dpg_ini_row"
                )
                scroll.mount(row)
        scroll.refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "dpg_edit_btn":
            self.render_edit()
            self.query_one("#dpg_status_label", Static).update("")
        elif btn_id == "dpg_save_btn":
            self.save_edits()
        elif btn_id == "dpg_cancel_btn":
            self.render_view()
            self.query_one("#dpg_status_label", Static).update("Edit cancelled.")
        elif btn_id == "dpg_deploy_btn":
            if not self.edit_mode:
                self.ask_deploy_confirmation()

    def save_edits(self):
        new_config = {}
        for section, fields in self.inputs.items():
            new_config[section] = {}
            for key, inp in fields.items():
                new_config[section][key] = inp.value.strip()
        self.config = new_config
        save_dict_to_ini(self.config, INI_OUTPUT_FILENAME)
        self.render_view()
        self.query_one("#dpg_status_label", Static).update(
            f"[green]Config updated and saved to INI file: {INI_OUTPUT_FILENAME}"
        )

    def ask_deploy_confirmation(self):
        def on_confirm():
            ini_path = INI_OUTPUT_FILENAME
            if not os.path.exists(ini_path):
                save_dict_to_ini(self.config, ini_path)
            self.app.push_screen(
                DeployLogsScreen(
                    ini_path=ini_path,
                    repo_dir=GAZELLE_REPO_DIR,
                    git_url=GAZELLE_GIT_URL,
                    branch_name=GAZELLE_BRANCH_NAME,
                    deploy_cmd_template=GAZELLE_DEPLOY_CMD_TMPL,
                    artifact_dir=GAZELLE_ARTIFACTS_DIR,
                    prev_screen=self,
                )
            )

        def on_cancel():
            self.query_one("#dpg_status_label", Static).update("Deployment cancelled.")

        dialog = ConfirmDialogScreen(
            "Proceed to deploy DPGs with these settings?\nThis will clone the Gazelle repo (if needed) and start deployment.",
            on_confirm=on_confirm,
            on_cancel=on_cancel,
        )
        self.app.push_screen(dialog)

    def deploy_dpgs(self, ini_path):
        try:
            os.makedirs(GAZELLE_ARTIFACTS_DIR, exist_ok=True)
            if not os.path.exists(GAZELLE_REPO_DIR):
                self.query_one("#dpg_status_label", Static).update(
                    "Cloning mifos-gazelle..."
                )
                subprocess.run(
                    [
                        "git",
                        "clone",
                        "--branch",
                        GAZELLE_BRANCH_NAME,
                        GAZELLE_GIT_URL,
                        GAZELLE_REPO_DIR,
                    ],
                    check=True,
                )
                self.query_one("#dpg_status_label", Static).update(
                    "[green]Repo cloned."
                )

            self.query_one("#dpg_status_label", Static).update(
                "Starting deployment (this may take a while)..."
            )
            cmd = [
                a if a != "{ini_path}" else ini_path for a in GAZELLE_DEPLOY_CMD_TMPL
            ]
            proc = subprocess.run(
                cmd, cwd=GAZELLE_REPO_DIR, capture_output=True, text=True, timeout=1800
            )
            if proc.returncode == 0:
                self.query_one("#dpg_status_label", Static).update(
                    f"[green]Deployment successful!\n{proc.stdout[:350]}"
                )
            else:
                self.query_one("#dpg_status_label", Static).update(
                    f"[red]Deployment failed:\n{proc.stderr[:350]}"
                )
        except Exception as e:
            self.query_one("#dpg_status_label", Static).update(
                f"[red]Deployment error: {e}"
            )

    def action_go_back(self) -> None:
        self.app.pop_screen()
        if hasattr(self.app.screen_stack[-1], "reload"):
            self.app.screen_stack[-1].reload()
