from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Static, Input, Button, Footer
from textual.app import ComposeResult
from demo_creator.utils import threaded_upload_to_jfrog, threaded_delete_from_jfrog
import os
import json
from textual.binding import Binding


class UploadScreen(Screen):
    CSS_PATH = "../assets/upload_form.tcss"
    BINDINGS = [Binding("escape", "go_back", "Back", show=True)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._upload_cancelled = False

    def compose(self) -> ComposeResult:
        with Vertical(id="upload_form"):
            yield Static("Upload to JFrog Artifactory")
            yield Static("Username:")
            self.username = Input(placeholder="Enter JFrog username")
            yield self.username
            yield Static("Password or API Key:")
            self.password = Input(
                password=True, placeholder="Enter API key or password"
            )
            yield self.password
            yield Static("Repo URL (full):")
            self.repo_url = Input(
                placeholder="e.g., https://<org>.jfrog.io/artifactory/<repo>/"
            )
            yield self.repo_url
            self.status = Static("", id="upload_status")
            yield self.status
            self.upload_button = Button("Upload", id="upload_button")
            yield self.upload_button
            self.cancel_button = Button("Cancel", id="cancel_upload")
            yield self.cancel_button
        yield Footer()
        self._upload_cancelled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "upload_button":
            self.sync_deleted_and_upload()
        elif event.button.id == "cancel_upload":
            self.cancel_upload()

    def sync_deleted_and_upload(self):
        self.upload_button.disabled = True
        self._upload_cancelled = False

        # Step 1: Deletion sync
        self.status.update("[yellow]Syncing deleted files... Please wait.")

        # Get filenames to delete
        metadata_path = os.path.join("demos", "latest", "metadata.json")
        deleted_files = []
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            deleted_files = [
                demo["file_name"]
                for demo in metadata.get("demos", [])
                if demo.get("deleted", False)
            ]

        def on_delete_done(success_delete, msg_delete):
            # Step 2: Trigger upload after deletes finish
            self.app.call_from_thread(
                self.status.update,
                f"[yellow]Uploading files... Please wait.\n" + (msg_delete or ""),
            )

            def on_upload_complete(success, msg_upload):
                color = "green" if success else "red"
                # Combine deletion and upload results
                self.app.call_from_thread(
                    self.status.update,
                    f"[{color}]{msg_delete or ''}\n{msg_upload or ''}",
                )
                self.app.call_from_thread(
                    setattr, self.upload_button, "disabled", False
                )

            def cancel_flag():
                return self._upload_cancelled

            threaded_upload_to_jfrog(
                self.username.value.strip(),
                self.password.value.strip(),
                self.repo_url.value.strip(),
                folder="demos/",
                ui_callback=on_upload_complete,
                cancel_flag=cancel_flag,
            )

        def cancel_flag():
            return self._upload_cancelled

        threaded_delete_from_jfrog(
            self.username.value.strip(),
            self.password.value.strip(),
            self.repo_url.value.strip(),
            deleted_files,
            ui_callback=on_delete_done,
            cancel_flag=cancel_flag,
        )

    def cancel_upload(self):
        self._upload_cancelled = True
        self.status.update("[red]Upload cancelled by user.")
        self.upload_button.disabled = False

    def action_go_back(self) -> None:
        self.app.pop_screen()
        # Optionally refresh main menu:
        if hasattr(self.app.screen_stack[-1], "reload"):
            self.app.screen_stack[-1].reload()
