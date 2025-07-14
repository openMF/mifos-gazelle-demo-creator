from demo_creator.app import DemoCreatorApp
from textual.testing import AppTest, wait_for_idle


class TestDemoCreator(AppTest, app=DemoCreatorApp):

    async def test_app_initializes(self):
        """Check if the app starts and renders the title."""
        async with self.run_app() as pilot:
            await wait_for_idle()
            title_widget = self.app.query_one("#title")
            assert title_widget.renderable == " Demo Creator"
