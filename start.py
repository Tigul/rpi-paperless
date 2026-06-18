"""Entry point: initialise SANE, build the UI and run the web server.

Run directly (``python start.py``) or via the systemd service. The
``__mp_main__`` guard keeps it compatible with NiceGUI's reload mechanism.
"""
from rpi_paperless.ui import UI

import sane

if __name__ in {"__main__", "__mp_main__"}:
    # SANE must be initialised before any other sane.* call is made.
    sane.init()

    ui = UI()
    ui.create_ui()
    ui.update_printer_selection()
    ui.load_paperless_url()

    # scanner_watcher = ScannerWatcher(ui.printer_select)
    # scanner_watcher.start()

    ui.start()
