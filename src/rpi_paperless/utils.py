from nicegui import ui, Client

def notify(message: str) -> None:
    for client in Client.instances.values():
        if not client.has_socket_connection:
            continue
        with client:
            ui.notify(message)