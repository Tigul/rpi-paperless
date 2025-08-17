import os

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
    def __init__(self):
        self.scan_button = None
        self.upload_button = None
        self.scan_and_upload_button = None
        self.printer_select = None
        self.user_name = None
        self.password = None
        self.save_credentials = None
        self.submit_credentials = None
        self.paperless_url_input = None
        self.save_url = None
        self.submit_url = None
        self.update_scanner = None

        self.scanner_device: Scanner = None

        self.paperless_url = None

        self.credentials = Credentials()

        self.current_document = Document()


    def create_ui(self):
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

    def update_printer_selection(self):
        devices = Scanner.get_devices()
        if devices != self.printer_select.options:
            self.printer_select.options = devices
            if not self.printer_select.value and devices:
                self.printer_select.value = devices[0]
            self.printer_select.update()
            ui.notify(f"Scanner devices updated: {devices}")
            self.update_scanner_device()

    def update_scanner_device(self):
        if self.scanner_device:
            self.scanner_device.close()
        self.scanner_device = Scanner(self.printer_select.value)


    def scan(self, upload = False):
        self.scanner_device.scan(self.current_document, upload, self.credentials, self.paperless_url)

    def upload(self):
        upload_thread = UploadThread(self.current_document, self.scanner_device.scanning_event, self.credentials,
                                     self.paperless_url, name="Upload", daemon=True)
        upload_thread.start()

    def scan_and_upload(self):
        self.scan(upload=True)

    def do_save_url(self):
        if self.save_url.value:
            with open('paperless_url.txt', 'w') as f:
                f.write(self.paperless_url_input.value)
            ui.notify("Paperless URL saved!")
        else:
            ui.notify("Paperless URL not saved.")
        self.paperless_url = self.paperless_url_input.value

    def load_paperless_url(self):
        if os.path.exists('paperless_url.txt'):
            with open('paperless_url.txt', 'r') as f:
                self.paperless_url = f.read().strip()
                self.paperless_url_input.value = self.paperless_url
                ui.notify(f'Loaded Paperless URL: {self.paperless_url}')

    def start(self):
        ui.run()
