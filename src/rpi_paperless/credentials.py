import base64
import os

from .utils import notify


class Credentials:
    def __init__(self, username: str = None, password: str = None, save_credentials: bool = False):
        self.username = username
        self.password = password
        self.save_credentials = save_credentials
        self.credentials_path = os.path.join(os.path.dirname(__file__), "..", "..", "credentials", "credentials.txt")
        self.crete_directory()

        self.credentials_b64 = None
        self.load_credentials()

    def crete_directory(self):
        """
        Create necessary directories for storing credentials and other files.
        """
        if not os.path.exists(os.path.dirname(self.credentials_path)):
            os.makedirs(os.path.dirname(self.credentials_path))
            notify("Created directory for credentials.")
        else:
            print("Directory for credentials already exists.")

    def load_credentials(self):
        if os.path.exists(self.credentials_path):
            try:
                with open(self.credentials_path, 'r') as f:
                    self.credentials_b64 = f.read().strip()
                    notify(f"Credentials loaded from credentials.txt")
                    print("Loaded credentials:", self.credentials_b64)
            except FileNotFoundError:
                print("Credentials file not found. Please set your credentials.")


    def encode_credentials(self, username: str, password: str, save_credentials: bool):
        creds = f"{username}:{password}"
        base64_credentials = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
        if save_credentials:
            with open(self.credentials_path, 'w') as f:
                f.write(base64_credentials)
        self.credentials_b64 = base64_credentials
        notify("Credentials saved!" if save_credentials else "Credentials submitted!")

