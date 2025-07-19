from textual.containers import Vertical
from textual.widgets import Static, Input, Button
from textual.app import ComposeResult
from textual.screen import Screen
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
            self.app.exit()

    def handle_upload(self):
        success, message = upload_to_jfrog(
            self.username.value.strip(),
            self.password.value.strip(),
            self.repo_url.value.strip()
        )
        color = "green" if success else "red"
        self.status.update(f"[{color}]{message}")

class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        with Vertical(id="login_form"):
            yield Static("Enter your user details", id="login_title")
            yield Static("Username:")
            self.username = Input(placeholder="e.g., alice", id="username_input")
            yield self.username
            yield Static("Email:")
            self.email = Input(placeholder="user@example.com", id="email_input")
            yield self.email
            self.status = Static("", id="login_status")
            yield self.status
            yield Button("Continue", id="continue_login")

class MainMenuScreen(Screen):
    def compose(self) -> ComposeResult:
        with Vertical(id="main_menu"):
            yield Static("Main Menu", id="main_menu_title")
            yield Static(f"User: {getattr(self.app, 'current_user', '')}", id="main_menu_user")
            yield Static(f"Email: {getattr(self.app, 'current_email', '')}", id="main_menu_email")
            yield Button("Create New Demo", id="create_demo_btn")
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_demo_btn":
            self.app.show_demo_creator_form()

