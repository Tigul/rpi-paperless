#!/bin/bash
set -e

sudo apt install -y libsane-dev
python3 -m venv paperless-venv
source paperless-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Install the rpi_paperless package itself so `import rpi_paperless` works.
pip install -e .

sudo ln -sf "$(pwd)/rpi-paperless.service" /etc/systemd/system/paperless.service
sudo systemctl daemon-reload
sudo systemctl enable paperless.service
echo "Setup complete. Start the service with: sudo systemctl start paperless.service"
