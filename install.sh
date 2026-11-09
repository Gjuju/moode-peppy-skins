#!/bin/bash
# Install the skins into moOde's Peppy folders. Select them in the WebUI afterwards.
set -e
cd "$(dirname "$0")"
sudo tar --no-same-owner -xzf peppymeter-1920x1280.tar.gz    -C /opt/peppymeter/
sudo tar --no-same-owner -xzf peppymeter-v5-1920x1280.tar.gz -C /opt/peppymeter/
sudo tar --no-same-owner -xzf peppyspectrum-1920x1280.tar.gz -C /opt/peppyspectrum/
# round-red joins the v5 set: its section is merged into the meters.txt the v5 tarball ships
sudo tar --no-same-owner -xzf peppymeter-round-red-1920x1280.tar.gz -C /opt/peppymeter/
M=/opt/peppymeter/1920x1280-moode
sudo sed -i '/^\[round-red\]/,/^screen.bgr = round-red-screen-bgr.png/d' "$M/meters.txt"
sudo sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$M/meters.txt"
{ echo; cat "$M/round-red.meters.txt"; } | sudo tee -a "$M/meters.txt" >/dev/null
sudo rm "$M/round-red.meters.txt"
echo "Installed: /opt/peppymeter/1920x1280, /opt/peppymeter/1920x1280-moode, /opt/peppyspectrum/1920x1280"
