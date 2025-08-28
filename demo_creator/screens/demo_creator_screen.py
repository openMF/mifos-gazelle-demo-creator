import uuid
import os
import json
from datetime import datetime, timezone
from textual.screen import Screen
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Input, Button, Footer, Label
from textual.app import ComposeResult, App
from jsonschema import validate
from demo_creator.schema import schema
from demo_creator.utils import (
    get_demo_file_name,
    update_metadata,
    snapshot_latest_to_dated,
)
from textual.binding import Binding


class DemoCreatorScreen(Screen):
    CSS_PATH = "../assets/demo_creator.tcss"
    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="demo_detail_container"):
            yield Static("Create Demo", id="screen_title")
            # Button row UNDER the title, just like Demo Details
            with Horizontal(id="top_buttons_row"):
                self.btn_submit = Button("Submit", id="submit_button")
                yield self.btn_submit
                self.btn_add_step = Button("Add Step", id="add_step_button")
                yield self.btn_add_step
                self.btn_cancel = Button("Cancel", id="cancel_button")
                yield self.btn_cancel
            self.status_label = Static("", id="status_label")
            yield self.status_label
            self.scroll_container = ScrollableContainer(id="demo_scroll_container")
            yield self.scroll_container
            yield Footer()

    def on_mount(self) -> None:
        # Source of truth for all field values
        self.demo_data = {
            "demoName": "",
            "demoDescription": "",
            "tags": [],
            "steps": [
                {"title": "", "url": "", "details": ""},
            ],
        }
        self.inputs = {}
        self.render_form()

    def render_form(self):
        self.inputs = {}
        self.scroll_container.remove_children()

        # Demo Name
        self.scroll_container.mount(Static("Demo Name:", classes="label"))
        name_input = Input(
            value=self.demo_data.get("demoName", ""),
            placeholder="e.g., Onboarding Walkthrough",
        )
        self.inputs["demoName"] = name_input
        self.scroll_container.mount(name_input)

        # Demo Description
        self.scroll_container.mount(Static("Demo Description:", classes="label"))
        desc_input = Input(
            value=self.demo_data.get("demoDescription", ""),
            placeholder="Short description...",
        )
        self.inputs["demoDescription"] = desc_input
        self.scroll_container.mount(desc_input)

        # DPGs (tags)
        self.scroll_container.mount(
            Static("Required DPGs (comma separated):", classes="label")
        )
        dpgs_str = (
            ", ".join(self.demo_data.get("tags", []))
            if self.demo_data.get("tags")
            else ""
        )
        dpgs_input = Input(
            value=dpgs_str, placeholder="e.g., MifosX, Payments, Reports"
        )
        self.inputs["tags"] = dpgs_input
        self.scroll_container.mount(dpgs_input)

        # Steps Section Title
        self.scroll_container.mount(Static("Steps:", classes="section_header"))

        # Steps
        for idx, step in enumerate(self.demo_data["steps"]):
            step_inputs = {}
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
            step_inputs["title"] = title_input
            step_inputs["url"] = url_input
            step_inputs["details"] = details_input
            self.inputs[f"step_{idx}"] = step_inputs

            step_container = Vertical(
                Label(f"Step {idx+1}", classes="step_label"),
                Static("Title:", classes="label"),
                title_input,
                Static("URL:", classes="label"),
                url_input,
                Static("Details:", classes="label"),
                details_input,
                Horizontal(
                    Button(
                        "Remove Step",
                        id=f"remove_step_{idx}",
                        classes="remove_step_btn",
                        disabled=(len(self.demo_data["steps"]) == 1),
                    ),
                    classes="step_btn_row",
                ),
                classes="step_container",
            )
            self.scroll_container.mount(step_container)

    def add_step(self):
        self.save_inputs_to_data()
        self.demo_data["steps"].append({"title": "", "url": "", "details": ""})
        self.render_form()

    def remove_step(self, idx):
        self.save_inputs_to_data()
        if len(self.demo_data["steps"]) > 1 and 0 <= idx < len(self.demo_data["steps"]):
            del self.demo_data["steps"][idx]
            self.render_form()

    def save_inputs_to_data(self):
        self.demo_data["demoName"] = self.inputs["demoName"].value
        self.demo_data["demoDescription"] = self.inputs["demoDescription"].value

        tags_field = self.inputs.get("tags")
        if tags_field:
            tags_raw = tags_field.value.strip()
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            self.demo_data["tags"] = tags
        else:
            self.demo_data["tags"] = []

        for idx in range(len(self.demo_data["steps"])):
            if f"step_{idx}" in self.inputs:
                step_inputs = self.inputs[f"step_{idx}"]
                self.demo_data["steps"][idx]["title"] = step_inputs["title"].value
                self.demo_data["steps"][idx]["url"] = step_inputs["url"].value
                self.demo_data["steps"][idx]["details"] = step_inputs["details"].value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "add_step_button":
            self.add_step()
        elif btn_id == "submit_button":
            self.handle_submit()
        elif btn_id == "cancel_button":
            self.app.pop_screen()
        elif btn_id and btn_id.startswith("remove_step_"):
            idx = int(btn_id.rsplit("_", 1)[1])
            self.remove_step(idx)

    def handle_submit(self):
        self.save_inputs_to_data()
        demo_name = self.demo_data["demoName"].strip()
        if not demo_name:
            self.status_label.update("[red]Demo Name cannot be empty.")
            return
        steps = {}
        for idx, step in enumerate(self.demo_data["steps"], 1):
            t = step["title"].strip()
            u = step["url"].strip()
            d = step["details"].strip()
            if not t:
                self.status_label.update(f"[red]Step {idx} Title cannot be empty.")
                return
            steps[str(idx)] = {"title": t, "url": u, "details": d}
        if not steps:
            self.status_label.update("[red]Must add at least one step.")
            return
        demo_data = {
            "demoId": str(uuid.uuid4()),
            "demoName": demo_name,
            "steps": steps,
            "tags": list(self.demo_data.get("tags", [])),  # <-- Add tags to result JSON
        }
        demo_desc = self.demo_data["demoDescription"].strip()
        if demo_desc:
            demo_data["demoDescription"] = demo_desc
        try:
            validate(instance=demo_data, schema=schema)
            file_name = get_demo_file_name(demo_name)
            username = getattr(self.app, "current_user", "system")
            latest_dir = os.path.join("demos", "latest")
            os.makedirs(latest_dir, exist_ok=True)
            latest_file = os.path.join(latest_dir, file_name)
            with open(latest_file, "w") as f:
                json.dump(demo_data, f, indent=2)
            update_metadata(demo_data, file_name, username)
            now = datetime.now(timezone.utc)
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H-%M-%S")
            snapshot_latest_to_dated(date_str, time_str, latest_dir=latest_dir)
            self.app.last_demo_file = latest_file
            self.status_label.update("[green]Demo created successfully!")
            self.app.pop_screen()
            app: App = self.app
            main_menu_screen = app.screen_stack[-1]
            if hasattr(main_menu_screen, "reload"):
                main_menu_screen.reload()
        except Exception as ve:
            self.status_label.update(f"[red]❌ Validation Error: {ve}")

    def action_go_back(self) -> None:
        self.app.pop_screen()
        # Optionally refresh main menu:
        if hasattr(self.app.screen_stack[-1], "reload"):
            self.app.screen_stack[-1].reload()
