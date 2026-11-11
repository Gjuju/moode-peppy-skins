#!/bin/bash
# Install the skins into moOde's Peppy folders. Select them in the WebUI afterwards.
set -e
cd "$(dirname "$0")"
sudo tar --no-same-owner -xzf peppymeter-1920x1280.tar.gz    -C /opt/peppymeter/
sudo tar --no-same-owner -xzf peppymeter-v5-1920x1280.tar.gz -C /opt/peppymeter/
sudo tar --no-same-owner -xzf peppyspectrum-1920x1280.tar.gz -C /opt/peppyspectrum/
# round-red, adv-silver and adv-black join the v5 set: each section is (re)merged into the
# meters.txt the v5 tarball ships (the section runs up to the next [header] or the end of file)
M=/opt/peppymeter/1920x1280-moode
for m in round-red adv-silver adv-black; do
    sudo tar --no-same-owner -xzf "peppymeter-$m-1920x1280.tar.gz" -C /opt/peppymeter/
    sudo sed -i "/^\[$m\]/,/^\[/{/^\[$m\]/d;/^\[/!d}" "$M/meters.txt"
    sudo sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$M/meters.txt"
    { echo; cat "$M/$m.meters.txt"; } | sudo tee -a "$M/meters.txt" >/dev/null
    sudo rm "$M/$m.meters.txt"
done
echo "Installed: /opt/peppymeter/1920x1280, /opt/peppymeter/1920x1280-moode, /opt/peppyspectrum/1920x1280"
