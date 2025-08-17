#!/bin/bash

sudo apt install libsane-dev
python3 -m venv paperless-venv
source paperless-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

ln -s rpi-paperless.service /etc/systemd/system/paperless.service


