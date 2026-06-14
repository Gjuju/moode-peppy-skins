# moOde Peppy skins — 1920×1280 (for moOdeX86)

Peppy **Meter** and **Spectrum** skins scaled to **1920×1280** for
[moOdeX86](https://github.com/Gjuju/moodeX86) local displays, plus the small
generators that produce them.

The skins are **4× LANCZOS upscales** of moOde's stock **480×320** Peppy skins:
every image is resized ×4 and every pixel coordinate in `meters.txt` /
`spectrum.txt` is scaled ×4 to match, so the layout stays correct on a
1920×1280 panel.

## Contents

| File | What |
|---|---|
| `peppymeter-1920x1280.tar.gz` | Peppy **Meter** skin — extract into `/opt/peppymeter/` |
| `peppyspectrum-1920x1280.tar.gz` | Peppy **Spectrum** skin — extract into `/opt/peppyspectrum/` |
| `mkskin-1920x1280.py` | regenerate the Meter skin from `/opt/peppymeter/480x320` |
| `mkspec-1920x1280.py` | regenerate the Spectrum skin from `/opt/peppyspectrum/480x320` |

Each tarball contains a top-level `1920x1280/` folder.

## Install (on a moOdeX86 box)

```bash
sudo tar xzf peppymeter-1920x1280.tar.gz    -C /opt/peppymeter/
sudo tar xzf peppyspectrum-1920x1280.tar.gz -C /opt/peppyspectrum/
```

Then in moOde, point the config at the new skin:
- `/etc/peppymeter/config.txt`: `meter.folder = 1920x1280`, `screen.width = 1920`, `screen.height = 1280`
- `/etc/peppyspectrum/config.txt`: `spectrum.folder = 1920x1280`

(Restart the local display afterwards.)

## Regenerate

Needs `python3-pil` and the stock `480x320` skins present under `/opt/peppy*/`.

```bash
python3 mkskin-1920x1280.py    # /opt/peppymeter/480x320   -> /opt/peppymeter/1920x1280
python3 mkspec-1920x1280.py    # /opt/peppyspectrum/480x320 -> /opt/peppyspectrum/1920x1280
```

The generators scale the pixel keys (`*.x`, `*.y`, bar/topping/reflection sizes,
etc.) by the same ×4 factor so the skin geometry matches the upscaled images.
