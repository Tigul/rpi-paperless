#!/bin/bash
set -e

sudo apt install -y libsane-dev chromium-browser
python3 -m venv paperless-venv
source paperless-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Install the rpi_paperless package itself so `import rpi_paperless` works.
pip install -e .

sudo ln -sf "$(pwd)/rpi-paperless.service" /etc/systemd/system/paperless.service
sudo systemctl daemon-reload
sudo systemctl enable paperless.service

# Install the Chromium kiosk as a per-user service so it runs inside the Pi's
# graphical (Wayland) session. Note: `systemctl --user`, no sudo.
chmod +x start-kiosk.sh
mkdir -p "$HOME/.config/systemd/user"
ln -sf "$(pwd)/paperless-kiosk.service" "$HOME/.config/systemd/user/paperless-kiosk.service"
systemctl --user daemon-reload
systemctl --user enable paperless-kiosk.service

echo "Setup complete. Start the server with: sudo systemctl start paperless.service"
echo "The Chromium kiosk starts automatically with the desktop session (log in or reboot)."
