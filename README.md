# moOde Peppy skins — 1920×1280

Peppy **Meter** and **Spectrum** skins scaled to **1920×1280** for any
[moOde audio player](https://github.com/moode-player/moode) install with a
1920×1280 local display (Raspberry Pi or x86), plus the small generators that
produce them.

The skins are **4× LANCZOS upscales** of moOde's stock **480×320** Peppy skins:
every image is resized ×4 and every pixel coordinate in `meters.txt` /
`spectrum.txt` is scaled ×4 to match, so the layout stays correct on a
1920×1280 panel.

## Contents

| File | What |
|---|---|
| `install.sh` | install everything below into `/opt/peppymeter/` and `/opt/peppyspectrum/` |
| `peppymeter-1920x1280.tar.gz` | Peppy **Meter** skin — extract into `/opt/peppymeter/` |
| `peppyspectrum-1920x1280.tar.gz` | Peppy **Spectrum** skin — extract into `/opt/peppyspectrum/` |
| `mkskin-1920x1280.py` | regenerate the Meter skin from `/opt/peppymeter/480x320` |
| `mkspec-1920x1280.py` | regenerate the Spectrum skin from `/opt/peppyspectrum/480x320` |
| `peppymeter-v5-1920x1280.tar.gz` | the 11 v5 moOde meters — see [below](#v5-moode-meters-19201280) |
| `mkskin-v5-1920x1280.py` | regenerate the v5 meters from the plugin's `1280x720-moode` folder |
| `peppymeter-round-red-1920x1280.tar.gz` | the **round-red** meter, added to the v5 set — see [below](#round-red-19201280) |
| `mkskin-round-red-1920x1280.py` | regenerate round-red |
| `peppymeter-adv-silver-1920x1280.tar.gz` | the **adv-silver** meter, added to the v5 set — see [below](#adv-silver-and-adv-black-19201280) |
| `peppymeter-adv-black-1920x1280.tar.gz` | the **adv-black** meter, added to the v5 set |
| `mkskin-adv-silver-1920x1280.py`, `mkskin-adv-black-1920x1280.py` | regenerate them |
| `fonts/` | DSEG7 Classic (SIL OFL 1.1) used by the adv-* volume readout |
| `tools/` | `preview.py` (needle placement exactly as PeppyMeter draws it), `simpeppy.py` (redraw simulation, shows fgr trails) |

The stock tarballs contain a top-level `1920x1280/` folder, the v5,
round-red and adv-* ones `1920x1280-moode/`.

## Install

```bash
git clone https://github.com/Gjuju/moode-peppy-skins.git
./moode-peppy-skins/install.sh
```

Manual install:

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

## v5 moOde meters (1920×1280)

`peppymeter-v5-1920x1280.tar.gz` holds the 11 meters of moOde's
[v5-moode-meters](https://github.com/moode-player/plugins/tree/main/peppydisplay/v5-moode-meters)
plugin (`1280x720-moode` set: black-white, blue, champagne, emerald, gold,
orange, pure-white, red, rust, tube, white-red), scaled for a 1920×1280 panel.

- Backgrounds/foregrounds: ×4 ESRGAN (**4x-UltraSharp**) then LANCZOS down to
  **×1.5**; alpha scaled with LANCZOS. Needles/indicators: LANCZOS ×1.5.
- 16:9 → 3:2: the meter is centred vertically (`meter.y += 100`) and each
  `*-screen-bgr.png` is extended 100 px top/bottom by repeating its edge rows.
- `meters.txt`: `distance`, `*.origin.x/y`, `meter.x/y` scaled ×1.5.

Install:

```bash
sudo tar xzf peppymeter-v5-1920x1280.tar.gz -C /opt/peppymeter/
```

then `meter.folder = 1920x1280-moode` and `meter = <name>` in
`/etc/peppymeter/config.txt`, and restart the local display.

Regenerate (needs `torch` (CPU is fine, ~3.5 min/meter), `spandrel`, `pillow`,
`numpy`, the extracted plugin zip and the `4x-UltraSharp.pth` model):

```bash
python3 mkskin-v5-1920x1280.py <zip>/update/files/1280x720-moode 1920x1280-moode \
    --model 4x-UltraSharp.pth
```

## round-red (1920×1280)

![round-red](round-red-preview.jpg)

`peppymeter-round-red-1920x1280.tar.gz` adds **round-red** to the
`1920x1280-moode` set: two round VU meters (black bezel melting into the black
screen, lower hill hiding the pivot) with the orange-to-yellow face of the v5
`red` meter. Drawn procedurally (no upscaling).

- Scale: −20…+3 VU over a voltage-linear arc, **0 VU = −3 dBFS** (+3 VU =
  digital full scale), with the 20…100 % row of a real VU meter.
- The marks are only true with **`volume.curve = 0`** (PeppyMeter's default)
  in `/etc/peppymeter/config.txt` (WebUI: Peppy config > meter curve). The curve
  is global, so it applies to every meter.
- The foreground holds only fully opaque/transparent pixels over the needle
  sweep: PeppyMeter re-blits `fgr` over areas whose `bgr` it did not restore,
  so a translucent foreground (glass, shadow) piles up into needle trails. Glass
  and inner shadow are baked into `bgr` instead.

Install: `install.sh` extracts it after the v5 set and (re)writes its section
in `/opt/peppymeter/1920x1280-moode/meters.txt`. Then `meter = round-red`
(`meter.folder = 1920x1280-moode`) and restart the local display.

Regenerate (needs `pillow` and the Lato font, `fonts-lato`):

```bash
python3 mkskin-round-red-1920x1280.py /opt/peppymeter/1280x720-moode/red-screen-bgr.png out/1920x1280-moode \
    [curve] [0VU-dBFS]          # defaults: 0, -3
```

## adv-silver and adv-black (1920×1280)

![adv-silver](adv-silver-preview.jpg)

![adv-black](adv-black-preview.jpg)

Two hi-fi amplifier fronts added to the `1920x1280-moode` set, drawn
procedurally (no brand, small engraved moOde badge):

- **adv-silver**: brushed silver faceplate, black glass window with two blue
  backlit 0…100 % scales and red needles, big knob and power button.
- **adv-black**: deep black faceplate, two meter windows with a flat dual scale
  (outer 0…100 %, inner dBFS at their true positions), anodised anthracite knob
  and power button, small display for the volume.

As for round-red, the marks are true with **`volume.curve = 0`**, and the
foreground has no translucent pixels over the needle sweep.

**Volume readout**: both skins carry `volume.text.*` keys for a volume readout
drawn in DSEG7 (shipped next to the images). It needs a PeppyMeter patch that
is not upstream yet
([project-owner/PeppyMeter#25](https://github.com/project-owner/PeppyMeter/issues/25))
plus `volume.text.source = <file>` in `/etc/peppymeter/config.txt` and a player
writing the volume into that file. Stock PeppyMeter ignores these keys: the
skins work, without the readout.

Install: `install.sh` extracts them after the v5 set and (re)writes their
sections in `/opt/peppymeter/1920x1280-moode/meters.txt`. Then
`meter = adv-silver` or `adv-black` (`meter.folder = 1920x1280-moode`) and
restart the local display.

Regenerate (needs `pillow`, `numpy`, the Lato font `fonts-lato`, and the v5
plugin's `red-screen-bgr.png` as the moOde logo source):

```bash
python3 mkskin-adv-silver-1920x1280.py /opt/peppymeter/1280x720-moode/red-screen-bgr.png out/1920x1280-moode fonts/DSEG7Classic-Regular.ttf
python3 mkskin-adv-black-1920x1280.py  /opt/peppymeter/1280x720-moode/red-screen-bgr.png out/1920x1280-moode fonts/DSEG7Classic-Regular.ttf
```
