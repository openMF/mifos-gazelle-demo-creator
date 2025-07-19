from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Static, Input, Button
from textual.app import ComposeResult
from demo_creator.utils import upload_to_jfrog

class UploadScreen(Screen):
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
            self.repo_url = Input(placeholder="e.g., https://<org>.jfrog.io/artifactory/<repo>/demos/demo_output.json")
            yield self.repo_url
            self.status = Static("", id="upload_status")
            yield self.status
            yield Button("Upload", id="upload_button")
            yield Button("Cancel", id="cancel_upload")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "upload_button":
            self.handle_upload()
        elif event.button.id == "cancel_upload":
            self.app.pop_screen()
            self.app.show_main_menu()

    def handle_upload(self):
        success, message = upload_to_jfrog(
            self.username.value.strip(),
            self.password.value.strip(),
            self.repo_url.value.strip()
        )
        color = "green" if success else "red"
        self.status.update(f"[{color}]{message}")
