"""NiceGUI front-end for the Raspberry Pi paperless scanner.

Defines the :class:`UI` class which builds the web interface, wires the
buttons to the scanner/upload logic and persists the Paperless URL.
"""
import os
from typing import Optional

import sane
from nicegui import ui

from .credentials import Credentials
from .document import Document
from .scanner import Scanner, ScanThread
from .upload import UploadThread

ui.add_head_html('''
    <style type="text/tailwindcss">
        @layer components {
            .blue-box {
                @apply bg-blue-500 p-20 text-center shadow-lg rounded-lg text-white;
            }
        }
    </style>
''')


class UI:
    """Builds and runs the NiceGUI web interface.

    A single shared page is created (NiceGUI's auto-index page); all widgets
    are stored as attributes so the event handlers can read their values. The
    instance also owns the active :class:`~rpi_paperless.scanner.Scanner`, the
    :class:`~rpi_paperless.credentials.Credentials` and the in-progress
    :class:`~rpi_paperless.document.Document`.
    """

    def __init__(self) -> None:
        """Initialise widget references and the scanner/credentials/document state.

        Widget attributes are set to ``None`` here and populated later in
        :meth:`create_ui`. The directory holding the persisted Paperless URL is
        created eagerly so saving never fails on a fresh device.
        """
        self.scan_button: Optional[ui.button] = None
        self.upload_button: Optional[ui.button] = None
        self.scan_and_upload_button: Optional[ui.button] = None
        self.printer_select: Optional[ui.select] = None
        self.user_name: Optional[ui.input] = None
        self.password: Optional[ui.input] = None
        self.save_credentials: Optional[ui.checkbox] = None
        self.submit_credentials: Optional[ui.button] = None
        self.paperless_url_input: Optional[ui.input] = None
        self.save_url: Optional[ui.checkbox] = None
        self.submit_url: Optional[ui.button] = None
        self.update_scanner: Optional[ui.button] = None

        self.scanner_device: Optional[Scanner] = None

        self.paperless_url: Optional[str] = None
        # Anchor the saved URL next to the credentials/merges instead of the
        # current working directory, which is undefined when run as a service.
        self.paperless_url_path: str = os.path.join(
            os.path.dirname(__file__), "..", "..", "config", "paperless_url.txt")
        os.makedirs(os.path.dirname(self.paperless_url_path), exist_ok=True)

        self.credentials: Credentials = Credentials()

        self.current_document: Document = Document()


    def create_ui(self) -> None:
        """Build the page layout: the action buttons, page counter and settings.

        Must be called once before :meth:`start`. Populates the widget
        attributes declared in :meth:`__init__` and binds the page counter to
        the current document's page count.
        """
        with ui.grid(columns=2).classes('w-full gap-5'):
            self.scan_button = ui.button('Scan', on_click=lambda: self.scan(), icon="document_scanner").classes(
                'blue-box')
            self.upload_button = ui.button('Upload', on_click=lambda: self.upload(), icon="upload").classes('blue-box')
            self.scan_and_upload_button = ui.button('Scan and Upload', on_click=lambda: self.scan_and_upload(),
                                                    icon="send").classes('blue-box')
            self.update_scanner = ui.button('Update Scanner', on_click=lambda: self.update_printer_selection(), icon="refresh").classes('blue-box')


            current_scans_label = ui.label(f'Current Scans: {self.current_document.number_of_pages}').classes(
                'text-lg font-bold')
        current_scans_label.bind_text_from(self.current_document, "number_of_pages",
                                      backward=lambda n: f'Current Scans: {n}').classes('blue-box').classes('w-full')

        with ui.expansion('Settings!', icon='settings'):
            self.printer_select = ui.select([], label='Select Printer',
                                            on_change=lambda: self.update_printer_selection())

            ui.label("Paperless Credentials").classes('text-lg font-bold')
            self.user_name = ui.input('Enter your name', placeholder='Name')
            self.password = ui.input('Enter your password', placeholder='Password')
            self.save_credentials = ui.checkbox('Save Credentials', value=False)
            self.submit_credentials = ui.button('Submit', on_click=lambda: self.credentials.encode_credentials(
                self.user_name.value, self.password.value, self.save_credentials.value))
            ui.separator()

            ui.label("Paperless URL").classes('text-lg font-bold')
            self.paperless_url_input = ui.input('Paperless URL', placeholder='https://your-paperless-instance.com')
            self.save_url = ui.checkbox('Save URL', value=True)
            self.submit_url = ui.button('Submit URL', on_click=lambda: self.do_save_url())

            ui.separator()

            ui.label("Fullscreen Mode").classes('text-lg font-bold')
            ui.button('Toggle Fullscreen', on_click=ui.fullscreen().toggle)

    def update_printer_selection(self) -> None:
        """Refresh the scanner dropdown from the currently connected devices.

        If the device list changed, the dropdown options are updated, the first
        device is selected when none is chosen yet, and the active scanner is
        re-opened via :meth:`update_scanner_device`.
        """
        devices = Scanner.get_devices()
        if devices != self.printer_select.options:
            self.printer_select.options = devices
            if not self.printer_select.value and devices:
                self.printer_select.value = devices[0]
            self.printer_select.update()
            ui.notify(f"Scanner devices updated: {devices}")
            self.update_scanner_device()

    def update_scanner_device(self) -> None:
        """Close the current scanner (if any) and open the selected device."""
        if self.scanner_device:
            self.scanner_device.close()
        self.scanner_device = Scanner(self.printer_select.value)


    def scan(self, upload: bool = False) -> None:
        """Start scanning a page with the active scanner.

        :param upload: If True, upload the document automatically once the scan
            has been added to it.
        """
        self.scanner_device.scan(self.current_document, upload, self.credentials, self.paperless_url)

    def upload(self) -> None:
        """Upload the current document to Paperless in a background thread."""
        upload_thread = UploadThread(self.current_document, self.credentials,
                                     self.paperless_url, name="Upload", daemon=True)
        upload_thread.start()

    def scan_and_upload(self) -> None:
        """Scan a page and upload the document once the scan completes."""
        self.scan(upload=True)

    def do_save_url(self) -> None:
        """Apply the entered Paperless URL and optionally persist it to disk.

        The URL is always stored on the instance; it is only written to
        ``config/paperless_url.txt`` when the "Save URL" checkbox is ticked.
        """
        if self.save_url.value:
            with open(self.paperless_url_path, 'w') as f:
                f.write(self.paperless_url_input.value)
            ui.notify("Paperless URL saved!")
        else:
            ui.notify("Paperless URL not saved.")
        self.paperless_url = self.paperless_url_input.value

    def load_paperless_url(self) -> None:
        """Load a previously saved Paperless URL into the instance and input field."""
        if os.path.exists(self.paperless_url_path):
            with open(self.paperless_url_path, 'r') as f:
                self.paperless_url = f.read().strip()
                self.paperless_url_input.value = self.paperless_url
                ui.notify(f'Loaded Paperless URL: {self.paperless_url}')

    def start(self) -> None:
        """Start the NiceGUI web server (blocking).

        Binds to all interfaces on port 8080 with the auto-reloader disabled so
        it runs reliably as a systemd service.
        """
        ui.run(host="0.0.0.0", port=8080, reload=False, show=False)
