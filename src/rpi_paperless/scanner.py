import time
from threading import Thread, Event
from typing import List

from .credentials import Credentials
from .document import CurrentScan, Document
from .upload import UploadThread
from .utils import notify

import sane

class Scanner:
    def __init__(self, scanner_device: str):
        self.device = None
        if not scanner_device:
            notify("No scanner device provided.")
            return
        self.device_name = scanner_device
        print(f"Initializing scanner device: {scanner_device}")
        self.device = sane.open(scanner_device)
        self.running_scans = []
        self.scanning_event = Event()
        self.scanning_event.clear()

    @classmethod
    def get_devices(cls) -> List[str]:
        """
        Get a list of available printer devices.
        This is a placeholder for actual implementation.
        """
        scanner = sane.get_devices()
        return [s[0] for s in scanner]

    def scan(self, doc: Document, upload = False, creds: Credentials = None, url: str = None):
        """
        Perform a scan using the initialized printer device.
        This is a placeholder for actual implementation.
        """
        if not self.device:
            notify(f'No printer device found')
            return

        # Example of scanning logic (to be replaced with actual scanning code)
        notify(f"Scanning with {self.device.sane_signature[2]}...")
        # Here you would add the actual scanning logic
        # For example, self.device.scan() or similar method call
        scan_thread = ScanThread(self, doc, upload, creds, url)
        self.running_scans.append(scan_thread)
        scan_thread.start()

    @property
    def is_scanning(self) -> bool:
        """
        Check if there are any scans currently running.
        """
        return len(self.running_scans) > 0

    def set_scanning_event(self):
        """
        Set the scanning event to control the scanning process.
        """
        if len(self.running_scans) > 0:
            self.scanning_event.set()
        else:
            self.scanning_event.clear()

class ScanThread(Thread):
    def __init__(self, scanner: Scanner, doc: Document, upload: bool, creds: Credentials = None, url: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True  # Ensure the thread doesn't block program exit
        self.scanner = scanner
        self.document = doc
        self.upload = upload
        self.creds = creds
        self.url = url

    def run(self):
        notify("Starting scan...")
        scan_image = self.scanner.device.scan()
        current_scan = CurrentScan(scan_image)
        self.document.add_page(current_scan)
        notify("Scan completed and added to document.")
        self.scanner.running_scans.remove(self)
        if self.upload:
            upload_thread = UploadThread(self.document, self.creds, self.url, name="Upload", daemon=True)
            upload_thread.start()

        # current_scans.add_scan(self.scanner_device.scan())
        # scan_threads.remove(self)
        # notify(f"Scan completed. Total scans: {len(current_scans)}")

# class ScannerWatcher(Thread):
#     def __init__(self, scanner_selection, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.selection = scanner_selection
#         self.name = "ScannerWatcher"
#         self.kill_event = Event()
#         self.daemon = True  # Ensure the thread doesn't block program exit
#         self.last_seen = None
#
#     def run(self):
#         while not self.kill_event.is_set():
#             devices = Scanner.get_devices()
#             if devices != self.last_seen:
#                 print(f"Scanner devices changed: {devices}")
#                 self.selection.options = devices
#                 if self.last_seen is None:
#                     self.selection.value = devices[0] if devices else None
#                 self.selection.update()
#                 self.last_seen = devices
#                 notify(f"Scanner devices updated: {devices}")
#                 time.sleep(1)
#
