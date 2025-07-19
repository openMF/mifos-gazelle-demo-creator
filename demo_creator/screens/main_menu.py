from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button, Footer
from textual.app import ComposeResult
import json
import os

class MainMenuScreen(Screen):
    CSS_PATH = "../assets/main_menu.tcss"
    def compose(self) -> ComposeResult:
        with Vertical(id="main_menu"):
            yield Static("Main Menu", id="main_menu_title")
            yield Static(f"User: {getattr(self.app, 'current_user', '')}", id="main_menu_user")
            yield Static(f"Email: {getattr(self.app, 'current_email', '')}", id="main_menu_email")
            yield Button("Create New Demo", id="create_demo_btn")
            yield Static("Available Demos:", id="demo_list_title")

            # Header row for the table:
            with Horizontal(id="demo_table_header"):
                yield Static("Demo Name", classes="demo_col demo_col_name")
                yield Static("Description", classes="demo_col demo_col_desc")
                yield Static("Last Updated", classes="demo_col demo_col_updated")

            # Table rows:
            for row in self.get_demo_rows():
                name, desc, updated = row
                with Horizontal(classes="demo_row"):
                    yield Static(name, classes="demo_col demo_col_name")
                    yield Static(desc, classes="demo_col demo_col_desc")
                    yield Static(updated, classes="demo_col demo_col_updated")

        yield Footer()

    def get_demo_rows(self):
        metadata_path = os.path.join("demos", "latest", "metadata.json")
        if not os.path.exists(metadata_path):
            return []
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        demos = metadata.get("demos", [])
        rows = []
        for demo in demos:
            if demo.get("deleted"):
                continue
            name = demo.get("name", "")
            desc = demo.get("description", "")
            if len(desc) > 60:
                desc = desc[:57] + "..."
            updated = demo.get("updated_at", "")
            rows.append((name, desc, updated))
        return rows

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_demo_btn":
            self.app.pop_screen()
            self.app.show_demo_creator()
