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

# Remove the old, unreliable systemd user service from earlier installs.
systemctl --user disable paperless-kiosk.service 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/paperless-kiosk.service"
systemctl --user daemon-reload 2>/dev/null || true

# Launch the Chromium kiosk from the desktop session via XDG autostart. The
# standard Raspberry Pi OS desktop runs lxsession-xdg-autostart, which starts
# entries in ~/.config/autostart on login.
chmod +x start-kiosk.sh
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/paperless-kiosk.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=rpi-paperless kiosk
Exec=$(pwd)/start-kiosk.sh
X-GNOME-Autostart-enabled=true
EOF

echo "Setup complete. Start the server with: sudo systemctl start paperless.service"
echo "The Chromium kiosk starts automatically with the desktop session (log in or reboot)."
