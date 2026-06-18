"""In-memory document made of scanned pages and PDF merging logic."""
from __future__ import annotations

import PIL.Image

from .utils import notify
from pypdf import PdfWriter

import os
from typing import List, Optional

class Document:
    """A collection of scanned pages that can be merged into a single PDF."""

    def __init__(self) -> None:
        """Initialise an empty document and ensure the merge output directory exists."""
        self.pages: List[CurrentScan] = []
        self.document_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "merges", )
        if not os.path.exists(self.document_path):
            os.makedirs(self.document_path)


    def merge(self) -> None:
        """Write each page to a temporary PDF, merge them into ``merged_scans.pdf``.

        The per-page temporary files are removed afterwards and the in-memory
        page list is cleared.
        """
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

    def add_page(self, current_scan: CurrentScan) -> None:
        """Append a scanned page to the document.

        :param current_scan: The scanned page to add.
        """
        self.pages.append(current_scan)
        notify(f"Added scan to document. Total pages: {len(self.pages)}")

    @property
    def number_of_pages(self) -> int:
        """Number of pages currently held in the document."""
        return len(self.pages)

    def clear(self) -> None:
        """Discard all pages from the document."""
        self.pages.clear()
        notify("Document cleared.")


class CurrentScan:
    """Wraps a single scanned page (a PIL image)."""

    def __init__(self, scan: PIL.Image.Image) -> None:
        """Store the scanned image.

        :param scan: The PIL image returned by the SANE device.
        """
        self.scan: Optional[PIL.Image.Image] = scan

    def clear(self) -> None:
        """Drop the reference to the scanned image."""
        self.scan = None

    def get_scans(self) -> Optional[PIL.Image.Image]:
        """Return the wrapped scanned image."""
        return self.scan

