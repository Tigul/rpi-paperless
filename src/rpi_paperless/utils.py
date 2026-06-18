"""Shared helpers for the rpi-paperless package."""
from nicegui import ui, Client

def notify(message: str) -> None:
    """Show a NiceGUI toast on every connected client.

    Safe to call from background threads: each connected client's context is
    entered explicitly so the notification is delivered to the right session.
    Clients without an active socket connection are skipped.

    :param message: The text to display.
    """
    for client in Client.instances.values():
        if not client.has_socket_connection:
            continue
        with client:
            ui.notify(message)