#!/bin/bash
# Wait for the rpi-paperless web server, then open it fullscreen in Chromium.
set -e

URL="http://localhost:8080"

# Raspberry Pi OS ships Chromium as `chromium-browser`; some images use `chromium`.
CHROMIUM="$(command -v chromium-browser || command -v chromium)"

# Block until the NiceGUI server is accepting connections on :8080.
until (exec 3<>/dev/tcp/localhost/8080) 2>/dev/null; do
    sleep 1
done
exec 3>&- 3<&-

exec "$CHROMIUM" \
    --kiosk \
    --ozone-platform=wayland \
    --noerrdialogs \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --check-for-update-interval=31536000 \
    "$URL"
