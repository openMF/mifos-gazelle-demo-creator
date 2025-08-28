import os
import json
import shutil
from typing import Optional

from textual.screen import Screen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Input, Button, Footer, Label
from textual.app import ComposeResult, App
from textual.binding import Binding
from jsonschema import validate, ValidationError

from demo_creator.schema import schema
from demo_creator.screens.confirm_dialog_screen import ConfirmDialogScreen


def get_demo_file_path(demo_id: str) -> Optional[str]:
    """
    Finds and returns the full file path for the demo JSON file with the given demo_id.
    Looks into demos/latest/ folder and metadata.json to get the filename.
    Returns None if not found.
    """
    metadata_path = os.path.join("demos", "latest", "metadata.json")
    if not os.path.exists(metadata_path):
        return None

    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    demos = metadata.get("demos", [])
    for demo in demos:
        if demo.get("demoId") == demo_id and not demo.get("deleted", False):
            fname = (
                demo.get("file_name")
                or f'{demo.get("demoName", "").replace(" ", "_")}.json'
            )
            return os.path.join("demos", "latest", fname)
    return None


def remove_demo_from_metadata(demo_id: str) -> None:
    """
    Marks demo as deleted in metadata.json by setting 'deleted': True.
    """
    metadata_path = os.path.join("demos", "latest", "metadata.json")
    if not os.path.exists(metadata_path):
        return

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    updated = False
    for demo in metadata.get("demos", []):
        if demo.get("demoId") == demo_id:
            demo["deleted"] = True
            updated = True
            break

    if updated:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)


class DemoDetailScreen(Screen):
    CSS_PATH = "../assets/demo_detail.tcss"

    BINDINGS = [
        Binding("escape", "go_back", "Go Back", show=True),
    ]

    def __init__(self, demo_id: str) -> None:
        super().__init__()
        self.demo_id = demo_id
        self.demo_data = None
        self.file_path = None
        self.edit_mode = False
        self.inputs = {}
        self.status_label: Optional[Static] = None

    def compose(self) -> ComposeResult:
        # Header and main vertical container
        with Vertical(id="demo_detail_container"):
            yield Static("Demo Details", id="screen_title")

            # Top-level metadata and buttons container
            with Horizontal(id="top_buttons_row"):
                self.btn_edit = Button("Edit", id="edit_btn")
                yield self.btn_edit
                self.btn_delete = Button("Delete", id="delete_btn")
                yield self.btn_delete
                self.btn_save = Button("Save", id="save_btn", disabled=True)
                yield self.btn_save
                self.btn_cancel = Button("Cancel", id="cancel_btn", disabled=True)
                yield self.btn_cancel

            # Status message label
            self.status_label = Static("", id="status_label")
            yield self.status_label

            # Scrollable container for demo info and steps
            self.scroll_container = ScrollableContainer(id="demo_scroll_container")
            yield self.scroll_container

            yield Footer()

    def on_mount(self) -> None:
        self.load_demo_data()
        self.call_later(self.render_demo_view)

    def load_demo_data(self) -> None:
        self.file_path = get_demo_file_path(self.demo_id)
        if not self.file_path or not os.path.exists(self.file_path):
            self.status_label.update("[red]❌ Demo file not found.")
            return

        with open(self.file_path, "r") as f:
            self.demo_data = json.load(f)

    def render_demo_view(self) -> None:
        if not self.demo_data:
            return

        self.edit_mode = False
        self.btn_edit.disabled = False
        self.btn_delete.disabled = False
        self.btn_save.disabled = True
        self.btn_cancel.disabled = True

        # Clear all children from the scroll container
        self.scroll_container.remove_children()

        # Add static metadata fields directly to the scroll container
        self.scroll_container.mount(Static("Demo Name:", classes="label"))
        self.scroll_container.mount(
            Static(
                self.demo_data.get("demoName", ""),
                id="demo_name_static",
                classes="meta_data",
            )
        )

        self.scroll_container.mount(Static("Demo Description:", classes="label"))
        self.scroll_container.mount(
            Static(
                self.demo_data.get("demoDescription", "(No description)"),
                id="demo_desc_static",
                classes="meta_data",
            )
        )

        # DPGs/tags display
        self.scroll_container.mount(Static("Required DPGs:", classes="label"))
        tags = self.demo_data.get("tags", [])
        if tags:
            tags_display = " ".join(
                f"[b][reverse][white] {tag} [/white][/reverse][/b]" for tag in tags
            )
        else:
            tags_display = "(None)"
        self.scroll_container.mount(
            Static(tags_display, id="dpg_tags_static", classes="meta_data")
        )

        # Populate steps as static labels
        steps = self.demo_data.get("steps", {})
        self.log(f"Found {len(steps)} steps for demo '{self.demo_id}'")

        if not steps:
            self.scroll_container.mount(
                Static("No steps found.", classes="empty_steps")
            )
            return

        sorted_step_keys = sorted(steps.keys(), key=lambda x: int(x))
        for step_idx in sorted_step_keys:
            step = steps[step_idx]
            step_container = Vertical(
                Label(f"Step {step_idx}", classes="step_label"),
                Static(f"Title: {step.get('title', '')}", classes="step_field"),
                Static(f"URL: {step.get('url', '')}", classes="step_field"),
                Static(f"Details: {step.get('details', '')}", classes="step_field"),
                classes="step_container",
            )
            self.scroll_container.mount(step_container)

    def render_demo_edit(self) -> None:
        if not self.demo_data:
            return

        self.edit_mode = True
        self.btn_edit.disabled = True
        self.btn_delete.disabled = True
        self.btn_save.disabled = False
        self.btn_cancel.disabled = False

        self.scroll_container.remove_children()
        self.inputs = {}

        # Add inputs for metadata
        self.scroll_container.mount(Static("Demo Name:", classes="label"))
        self.input_demo_name = Input(
            value=self.demo_data.get("demoName", ""), id="input_demo_name"
        )
        self.scroll_container.mount(self.input_demo_name)

        self.scroll_container.mount(Static("Demo Description:", classes="label"))
        self.input_demo_desc = Input(
            value=self.demo_data.get("demoDescription", ""), id="input_demo_desc"
        )
        self.scroll_container.mount(self.input_demo_desc)

        self.scroll_container.mount(
            Static("Required DPGs (comma separated):", classes="label")
        )
        tags_array = self.demo_data.get("tags", [])
        tags_str = ", ".join(tags_array) if tags_array else ""
        self.input_demo_tags = Input(value=tags_str, id="input_demo_tags")
        self.scroll_container.mount(self.input_demo_tags)

        self.scroll_container.mount(Static("Steps:", classes="section_header"))
        # Add inputs for steps
        steps = self.demo_data.get("steps", {})
        sorted_step_keys = sorted(steps.keys(), key=lambda x: int(x))
        for step_idx in sorted_step_keys:
            step = steps[step_idx]

            # Inputs for this step
            title_input = Input(
                value=step.get("title", ""),
                placeholder="Step Title",
                classes="step_input",
            )
            url_input = Input(
                value=step.get("url", ""), placeholder="Step URL", classes="step_input"
            )
            details_input = Input(
                value=step.get("details", ""),
                placeholder="Step Details",
                classes="step_input",
            )

            self.inputs[step_idx] = {
                "title": title_input,
                "url": url_input,
                "details": details_input,
            }

            # Compose everything at construction; do NOT use mount() on detached widgets
            step_container = Vertical(
                Label(f"Step {step_idx}", classes="step_label"),
                Static("Title:", classes="label"),
                title_input,
                Static("URL:", classes="label"),
                url_input,
                Static("Details:", classes="label"),
                details_input,
                classes="step_container",
            )
            self.scroll_container.mount(step_container)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "edit_btn":
            self.render_demo_edit()
            self.status_label.update("")
        elif btn_id == "delete_btn":
            self.show_delete_confirmation()
        elif btn_id == "save_btn":
            self.handle_save()
        elif btn_id == "cancel_btn":
            self.render_demo_view()
            self.status_label.update("Edit cancelled.")
        else:
            pass

    def show_delete_confirmation(self) -> None:
        def on_confirm():
            self.delete_demo()
            # ...refresh logic if needed

        def on_cancel():
            pass

        dialog = ConfirmDialogScreen(
            "Are you sure you want to delete this demo?",
            on_confirm=on_confirm,
            on_cancel=on_cancel,
        )
        self.app.push_screen(dialog)

    def delete_demo(self) -> None:
        try:
            if self.file_path and os.path.exists(self.file_path):
                os.remove(self.file_path)
            remove_demo_from_metadata(self.demo_id)
            self.status_label.update("[green]Demo deleted successfully!")
            self.app.pop_screen()
            # --- Refresh main menu datatable ---
            app: App = self.app
            main_menu_screen = app.screen_stack[-1]
            if hasattr(main_menu_screen, "reload"):
                main_menu_screen.reload()
        except Exception as e:
            self.status_label.update(f"[red]Failed to delete demo: {e}")

    def handle_save(self) -> None:
        try:
            updated_data = {}

            demo_name = self.input_demo_name.value.strip()
            if not demo_name:
                self.status_label.update("[red]Demo Name cannot be empty.")
                return

            updated_data["demoName"] = demo_name
            demo_desc = self.input_demo_desc.value.strip()
            if demo_desc:
                updated_data["demoDescription"] = demo_desc

            tags_raw = (
                self.input_demo_tags.value.strip()
                if hasattr(self, "input_demo_tags")
                else ""
            )
            tags_list = [t.strip() for t in tags_raw.split(",") if t.strip()]
            updated_data["tags"] = tags_list

            steps = {}
            for idx, fields in self.inputs.items():
                title = fields["title"].value.strip()
                url = fields["url"].value.strip()
                details = fields["details"].value.strip()
                if not title:
                    self.status_label.update(f"[red]Step {idx} Title cannot be empty.")
                    return
                steps[str(idx)] = {
                    "title": title,
                    "url": url,
                    "details": details,
                }
            updated_data["steps"] = steps

            # Preserve the original demoId and created_at!
            demo_id = self.demo_data.get("demoId")
            updated_data["demoId"] = demo_id

            # Validate JSON schema
            validate(instance=updated_data, schema=schema)

            # Handle file name change if demo name changed
            from demo_creator.utils import (
                get_demo_file_name,
                load_metadata,
                save_metadata,
                snapshot_latest_to_dated,
            )

            old_file_name = os.path.basename(self.file_path)
            new_file_name = get_demo_file_name(demo_name)
            latest_dir = os.path.dirname(self.file_path)
            new_file_path = os.path.join(latest_dir, new_file_name)

            if new_file_name != old_file_name:
                if os.path.exists(new_file_path):
                    self.status_label.update(
                        f"[red]A demo with that name already exists. Choose a different name."
                    )
                    return
                os.rename(self.file_path, new_file_path)
                self.file_path = new_file_path

            # Save updated demo file
            with open(self.file_path, "w") as f:
                json.dump(updated_data, f, indent=2)

            # --- Now update only the existing entry in metadata.json ---
            metadata = load_metadata()
            username = getattr(self.app, "current_user", "system")
            import datetime

            now = datetime.datetime.now(datetime.timezone.utc)
            now_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")

            entry = None
            for d in metadata["demos"]:
                if d["demoId"] == demo_id:
                    entry = d
                    break

            if entry:
                entry["name"] = demo_name
                entry["file_name"] = new_file_name
                entry["description"] = updated_data.get("demoDescription", "")
                entry["steps_count"] = len(steps)
                entry["updated_at"] = now_str
                entry["last_modified_by"] = username
                entry["deleted"] = False
                entry["version"] = entry.get("version", 1) + 1
                entry["tags"] = updated_data.get("tags", [])
                # created_at and created_by remain unchanged!
            else:
                # (Should not happen in edit flow, but fallback!) Create a new one if not found
                entry = {
                    "demoId": demo_id,
                    "name": demo_name,
                    "file_name": new_file_name,
                    "description": updated_data.get("demoDescription", ""),
                    "version": 1,
                    "steps_count": len(steps),
                    "created_at": now_str,
                    "updated_at": now_str,
                    "created_by": username,
                    "last_modified_by": username,
                    "deleted": False,
                    "tags": [],
                }
                metadata["demos"].append(entry)

            save_metadata(metadata)

            # Optional: Versioned snapshot
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H-%M-%S")
            snapshot_latest_to_dated(date_str, time_str, latest_dir=latest_dir)

            self.demo_data = updated_data
            self.status_label.update("[green]Demo saved successfully!")
            self.render_demo_view()

        except ValidationError as ve:
            self.status_label.update(f"[red]Validation Error: {ve.message}")
        except Exception as e:
            self.status_label.update(f"[red]Failed to save demo: {e}")

    def update_metadata(self, updated_demo: dict) -> None:
        metadata_path = os.path.join("demos", "latest", "metadata.json")
        if not os.path.exists(metadata_path):
            return

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        updated = False
        for demo in metadata.get("demos", []):
            if demo.get("demoId") == updated_demo.get("demoId"):
                demo["name"] = updated_demo.get("demoName", demo.get("name"))
                if updated_demo.get("demoDescription"):
                    demo["description"] = updated_demo["demoDescription"]
                updated = True
                break
        if updated:
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

    def action_go_back(self) -> None:
        # Pop and tell main menu to reload
        self.app.pop_screen()
        # After the pop, schedule the reload (on next tick so MainMenuScreen is top of stack)
        app: App = self.app
        # Find the main menu screen (assuming it's the previous/topmost screen)
        main_menu_screen = app.screen_stack[-1]  # Or however you manage your stack
        if hasattr(main_menu_screen, "reload"):
            main_menu_screen.reload()
