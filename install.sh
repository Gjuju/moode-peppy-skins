#!/bin/bash
# Install the skins into moOde's Peppy folders. Select them in the WebUI afterwards.
set -e
cd "$(dirname "$0")"
sudo tar --no-same-owner -xzf peppymeter-1920x1280.tar.gz    -C /opt/peppymeter/
sudo tar --no-same-owner -xzf peppymeter-v5-1920x1280.tar.gz -C /opt/peppymeter/
sudo tar --no-same-owner -xzf peppyspectrum-1920x1280.tar.gz -C /opt/peppyspectrum/
echo "Installed: /opt/peppymeter/1920x1280, /opt/peppymeter/1920x1280-moode, /opt/peppyspectrum/1920x1280"
