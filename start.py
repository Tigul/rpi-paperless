"""Entry point: initialise SANE, build the UI and run the web server.

Run directly (``python start.py``) or via the systemd service. The
``__mp_main__`` guard keeps it compatible with NiceGUI's reload mechanism.
"""
from nicegui import ui

from rpi_paperless.ui import UI

import sane

app_ui = UI()


@ui.page('/')
def index() -> None:
    app_ui.create_ui()
    app_ui.load_paperless_url()
    app_ui.load_scan_resolution()
    app_ui.update_printer_selection()


if __name__ in {"__main__", "__mp_main__"}:
    # SANE must be initialised before any other sane.* call is made.
    sane.init()

    ui.run(host="0.0.0.0", port=8080, reload=False, show=False)
