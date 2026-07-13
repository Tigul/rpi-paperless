# rpi-paperless

A lightweight touch-screen interface for a Raspberry Pi to control a document
scanner and upload the scans straight to a [Paperless-ngx](https://docs.paperless-ngx.com/)
instance.

The Pi runs a small [NiceGUI](https://nicegui.io/) web app (served on
`http://<pi>:8080`) that lets you scan one or more pages, merge them into a
single PDF and push them to Paperless with one tap — ideal for a Pi with a small
DSI display mounted next to the scanner.

## Features

- Scan pages from any [SANE](http://www.sane-project.org/)-supported scanner
- Combine multiple pages into a single PDF
- Upload directly to Paperless-ngx via its REST API
- Scan-and-upload in one action
- Settings panel for scanner selection, Paperless credentials, server URL and a
  fullscreen toggle
- Runs as a `systemd` service so it starts automatically on boot
- Opens automatically in a fullscreen Chromium kiosk on the Pi's display

## Hardware

- Raspberry Pi (any model that runs Raspberry Pi OS)
- A SANE-compatible scanner
- A small touch display — this project is built around the
  [Waveshare 4.3" DSI LCD](https://www.waveshare.com/4.3inch-dsi-lcd.htm)
- A 3D-printable stand for the display:
  **[Waveshare 4.3 inch DSI LCD Stand (Printables)](https://www.printables.com/model/480911-waveshare-43-inch-dsi-lcd-stand/files)**

## Installation

Clone the repository onto the Raspberry Pi and run the setup script:

```bash
git clone https://github.com/Tigul/rpi-paperless.git
cd rpi-paperless
./setup.sh
```

> **Run `setup.sh` from a terminal on the Pi's desktop**, not a bare SSH shell —
> it enables a *user* systemd service (`systemctl --user`), which needs your
> graphical login session's bus to be present.

`setup.sh` will:

1. Install the `libsane-dev` and `chromium-browser` system dependencies
2. Create a `paperless-venv` virtual environment
3. Install the Python dependencies and the `rpi_paperless` package itself
4. Symlink `rpi-paperless.service` into `/etc/systemd/system/paperless.service`,
   reload systemd and enable the service on boot
5. Enable the `paperless-kiosk` **user** service, which launches Chromium
   fullscreen against `http://localhost:8080` when the desktop session starts

> **Note:** Both unit files assume the project lives at `/home/pi/rpi-paperless`
> and run as the `pi` user. If you use a different path or user, edit
> `rpi-paperless.service` (the `User`, `WorkingDirectory` and `ExecStart` lines)
> and the `ExecStart` line of `paperless-kiosk.service` before running
> `setup.sh`.

### Start the service

```bash
sudo systemctl start paperless.service
sudo systemctl status paperless.service   # check it is running
```

The interface is then available at `http://<raspberry-pi-ip>:8080`.

### The kiosk display

When the desktop session starts (log in or reboot), the `paperless-kiosk` user
service launches Chromium fullscreen against `http://localhost:8080`. It waits
for the server to come up first, so a few seconds' delay on boot is normal.

```bash
systemctl --user status paperless-kiosk.service   # check it is running
systemctl --user restart paperless-kiosk.service  # relaunch the browser
```

If Chromium does not appear on boot, confirm your desktop session reaches
`graphical-session.target` (the Raspberry Pi OS Bookworm default). As a fallback
you can launch the kiosk from your compositor's autostart instead, e.g. a
`~/.config/autostart/paperless-kiosk.desktop` entry or a wayfire/labwc autostart
line that runs `start-kiosk.sh`.

### Running manually (for development)

```bash
source paperless-venv/bin/activate
python start.py
```

## Usage

1. Open the web interface on the Pi's display (or any device on the network).
2. In **Settings**, pick your scanner, enter your Paperless URL and your
   Paperless username/password, then submit. Tick *Save* to keep them across
   restarts.
3. Use **Scan** to add pages, **Upload** to send the collected pages, or
   **Scan and Upload** to do both at once.

Saved settings are stored next to the code in `config/` and `credentials/`;
merged PDFs are written to `merges/`.

## License

LGPL-3.0-only. See [LICENSE](LICENSE).
