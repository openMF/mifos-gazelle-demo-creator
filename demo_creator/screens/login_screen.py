from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Static, Input, Button, Footer
from textual.app import ComposeResult


class LoginScreen(Screen):
    CSS_PATH = "../assets/login_form.tcss"

    def compose(self) -> ComposeResult:
        with Vertical(id="login_form"):
            yield Static("Enter your user details", id="login_title")
            yield Static("Username:")
            self.username = Input(placeholder="e.g., alice")
            yield self.username
            yield Static("Email:")
            self.email = Input(placeholder="user@example.com")
            yield self.email
            self.status = Static("", id="login_status")
            yield self.status
            yield Button("Continue", id="continue_login")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "continue_login":
            username = self.username.value.strip()
            email = self.email.value.strip()
            if not username or not email or "@" not in email:
                self.status.update("[red]Please provide a valid username and email.")
                return
            self.app.current_user = username
            self.app.current_email = email
            self.app.pop_screen()
            self.app.show_main_menu()
