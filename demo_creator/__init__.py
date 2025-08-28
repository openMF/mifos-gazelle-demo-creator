# flake8: noqa
"""
demo_creator: Core package for the Mifos Gazelle Demo Creator TUI.
Exposes the main app class, core schemas, and key utilities.
"""

from .app import DemoCreatorApp
from .schema import schema, metadata_schema, DPG_DEFAULT_CONFIG
from .utils import (
    threaded_delete_from_jfrog,
    upload_to_jfrog,
    threaded_upload_to_jfrog,
    get_demo_file_name,
    snapshot_latest_to_dated,
    load_metadata,
    save_metadata,
    update_metadata,
)
from .screens import (
    LoginScreen,
    MainMenuScreen,
    DemoCreatorScreen,
    UploadScreen,
    ConfirmDialogScreen,
    DemoDetailScreen,
    DeployDPGScreen,
    DeployLogsScreen,
)
