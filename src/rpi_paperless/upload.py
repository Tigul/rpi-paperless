import os
from threading import Thread, Event

import httpx

from .credentials import Credentials
from .document import Document
from .utils import notify


class UploadThread(Thread):
    def __init__(self, doc: Document, creds: Credentials, url: str, name: str, daemon: bool = True, *args, **kwargs):
        """
        Initialize the UploadThread.

        :param doc: Document to be uploaded.
        :param scanning_event: Event if the scanner is currently scanning.
        :param creds: Credentials for authentication.
        :param url: Upload URL for the Paperless instance.
        :param name: Name of the thread.
        :param daemon: If True, the thread will exit when the main program exits.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(name=name, daemon=daemon, *args, **kwargs)
        self.daemon = True  # Ensure the thread doesn't block program exit
        self.doc = doc
        self.credentials = creds
        self.url = url
        self.document_path = os.path.join(os.path.dirname(__file__), "..", "..", "merges", "merged_scans.pdf")
        print("UploadThread initialized with URL:", self.url)

    def run(self):
        self.doc.merge()
        self.send_request()

    def send_request(self):
        """
        Send the request to upload the document to the Paperless instance.
        """
        url = f"{self.url}/api/documents/post_document/"
        if not self.credentials.credentials_b64:
            notify("Credentials are not set. Please set your credentials before uploading.")
            return
        try:
            notify(f"Uploading scans ...")
            resp = httpx.post(url + "/api/documents/post_document/",
                              headers={"Authorization": "Basic " + self.credentials.credentials_b64},
                              files={'document': ('scan.pdf', open(self.document_path, 'rb'), 'application/pdf')},
                              data={"title": "Scanned Document", "created": "2023-12-21"})
            print(resp.status_code)
            if resp.status_code == 200:
                notify(f"Uploaded successfully to {self.url}")
                self.doc.clear()
        except Exception as e:
            print(f"Failed to upload scans: {e}")
            notify(f"Failed to upload scans due to {e}")

