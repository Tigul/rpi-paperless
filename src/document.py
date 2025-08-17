from __future__ import annotations

import PIL

from .utils import notify
from pypdf import PdfWriter

import os

class Document:
    def __init__(self):
        self.pages = []

    def merge(self):
        filenames = []
        notify("Merging scans into a single PDF...")
        for i, scan in enumerate(self.pages):
            filename = f'scan_{i}.pdf'
            scan.scan.save(filename)
            filenames.append(filename)

        merger = PdfWriter()
        for pdf in filenames:
            merger.append(pdf)
        merger.write("merged_scans.pdf")
        for file in filenames:
            os.remove(file)
        notify(f"Merged {len(self.pages)} scans into merged_scans.pdf")
        self.pages.clear()

    def add_page(self, current_scan: CurrentScan):
        self.pages.append(current_scan)
        notify(f"Added scan to document. Total pages: {len(self.pages)}")

    @property
    def number_of_pages(self):
        return len(self.pages)

    def clear(self):
        self.pages.clear()
        notify("Document cleared.")


class CurrentScan:
    def __init__(self, scan):
        self.scan = scan

    def clear(self):
        self.scan = None

    def get_scans(self):
        return self.scan

