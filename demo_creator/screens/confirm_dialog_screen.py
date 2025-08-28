from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button, Label


class ConfirmDialogScreen(Screen):
    CSS_PATH = "../assets/confirm_dialog.tcss"
    BINDINGS = []

    def __init__(self, message, on_confirm, on_cancel):
        super().__init__()
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

    def compose(self):
        yield Vertical(
            Label(self.message, id="confirm_message"),
            Horizontal(
                Button("Yes", id="confirm_yes"),
                Button("No", id="confirm_no"),
                id="dialog_buttons",
            ),
            id="confirm_overlay",
        )

    def on_button_pressed(self, event):
        if event.button.id == "confirm_yes":
            self.app.pop_screen()
            self.on_confirm()
        elif event.button.id == "confirm_no":
            self.app.pop_screen()
            self.on_cancel()
