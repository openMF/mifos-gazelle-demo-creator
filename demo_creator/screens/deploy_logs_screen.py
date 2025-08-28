import os
import threading
import subprocess
import signal
import re
from textual.screen import Screen
from textual.containers import Vertical, ScrollableContainer, Horizontal
from textual.widgets import Static, Button, Footer
from textual.app import ComposeResult
from demo_creator.config import LOG_DISPLAY_LIMIT, LOG_STORE_LIMIT


def strip_ansi(s):
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-\~]")
    return ansi_escape.sub("", s)


class DeployLogsScreen(Screen):
    CSS_PATH = "../assets/deploy_logs.tcss"
    BINDINGS = [("ctrl+c", "cancel_deploy", "Cancel Deployment")]

    def __init__(
        self,
        ini_path,
        repo_dir,
        git_url,
        branch_name,
        deploy_cmd_template,
        artifact_dir,
        prev_screen=None,
    ):
        super().__init__()
        self.ini_path = ini_path
        self.repo_dir = repo_dir
        self.git_url = git_url
        self.branch_name = branch_name
        self.deploy_cmd_template = deploy_cmd_template
        self.artifact_dir = artifact_dir
        self.prev_screen = prev_screen
        self.log_lines = []
        self.process_finished = False
        self.process_ok = None
        self._deploy_proc = None
        self._deploy_thread = None
        self._cancel_requested = False

    def compose(self) -> ComposeResult:
        with Vertical(id="logs_screen_container"):
            yield Static("Deployment Logs", id="logs_title")
            with Horizontal(id="logs_top_row"):
                yield Button("Back", id="back_btn")
                yield Button("Cancel", id="cancel_btn")
                yield Static("", id="logs_status")
            yield ScrollableContainer(Static("", id="logs_text"), id="logs_scroll")
            yield Footer()

    def on_mount(self):
        self.log_widget = self.query_one("#logs_text", Static)
        self.status_widget = self.query_one("#logs_status", Static)
        self._deploy_thread = threading.Thread(target=self.run_deploy_job, daemon=True)
        self._deploy_thread.start()
        self.set_interval(1.0, self._update_logs_ui)  # Less frequent, less lag

    def run_deploy_job(self):
        os.makedirs(self.artifact_dir, exist_ok=True)
        try:
            clone_msg = (
                f"[dim]Cloning repo: {self.git_url} (branch: {self.branch_name})"
            )
            if not os.path.exists(self.repo_dir):
                self._thread_safe_log(clone_msg)
                proc = subprocess.Popen(
                    [
                        "git",
                        "clone",
                        "--branch",
                        self.branch_name,
                        self.git_url,
                        self.repo_dir,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                self._deploy_proc = proc
                self._thread_safe_stream_subprocess(proc)
                if proc.returncode is not None and proc.returncode != 0:
                    self._thread_safe_log(f"[red]Repo clone failed!")
                    self._thread_safe_status("[red]Clone failed.")
                    self.process_ok = False
                    self.process_finished = True
                    return
                self._thread_safe_log("[green]Repo cloned successfully!")
            else:
                self._thread_safe_log(
                    "[dim]Repo already exists, pulling latest changes..."
                )
                proc = subprocess.Popen(
                    ["git", "pull"],
                    cwd=self.repo_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                self._thread_safe_stream_subprocess(proc)
                if proc.returncode is not None and proc.returncode != 0:
                    self._thread_safe_log(f"[red]Repo pull failed!")
                    self._thread_safe_status("[red]Pull failed.")
                    self.process_ok = False
                    self.process_finished = True
                    return
                self._thread_safe_log("[green]Repo updated with latest changes!")
            # ---- DEPLOY STEP ----
            self._thread_safe_log("[dim]Starting deployment process...")
            cmd = [
                a if a != "{ini_path}" else self.ini_path
                for a in self.deploy_cmd_template
            ]
            proc = subprocess.Popen(
                cmd,
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            self._deploy_proc = proc
            self._thread_safe_stream_subprocess(proc)
            if proc.returncode == 0:
                self._thread_safe_log("[green]Deployment successful!")
                self._thread_safe_status("[green]Deployment finished.")
                self.process_ok = True
            else:
                self._thread_safe_log(f"[red]Deployment failed [{proc.returncode}].")
                self._thread_safe_status("[red]Deployment failed.")
                self.process_ok = False
        except Exception as e:
            self._thread_safe_log(f"[red]Error: {e}")
            self._thread_safe_status(f"[red]Error: {e}")
            self.process_ok = False
        self.process_finished = True

    def _thread_safe_log(self, line: str):
        self.app.call_from_thread(self._log_live, line)

    def _thread_safe_status(self, msg: str):
        self.app.call_from_thread(self.status_widget.update, msg)

    def _thread_safe_stream_subprocess(self, proc):
        # Read lines from proc, update logs
        try:
            while True:
                if self._cancel_requested:
                    break
                line = proc.stdout.readline()
                if not line:
                    break
                line = strip_ansi(line.rstrip())
                self._thread_safe_log(line)
            proc.wait()
        except Exception as e:
            self._thread_safe_log(f"[red]Exception in log streaming: {e}")

    def _log_live(self, line: str):
        # In-place progress updates (\r): overwrite previous line
        if "\r" in line:
            for part in line.split("\r"):
                if part:
                    if self.log_lines:
                        self.log_lines[-1] = part
                    else:
                        self.log_lines.append(part)
        else:
            self.log_lines.append(line)
        if len(self.log_lines) > LOG_STORE_LIMIT:
            self.log_lines = self.log_lines[-LOG_STORE_LIMIT:]

    def _update_logs_ui(self):
        content = "\n".join(self.log_lines[-LOG_DISPLAY_LIMIT:])
        self.log_widget.update(content)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_btn":
            self.process_finished = True
            self._cancel_requested = True
            self.app.pop_screen()
        elif event.button.id == "cancel_btn":
            self.action_cancel_deploy()

    def action_cancel_deploy(self):
        self.stop_deployment()

    def stop_deployment(self):
        self._cancel_requested = True
        if self._deploy_proc and not self.process_finished:
            try:
                # Try SIGINT first
                if hasattr(self._deploy_proc, "send_signal"):
                    self._deploy_proc.send_signal(signal.SIGINT)
                else:
                    self._deploy_proc.terminate()
                self.status_widget.update(
                    "[red]Deployment cancelled by user.[yellow] Cleanup in progress..."
                )
                self._log_live(
                    "[red]Deployment cancelled by user.[yellow] Cleanup in progress..."
                )
                threading.Thread(
                    target=self._wait_for_cleanup,
                    args=(self._deploy_proc,),
                    daemon=True,
                ).start()
                self.process_finished = True
            except Exception as e:
                self.status_widget.update(f"[red]Could not stop process: {e}")
                self._log_live(f"[red]Could not stop process: {e}")

    def _wait_for_cleanup(self, proc):
        proc.wait()
        self.app.call_from_thread(
            self.status_widget.update, "[green]Cleanup done. Deployment stopped."
        )
        self.app.call_from_thread(
            self._log_live, "[green]Cleanup done. Deployment stopped."
        )
