from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Static, Button, Footer
from textual.app import ComposeResult

class MainMenuScreen(Screen):
    def compose(self) -> ComposeResult:
        with Vertical(id="main_menu"):
            yield Static("Main Menu", id="main_menu_title")
            yield Static(f"User: {getattr(self.app, 'current_user', '')}", id="main_menu_user")
            yield Static(f"Email: {getattr(self.app, 'current_email', '')}", id="main_menu_email")
            yield Button("Create New Demo", id="create_demo_btn")
        yield Footer()
            # Later: add demo list, edit/delete buttons, etc.

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_demo_btn":
            self.app.pop_screen()
            self.app.show_demo_creator()
