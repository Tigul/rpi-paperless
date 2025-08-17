from __future__ import annotations

import PIL

from .utils import notify
from pypdf import PdfWriter

import os

class Document:
    def __init__(self):
        self.pages = []
        self.document_path = os.path.join(os.path.dirname(__file__), "..", "..", "merges", )
        if not os.path.exists(self.document_path):
            os.makedirs(self.document_path)


    def merge(self):
        filenames = []
        notify("Merging scans into a single PDF...")
        for i, scan in enumerate(self.pages):
            filename = f'scan_{i}.pdf'
            filepath = os.path.join(self.document_path, filename)
            scan.scan.save(filepath)
            filenames.append(filepath)

        merger = PdfWriter()
        for pdf in filenames:
            merger.append(pdf)
        merged_path = os.path.join(self.document_path, "merged_scans.pdf")
        merger.write(merged_path)
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

