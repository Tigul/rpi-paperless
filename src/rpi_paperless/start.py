from .ui import UI

import sane

if __name__ in {"__main__", "__mp_main__"}:
    ui = UI()
    ui.create_ui()
    ui.update_printer_selection()
    ui.load_paperless_url()

    # scanner_watcher = ScannerWatcher(ui.printer_select)
    # scanner_watcher.start()

    sane.init()
    ui.start()
    ui.update_printer_selection()

