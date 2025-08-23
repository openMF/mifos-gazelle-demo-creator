import os
import signal
import asyncio
import re
from textual.screen import Screen
from textual.containers import Vertical, ScrollableContainer, Horizontal
from textual.widgets import Static, Button, Footer
from textual.app import ComposeResult

def strip_ansi(s):
    # Remove all ANSI escape sequences (color codes)
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', s)

class DeployLogsScreen(Screen):
    CSS_PATH = "../assets/deploy_logs.tcss"
    BINDINGS = [("ctrl+c", "cancel_deploy", "Cancel Deployment")]

    def __init__(self, ini_path, repo_dir, git_url, branch_name, deploy_cmd_template, artifact_dir, prev_screen=None):
        super().__init__()
        self.ini_path = ini_path
        self.repo_dir = repo_dir
        self.git_url = git_url
        self.branch_name = branch_name
        self.deploy_cmd_template = deploy_cmd_template
        self.artifact_dir = artifact_dir
        self.prev_screen = prev_screen
        self.log_lines = []
        self.log_buffer = []
        self.process_finished = False
        self.process_ok = None
        self._deploy_proc = None

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
        self.set_interval(0.5, self._update_logs_ui)  # Only refresh UI every 0.5s
        asyncio.create_task(self.run_deploy_job())

    async def run_deploy_job(self):
        os.makedirs(self.artifact_dir, exist_ok=True)
        try:
            # ---- CLONE STEP ----
            clone_msg = f"[dim]Cloning repo: {self.git_url} (branch: {self.branch_name})"
            already_msg = "[dim]Repo already exists, skipping clone."
            if not os.path.exists(self.repo_dir):
                await self._log_buffered(clone_msg)
                self._deploy_proc = await asyncio.create_subprocess_exec(
                    "git", "clone", "--branch", self.branch_name, self.git_url, self.repo_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                )
                await self._stream_subprocess(self._deploy_proc)
                if self._deploy_proc.returncode != 0:
                    await self._log_buffered(f"[red]Repo clone failed!")
                    self.status_widget.update("[red]Clone failed.")
                    self.process_ok = False
                    self.process_finished = True
                    return
                await self._log_buffered("[green]Repo cloned successfully!")
            else:
                await self._log_buffered(already_msg)

            # ---- DEPLOY STEP ----
            await self._log_buffered("[dim]Starting deployment process...")
            cmd = [a if a != "{ini_path}" else self.ini_path for a in self.deploy_cmd_template]
            self._deploy_proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.repo_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            await self._stream_subprocess(self._deploy_proc)
            if self._deploy_proc.returncode == 0:
                await self._log_buffered(f"[green]Deployment successful!")
                self.status_widget.update("[green]Deployment finished.")
                self.process_ok = True
            else:
                await self._log_buffered(f"[red]Deployment failed [{self._deploy_proc.returncode}].")
                self.status_widget.update("[red]Deployment failed.")
                self.process_ok = False

        except Exception as e:
            await self._log_buffered(f"[red]Error: {e}")
            self.status_widget.update(f"[red]Error: {e}")
            self.process_ok = False
        self.process_finished = True

    async def _stream_subprocess(self, proc):
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            # Strip ANSI color codes from every log line
            line = strip_ansi(line.decode().rstrip())
            await self._log_buffered(line)
        await proc.wait()

    async def _log_buffered(self, line: str):
        """Buffer log lines for batch UI updating."""
        self.log_buffer.append(line)
        # Optionally flush buffer if it grows too large
        if len(self.log_buffer) > 200:
            self._update_logs_ui()

    def _update_logs_ui(self):
        """Flush buffered logs to main lines, trim, and update the UI."""
        if self.log_buffer:
            self.log_lines.extend(self.log_buffer)
            self.log_buffer = []
        # Show only last 300 lines for performance
        self.log_lines = self.log_lines[-300:]
        content = "\n".join(self.log_lines)
        self.log_widget.update(content)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_btn":
            self.app.pop_screen()
        elif event.button.id == "cancel_btn":
            self.stop_deployment()

    def action_cancel_deploy(self):
        self.stop_deployment()

    def stop_deployment(self):
        if self._deploy_proc is not None and not self.process_finished:
            try:
                # Send SIGINT for graceful stop/cancel
                if hasattr(self._deploy_proc, "send_signal"):
                    self._deploy_proc.send_signal(signal.SIGINT)
                else:
                    self._deploy_proc.terminate()
                self.status_widget.update("[red]Deployment cancelled by user.[yellow] Cleanup in progress...")
                asyncio.create_task(self._log_buffered("[red]Deployment cancelled by user.[yellow] Cleanup in progress..."))

                # Kick off a cleanup monitor that waits for script exit
                async def wait_for_cleanup(proc, screen):
                    await proc.wait()  # Wait for script to finish (including its cleanup)
                    screen.status_widget.update("[green]Cleanup done. Deployment stopped.")
                    await screen._log_buffered("[green]Cleanup done. Deployment stopped.")

                asyncio.create_task(wait_for_cleanup(self._deploy_proc, self))
                self.process_finished = True
            except Exception as e:
                self.status_widget.update(f"[red]Could not stop process: {e}")
                asyncio.create_task(self._log_buffered(f"[red]Could not stop process: {e}"))
