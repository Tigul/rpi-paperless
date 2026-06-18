"""SANE scanner wrapper and the background thread that performs scans.

:class:`Scanner` wraps a single SANE device; :class:`ScanThread` runs an
individual scan off the UI thread and optionally triggers an upload afterwards.
``sane.init()`` must have been called before any of this is used.
"""
from __future__ import annotations

import time
from threading import Thread, Event
from typing import List, Optional

from .credentials import Credentials
from .document import CurrentScan, Document
from .upload import UploadThread
from .utils import notify

import sane

class Scanner:
    """Wraps a single SANE scanner device and tracks its in-flight scans."""

    def __init__(self, scanner_device: str) -> None:
        """Open the given SANE device.

        :param scanner_device: SANE device name (as returned by
            :meth:`get_devices`). If falsy, no device is opened and the scanner
            stays inert; :meth:`scan` will report that no device is available.
        """
        self.device: Optional[sane.SaneDev] = None
        self.device_name: str = scanner_device
        self.running_scans: List[ScanThread] = []
        self.scanning_event: Event = Event()
        self.scanning_event.clear()
        if not scanner_device:
            notify("No scanner device provided.")
            return
        print(f"Initializing scanner device: {scanner_device}")
        self.device = sane.open(scanner_device)

    @classmethod
    def get_devices(cls) -> List[str]:
        """Return the names of all SANE scanner devices currently available."""
        scanner = sane.get_devices()
        return [s[0] for s in scanner]

    def scan(self, doc: Document, upload: bool = False, creds: Optional[Credentials] = None, url: Optional[str] = None) -> None:
        """Start scanning a single page in a background thread.

        The scan runs in a :class:`ScanThread` so the UI stays responsive; the
        resulting page is appended to ``doc`` when it finishes.

        :param doc: Document the scanned page is appended to.
        :param upload: If True, upload ``doc`` once the scan completes.
        :param creds: Credentials used for the upload.
        :param url: Paperless base URL used for the upload.
        """
        if not self.device:
            notify(f'No printer device found')
            return

        notify(f"Scanning with {self.device.sane_signature[2]}...")
        scan_thread = ScanThread(self, doc, upload, creds, url)
        self.running_scans.append(scan_thread)
        scan_thread.start()

    def close(self) -> None:
        """Close the underlying SANE device if one is open."""
        if self.device:
            self.device.close()
            self.device = None

    @property
    def is_scanning(self) -> bool:
        """True while at least one scan thread is still running."""
        return len(self.running_scans) > 0

    def set_scanning_event(self) -> None:
        """Set the scanning event while scans are running, clear it otherwise."""
        if len(self.running_scans) > 0:
            self.scanning_event.set()
        else:
            self.scanning_event.clear()

class ScanThread(Thread):
    """Performs a single scan off the UI thread and optionally uploads after."""

    def __init__(self, scanner: Scanner, doc: Document, upload: bool, creds: Optional[Credentials] = None, url: Optional[str] = None, *args, **kwargs) -> None:
        """Configure the scan thread.

        :param scanner: Scanner whose device is used for the scan.
        :param doc: Document the scanned page is appended to.
        :param upload: If True, upload ``doc`` once the scan completes.
        :param creds: Credentials used for the upload.
        :param url: Paperless base URL used for the upload.
        """
        super().__init__(*args, **kwargs)
        self.daemon = True  # Ensure the thread doesn't block program exit
        self.scanner: Scanner = scanner
        self.document: Document = doc
        self.upload: bool = upload
        self.creds: Optional[Credentials] = creds
        self.url: Optional[str] = url

    def run(self) -> None:
        """Scan one page, append it to the document and start the upload if requested."""
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
