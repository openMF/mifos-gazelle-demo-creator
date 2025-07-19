import datetime
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button, Footer
from textual.app import ComposeResult
import json
import os

from demo_creator.screens.show_demo import ShowDemoScreen
from demo_creator.utils import snapshot_latest_to_dated

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
                yield Static("Actions", classes="demo_col demo_col_actions")

            for demo in self.get_demo_list():
                demo_id = demo["demoId"]
                name = demo["name"]
                desc = demo["description"][:57] + "..." if len(demo.get("description", "")) > 60 else demo.get("description", "")
                updated = demo.get("updated_at", "")
                with Horizontal(classes="demo_row"):
                    yield Static(name, classes="demo_col demo_col_name")
                    yield Static(desc, classes="demo_col demo_col_desc")
                    yield Static(updated, classes="demo_col demo_col_updated")
                    yield Button("🔍", id=f"show_{demo_id}", classes="show_btn demo_col demo_col_actions")
                    yield Button("✏️", id=f"edit_{demo_id}", classes="edit_btn demo_col demo_col_actions")
                    yield Button("🗑️", id=f"delete_{demo_id}", classes="delete_btn demo_col demo_col_actions")

        yield Footer()

    def get_demo_list(self):
        metadata_path = os.path.join("demos", "latest", "metadata.json")
        if not os.path.exists(metadata_path):
            return []
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        return [d for d in metadata.get("demos", []) if not d.get("deleted")]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_demo_btn":
            self.app.pop_screen()
            self.app.show_demo_creator()
        elif event.button.id.startswith("show_"):
            demo_id = event.button.id.removeprefix("show_")
            self.show_demo(demo_id)
        elif event.button.id.startswith("edit_"):
            demo_id = event.button.id.removeprefix("edit_")
            self.edit_demo(demo_id)
        elif event.button.id.startswith("delete_"):
            demo_id = event.button.id.removeprefix("delete_")
            self.delete_demo(demo_id)
            self.refresh()  # reload UI to reflect deletion

    def delete_demo(self, demo_id):
        metadata_path = os.path.join("demos", "latest", "metadata.json")
        if not os.path.exists(metadata_path):
            return
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        for d in metadata.get("demos", []):
            if d["demoId"] == demo_id:
                d["deleted"] = True
                # Also remove the actual demo file from latest/
                try:
                    os.remove(os.path.join("demos", "latest", d["file_name"]))
                except Exception:
                    pass
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")
        snapshot_latest_to_dated(date_str, time_str, latest_dir=os.path.join("demos", "latest"))
