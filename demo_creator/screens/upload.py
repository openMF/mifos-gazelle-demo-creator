from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Static, Input, Button, Footer
from textual.app import ComposeResult
from demo_creator.utils import threaded_upload_to_jfrog

class UploadScreen(Screen):
    CSS_PATH = "../assets/upload.tcss"
    
    def compose(self) -> ComposeResult:
        with Vertical(id="upload_form"):
            yield Static("🔼 Upload to JFrog Artifactory")
            yield Static("Username:")
            self.username = Input(placeholder="Enter JFrog username")
            yield self.username
            yield Static("Password or API Key:")
            self.password = Input(password=True, placeholder="Enter API key or password")
            yield self.password
            yield Static("Repo URL (full):")
            self.repo_url = Input(placeholder="e.g., https://<org>.jfrog.io/artifactory/<repo>/demos/")
            yield self.repo_url
            self.status = Static("", id="upload_status")
            yield self.status
            self.upload_button = Button("Upload", id="upload_button")
            yield self.upload_button
            self.cancel_button = Button("Cancel", id="cancel_upload")
            yield self.cancel_button
        yield Footer()
        self._upload_cancelled = False  # Internal flag for cancel


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "upload_button":
            self.handle_upload()
        elif event.button.id == "cancel_upload":
            self.cancel_upload()

    def handle_upload(self):
        self.status.update("[yellow]Uploading files... Please wait.")
        self.upload_button.disabled = True
        self._upload_cancelled = False  # Reset cancel state

        def on_upload_complete(success, message):
            color = "green" if success else "red"
            self.app.call_from_thread(
                self.status.update, f"[{color}]{message}"
            )
            self.app.call_from_thread(
                setattr, self.upload_button, 'disabled', False
            )

        # Pass cancellation flag via closure
        def cancel_flag():
            return self._upload_cancelled
        
        # Patch to pass "cancel_flag" to utils
        threaded_upload_to_jfrog(
            self.username.value.strip(),
            self.password.value.strip(),
            self.repo_url.value.strip(),
            folder="demos/",
            ui_callback=on_upload_complete,
            cancel_flag=cancel_flag  # new argument
        )

    def cancel_upload(self):
        # Set cancellation flag
        self._upload_cancelled = True
        self.status.update("[red]Upload cancelled by user.")
        self.upload_button.disabled = False    
