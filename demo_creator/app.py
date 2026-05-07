from textual.app import App
from textual.binding import Binding
from demo_creator.screens import (
    LoginScreen,
    MainMenuScreen,
    DemoCreatorScreen,
    UploadScreen,
)


class DemoCreatorApp(App):
    CSS_PATH = "./assets/base.tcss"

    BINDINGS = [
       Binding("ctrl+q", "quit", "Quit", show=True),  
       Binding("ctrl+z", "suspend_process", "Suspend (go to terminal)", show=True), 
    ]

    def on_mount(self):
        self.push_screen(LoginScreen())

    def show_main_menu(self):
        self.push_screen(MainMenuScreen())

    def show_demo_creator(self):
        self.push_screen(DemoCreatorScreen())

    def show_upload_screen(self):
        self.push_screen(UploadScreen())
