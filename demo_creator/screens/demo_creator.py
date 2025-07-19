import json
import os
import uuid
import datetime
from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Static, Input, Button, Footer
from textual.app import ComposeResult
from jsonschema import validate
from demo_creator.schema import schema
from demo_creator.utils import (
    get_demo_file_name,
    update_metadata,
    snapshot_latest_to_dated,
)

class DemoCreatorScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Demo Creator", id="title", classes="title")
        with Vertical(id="form"):
            self.status = Static("", id="status")
            yield self.status
            yield Static("Demo Name:")
            self.demo_name = Input(placeholder="e.g., Onboarding Walkthrough")
            yield self.demo_name
            yield Static("Demo Description (optional):")
            self.demo_description = Input(placeholder="Short description...")
            yield self.demo_description
            yield Static("How many steps?")
            self.step_count = Input(placeholder="e.g., 3")
            yield self.step_count
            yield Button("Start", id="start_button")
        yield Footer()
        self.step_index = 1
        self.total_steps = 0
        self.demo_data = {}

    def on_button_pressed(self, event: Button.Pressed) -> None:
        label = event.button.label
        if event.button.id == "start_button":
            self.start_demo_flow()
        elif label == "Next":
            self.capture_step_input()
        elif label == "Back":
            self.go_back_step()
        elif label == "Submit":
            self.capture_step_input()

    def start_demo_flow(self):
        try:
            count = int(self.step_count.value.strip())
            if count < 1:
                raise ValueError("Must be at least 1 step.")
            self.total_steps = count
            self.demo_data = {
                "demoId": str(uuid.uuid4()),
                "demoName": self.demo_name.value.strip(),
                "steps": {}
            }
            desc = self.demo_description.value.strip()
            if desc:
                self.demo_data["demoDescription"] = desc
            self.clear_form()
            self.render_step_form()
        except Exception as e:
            self.status.update(f"[red]❌ {e}")

    def clear_form(self):
        self.query_one("#form").remove_children()

    def render_step_form(self):
        form = self.query_one("#form")
        form.mount(Static(f"Step {self.step_index} Title:"))
        self.step_title = Input(placeholder="e.g., Open Dashboard")
        form.mount(self.step_title)
        form.mount(Static("Step URL:"))
        self.step_url = Input(placeholder="e.g., https://example.com")
        form.mount(self.step_url)
        form.mount(Static("Step Details:"))
        self.step_details = Input(placeholder="What happens in this step?")
        form.mount(self.step_details)
        step_data = self.demo_data["steps"].get(str(self.step_index))
        if step_data:
            self.step_title.value = step_data.get("title", "")
            self.step_url.value = step_data.get("url", "")
            self.step_details.value = step_data.get("details", "")
        if self.step_index > 1:
            form.mount(Button("Back"))
        label = "Submit" if self.step_index == self.total_steps else "Next"
        form.mount(Button(label))

    def capture_step_input(self):
        self.demo_data["steps"][str(self.step_index)] = {
            "title": self.step_title.value.strip(),
            "url": self.step_url.value.strip(),
            "details": self.step_details.value.strip()
        }
        self.step_index += 1
        if self.step_index <= self.total_steps:
            self.clear_form()
            self.render_step_form()
        else:
            self.finalize()

    def go_back_step(self):
        self.demo_data["steps"][str(self.step_index)] = {
            "title": self.step_title.value.strip(),
            "url": self.step_url.value.strip(),
            "details": self.step_details.value.strip()
        }
        self.step_index = max(1, self.step_index - 1)
        self.clear_form()
        self.render_step_form()

    def finalize(self):
        try:
            validate(instance=self.demo_data, schema=schema)
            demo_name = self.demo_data["demoName"]
            file_name = get_demo_file_name(demo_name)
            username = getattr(self.app, 'current_user', 'system')
            latest_dir = os.path.join("demos", "latest")
            os.makedirs(latest_dir, exist_ok=True)
            latest_file = os.path.join(latest_dir, file_name)
            with open(latest_file, "w") as f:
                json.dump(self.demo_data, f, indent=2)
            update_metadata(self.demo_data, file_name, username)
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H-%M-%S")
            snapshot_latest_to_dated(date_str, time_str, latest_dir=latest_dir)
            self.app.last_demo_file = latest_file
            self.app.pop_screen()               # Done with creator
            self.app.show_upload_screen()
        except Exception as ve:
            self.status.update(f"[red]❌ Validation Error: {ve}")
