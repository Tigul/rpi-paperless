import base64
import os
import time

import httpx
import requests
from threading import Thread

from nicegui import ui, Client
import sane
from pypdf import PdfWriter
from sane import get_devices

ui.add_head_html('''
    <style type="text/tailwindcss">
        @layer components {
            .blue-box {
                @apply bg-blue-500 p-20 text-center shadow-lg rounded-lg text-white;
            }
        }
    </style>
''')

# sane.init()
#
# printers = sane.get_devices()
printers = get_devices()
printer_device = None

class CurrentScans:
    def __init__(self):
        self.scans = []

    def add_scan(self, scan):
        self.scans.append(scan)

    def clear(self):
        self.scans.clear()

    def get_scans(self):
        return self.scans

    @property
    def len(self):
        return len(self.scans)

    @len.setter
    def len(self, value):
        pass

    def merge(self):
        filenames = []
        notify("Merging scans into a single PDF...")
        for i, scan in enumerate(self.scans):
            filename = f'scan_{i}.pdf'
            scan.save(filename)
            filenames.append(filename)

        merger = PdfWriter()
        for pdf in filenames:
            merger.append(pdf)
        merger.write("merged_scans.pdf")
        for file in filenames:
            os.remove(file)
        notify(f"Merged {len(self.scans)} scans into merged_scans.pdf")
        current_scans.clear()

    def __len__(self):
        return len(self.scans)

    def __iter__(self):
        return iter(self.scans)


class ScanThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True  # Ensure the thread doesn't block program exit

    def run(self):
        global printer_device
        global current_scans
        global scan_threads
        if not printer_device:
            init_scanner()

        notify("Starting scan...")
        current_scans.add_scan(printer_device.scan())
        scan_threads.remove(self)
        notify(f"Scan completed. Total scans: {len(current_scans)}")


class UploadThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True  # Ensure the thread doesn't block program exit

    def run(self):
        global current_scans
        if len(scan_threads) > 0:
            for thread in scan_threads:
                thread.join()
        current_scans.merge()
        self.send_request()

    def send_request(self):
        global credentials
        global paperless_url
        if not paperless_url:
            notify("Paperless URL is not set. Please set it before uploading.")
            return

        url = f"{paperless_url}/api/documents/post_document/"
        try:
            notify(f"Uploading scans ...")
            # response = requests.post(url, headers=headers, data=data)
            resp = httpx.post(url + "/api/documents/post_document/",
                              headers={"Authorization": "Basic " + credentials},
                              files={'document': ('scan.pdf', open('merged_scans.pdf', 'rb'), 'application/pdf')},
                              data={"title": "Scanned Document", "created": "2023-12-21"})
            if resp.status_code == 200:
                notify(f"Uploaded successfully to {paperless_url}")
        except Exception as e:
            notify(f"Failed to upload scans due to {e}")




current_scans = CurrentScans()
scan_threads = []
credentials = None
paperless_url = None

with ui.grid(columns=2).classes('w-full gap-5'):
    scan_button = ui.button('Scan', on_click=lambda: scan(), icon="document_scanner").classes('blue-box')
    upload_button = ui.button('Upload', on_click=lambda: upload(), icon="upload").classes('blue-box')
    scan_and_upload_button = ui.button('Scan and Upload', on_click=lambda: scan_and_upload(), icon="send").classes('blue-box')

    current_scans_label = ui.label(f'Current Scans: {len(current_scans)}').classes('text-lg font-bold')
    current_scans_label.bind_text(current_scans, "len", backward=lambda n: f'Current Scans: {n}').classes('blue-box')

with ui.expansion('Settings!', icon='settings'):
    printer_select = ui.select([printer[0] for printer in printers], label='Select Printer',
                               value=printers[0][0] if printers else None, on_change=lambda: update_printer_selection())

    ui.label("Paperless Credentials").classes('text-lg font-bold')
    user_name = ui.input('Enter your name', placeholder='Name')
    password = ui.input('Enter your password', placeholder='Password')
    save_credentials = ui.checkbox('Save Credentials', value=False)
    submit_credentials = ui.button('Submit', on_click=lambda: encode_credentials())
    ui.separator()

    ui.label("Paperless URL").classes('text-lg font-bold')
    paperless_url_input = ui.input('Paperless URL', placeholder='https://your-paperless-instance.com')
    save_url = ui.checkbox('Save URL', value=True)
    submit_url = ui.button('Submit URL', on_click=lambda: do_save_url())

    ui.separator()

    ui.label("Fullscreen Mode").classes('text-lg font-bold')
    ui.button('Toggle Fullscreen', on_click=ui.fullscreen().toggle)

def get_scanner_devices():
    global printers
    sane.init()
    printers = sane.get_devices()
    printer_select.options = [printer[0] for printer in printers]
    if not printer_select.value and printers:
        printer_select.value = printers[0][0]
    ui.notify('Scanner devices updated.')

def update_printer_selection():
    global printer_device
    global printer_select
    get_scanner_devices()
    if printer_device:
        return
    printer_device = sane.open(printer_select.value)
    ui.notify('Updated printer selection to: ' + printer_select.value)

def init_scanner():
    global printer_device
    global printer_select
    if not printer_select.value:
        ui.notify("No printer selected. Please select a printer.")
        return
    try:
        printer_device = sane.open(printer_select.value)
        ui.notify(f"Scanner initialized: {printer_device.sane_signature[2]}")
    except Exception as e:
        ui.notify(f"Failed to initialize scanner: {e}")
        printer_device = None

def scan():
    global current_scans
    global scan_threads
    # ui.notify(f'Scanning with {printer_device.sane_signature[2]}...')

    scan_thread = ScanThread(name=f"Scan_{len(current_scans)}", daemon=True)
    scan_threads.append(scan_thread)
    scan_thread.start()

def upload():
    upload_thread = UploadThread(name="Upload", daemon=True)
    upload_thread.start()

def scan_and_upload():
    scan()
    upload()


def encode_credentials():
    global user_name
    global password
    global save_credentials
    global credentials
    creds = f"{user_name.value}:{password.value}"
    base64_credentials = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
    if save_credentials.value:
        with open('credentials.txt', 'w') as f:
            f.write(base64_credentials)
    credentials = base64_credentials
    ui.notify("Credentials saved!" if save_credentials.value else "Credentials submitted!")

def load_credentials():
    global credentials
    if os.path.exists('credentials.txt'):
        with open('credentials.txt', 'r') as f:
            credentials = f.read().strip()
            ui.notify(f'Loaded credentials: {credentials}')

def do_save_url():
    global paperless_url
    global paperless_url_input
    global save_url
    if save_url.value:
        with open('paperless_url.txt', 'w') as f:
            f.write(paperless_url_input.value)
        ui.notify("Paperless URL saved!")
    else:
        ui.notify("Paperless URL not saved.")
    paperless_url = paperless_url_input.value

def load_paperless_url():
    global paperless_url
    global paperless_url_input
    if os.path.exists('paperless_url.txt'):
        with open('paperless_url.txt', 'r') as f:
            paperless_url = f.read().strip()
            paperless_url_input.value = paperless_url
            ui.notify(f'Loaded Paperless URL: {paperless_url}')

def notify(message: str) -> None:
    for client in Client.instances.values():
        if not client.has_socket_connection:
            continue
        with client:
            ui.notify(message)

get_devices()
update_printer_selection()

load_credentials()
load_paperless_url()
ui.run()