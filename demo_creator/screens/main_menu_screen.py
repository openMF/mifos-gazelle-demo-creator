from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button, Footer, DataTable
from textual.app import ComposeResult
from datetime import datetime
import os
import json

from demo_creator.screens.demo_creator_screen import DemoCreatorScreen
from demo_creator.screens.upload_form_screen import UploadScreen
from demo_creator.screens.deploy_dpg_screen import DeployDPGScreen
from demo_creator.screens.demo_detail_screen import DemoDetailScreen


class MainMenuScreen(Screen):
    CSS_PATH = "../assets/main_menu.tcss"

    def compose(self) -> ComposeResult:
        """Create child widgets for the main menu screen."""
        with Vertical(id="main_menu_container"):
            # Title and user info
            yield Static("Main Menu", id="main_menu_title")
            yield Static(
                f"User: {getattr(self.app, 'current_user', '')}", id="user_info"
            )
            yield Static(
                f"Email: {getattr(self.app, 'current_email', '')}", id="email_info"
            )

            # Buttons row
            with Horizontal(id="action_buttons"):
                yield Button("Create New Demo", id="create_demo_btn")
                yield Button("Upload Demo", id="upload_demo_btn")
                yield Button("Deploy DPG", id="deploy_dpg_btn")

            # Label for demos list
            yield Static("Available Demos:", id="demo_list_title")

            # DataTable widget for demos
            self.data_table = DataTable(id="demo_data_table")
            self.data_table.cursor_type = (
                "row"  # Crucial change: enable full row selection
            )
            yield self.data_table

            # Footer
            yield Footer()

    def on_mount(self) -> None:
        """Actions to perform when the screen is mounted."""
        self.load_demo_list()
        self.data_table.focus()  # Ensure the data table has keyboard focus

    def load_demo_list(self) -> None:
        """Loads the list of demos into the DataTable."""
        demos = self.get_demo_list()
        self.data_table.clear(columns=True)

        # Add columns
        self.data_table.add_column("Demo Name", width=25)
        self.data_table.add_column("Description", width=45)
        self.data_table.add_column("Last Updated", width=28)
        self.data_table.add_column("DPGs Required")

        if not demos:
            # Show placeholder row if no demos
            self.data_table.add_row("No demos found.", "", "")
            return

        # Add each demo as a row; use demoId as row key for selection
        for demo in demos:
            name = demo.get("name", "")
            desc = demo.get("description", "") or ""
            if len(desc) > 60:
                desc = desc[:57] + "..."
            updated = demo.get("updated_at", "")
            if updated:
                try:
                    dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    updated_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    updated_str = updated
            else:
                updated_str = ""
            tags = demo.get("tags", [])
            if tags:
                tag_chips = " ".join(
                    f"[bold][bright_black][[/bright_black][/bold][bold][#228B22]{tag}[/#228B22][/bold][bold][bright_black]][/bright_black][/bold]"
                    for tag in tags
                )
            else:
                tag_chips = ""

            self.data_table.add_row(
                name, desc, updated_str, tag_chips, key=demo["demoId"]
            )

    def get_demo_list(self) -> list:
        """Fetches the list of demos from the metadata file, sorted by latest updated first."""
        metadata_path = os.path.join("demos", "latest", "metadata.json")
        if not os.path.exists(metadata_path):
            return []

        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            return []

        demos = [d for d in metadata.get("demos", []) if not d.get("deleted")]

        # Define key function for sorting by 'updated_at'
        def date_key(demo):
            val = demo.get("updated_at", "")
            try:
                # Replace 'Z' with '+00:00' for ISO8601 compatibility
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except Exception:
                return datetime.min  # fallback if date missing or invalid

        # Sort by updated_at (latest first)
        demos.sort(key=date_key, reverse=True)
        return demos

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """
        Called when a row is selected (Enter key, or double-click with mouse).
        This event handler should now work correctly because cursor_type is 'row'.
        """
        demo_id = event.row_key
        # Check for the placeholder row's key, which would be 'None'
        if not demo_id or demo_id == "None":
            return

        self.app.push_screen(DemoDetailScreen(demo_id))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button presses on the screen."""
        btn_id = event.button.id
        if btn_id == "create_demo_btn":
            self.app.push_screen(DemoCreatorScreen())
        elif btn_id == "upload_demo_btn":
            self.app.push_screen(UploadScreen())
        elif btn_id == "deploy_dpg_btn":
            self.app.push_screen(DeployDPGScreen())

    def reload(self):
        self.load_demo_list()
        self.data_table.focus()
