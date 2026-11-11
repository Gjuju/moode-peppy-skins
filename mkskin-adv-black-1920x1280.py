#!/usr/bin/env python3
"""Generate the 'adv-black' PeppyMeter skin for a 1920x1280 screen.

Deep black faceplate with two dark meter windows: blue backlit dual scales
(outer row 0..100 %, inner row dBFS at their true positions) and red needles
rising from a pivot hidden under the faceplate; below, a power button, a
anodised anthracite knob and a small fluorescent-style display where PeppyMeter draws the
volume readout (volume.text.*).

Marks are true with volume.curve = 0: the needle angle is linear in the level,
so x % sits at f = x/100 and N dBFS at f = 10**(N/20).

The foreground (faceplate with the meter windows and the display cut out) only
has fully opaque or fully transparent pixels away from the cut edges:
PeppyMeter re-blits fgr over areas whose bgr it did not restore, so translucent
fgr pixels pile up. Glows and reflections are baked into bgr.

usage: mkskin-adv-black-1920x1280.py <v5 red-screen-bgr.png (moOde logo source)> <out-dir> [DSEG7 .ttf]

The readout uses DSEG7 Classic (SIL OFL 1.1, fonts-dseg), copied next to the images.
"""
import math, os, shutil, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

LOGO_SRC, OUT = sys.argv[1], sys.argv[2]
DSEG = sys.argv[3] if len(sys.argv) > 3 else "/usr/share/fonts/truetype/dseg/DSEG7Classic-Regular.ttf"
NAME = "adv-black"
W, H, S = 1920, 1280, 2                         # screen, supersampling
WINS = ((60, 200, 920, 640), (1000, 200, 1860, 640))
WIN_R = 6
CXS, PY = (490, 1430), 775                      # meter centres, pivot y (under the faceplate)
SPAN = 39                                       # start.angle = +SPAN, stop.angle = -SPAN
R_OUT, R_MAJ, R_MIN, R_LAB = 510, 425, 456, 540 # outer % row
R_DB_OUT, R_DB_IN, R_DB_LAB = 367, 251, 394
ELL = 1.6                                      # scale arcs: ellipse width/height (1 = circles)     # inner dBFS row
NEEDLE_IN, NEEDLE_OUT, NEEDLE_W = 120, 485, 14
KNOB = (960, 960, 205)
POWER = (185, 960, 52)
DISP = (1405, 901, 1655, 1019)                  # volume display window: 3 digit cells + margin
VOL_SIZE = 84
BADGE = (820, 100, 280)                          # engraved moOde: left x, centre y, width

BLACK_TOP, BLACK_BOT = (16, 16, 18), (6, 6, 7)
WIN_COL = (18, 19, 22)
GLOW, CORE, TXT = (20, 100, 255), (130, 200, 255), (80, 170, 255)
DISP_BG, DISP_DOT = (8, 11, 22), (16, 22, 40)

def font(size, bold=True):
    f = "/usr/share/fonts/truetype/lato/" + ("Lato-Bold.ttf" if bold else "Lato-Regular.ttf")
    return ImageFont.truetype(f if os.path.exists(f) else "DejaVuSans.ttf", size * S)

def sc(*v): return [x * S for x in v]

def ang(f): return math.radians(SPAN - 2 * SPAN * f)        # 0 = up, + = left

def pt(cx, r, f):
    """Point on a scale arc: same angle as the needle, radius stretched towards the ends (flat dial)."""
    a = ang(f)
    r = r / math.hypot(math.sin(a) / ELL, math.cos(a))
    return ((cx - r * math.sin(a)) * S, (PY - r * math.cos(a)) * S)

def logo_mask(width):
    """moOde logo from a v5 red-screen-bgr.png, as a full-contrast L mask of the given width."""
    src = Image.open(LOGO_SRC).convert("L")
    logo = src.crop(src.point(lambda v: 255 if v > 30 else 0).getbbox())
    lo, hi = logo.getextrema()
    logo = logo.point(lambda v: min(255, max(0, (v - lo) * 255 // max(1, hi - lo))))
    return logo.resize((width, round(logo.height * width / logo.width)), Image.LANCZOS)

# ---------------------------------------------------------------- faceplate
def black_plate():
    y = np.linspace(0, 1, H * S, dtype=np.float32)[:, None]
    top, bot = np.array(BLACK_TOP, np.float32), np.array(BLACK_BOT, np.float32)
    rgb = top + (bot - top) * y[..., None]
    rng = np.random.default_rng(5)
    rgb = rgb + rng.normal(0, 0.6, (H * S, W * S, 1)).astype(np.float32)
    rgb = np.broadcast_to(rgb, (H * S, W * S, 3))
    img = Image.fromarray(rgb.clip(0, 255).astype(np.uint8))
    return img

def silver_disc(n, seed, base=0.30, sheen=0.06):
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n / 2
    th = np.arctan2(yy, xx)
    rr = np.hypot(xx, yy) / (n / 2)
    v = base + sheen * np.cos(2 * (th + 0.6)) + 0.05 * np.cos(6 * th) - 0.06 * rr
    rng = np.random.default_rng(seed)
    noise = np.asarray(Image.fromarray(rng.normal(128, 40, (n // 4, n // 4)).clip(0, 255).astype(np.uint8))
                       .resize((n, n), Image.BICUBIC), dtype=np.float32) / 128 - 1
    v = v + 0.02 * noise
    disc = Image.fromarray((np.stack([v * 0.97, v * 0.99, v * 1.05], -1).clip(0, 1) * 255).astype(np.uint8))   # anodised anthracite
    m = Image.new("L", (n, n), 0); ImageDraw.Draw(m).ellipse([0, 0, n - 1, n - 1], fill=255)
    return disc, m

def knob(img):
    cx, cy, r = KNOB
    d = ImageDraw.Draw(img)
    d.ellipse(sc(cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14), fill=(2, 2, 3))
    disc, m = silver_disc(2 * r * S, 3, base=0.20, sheen=0.045)
    img.paste(disc, ((cx - r) * S, (cy - r) * S), m)
    ri = int(r * 0.66)                                  # inner cap, a step below the rim
    d.ellipse(sc(cx - ri - 6, cy - ri - 6, cx + ri + 6, cy + ri + 6), fill=(20, 21, 24))
    disc, m = silver_disc(2 * ri * S, 4, base=0.16, sheen=0.035)
    img.paste(disc, ((cx - ri) * S, (cy - ri) * S), m)

def power(img):
    cx, cy, r = POWER
    d = ImageDraw.Draw(img)
    d.ellipse(sc(cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), fill=(2, 2, 3))
    disc, m = silver_disc(2 * r * S, 6, base=0.21, sheen=0.045)
    img.paste(disc, ((cx - r) * S, (cy - r) * S), m)
    ri = int(r * 0.62)
    disc, m = silver_disc(2 * ri * S, 7, base=0.15, sheen=0.03)
    img.paste(disc, ((cx - ri) * S, (cy - ri) * S), m)
    # power symbol under the button
    sy, rr = cy + r + 50, 15
    d.arc(sc(cx - rr, sy - rr, cx + rr, sy + rr), 300, 240, fill=(150, 150, 156), width=3 * S)
    d.line(sc(cx, sy - rr - 4, cx, sy - 2), fill=(150, 150, 156), width=3 * S)

def faceplate():
    img = black_plate()
    d = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in WINS + (DISP,):           # thin dark recess around each window
        d.rounded_rectangle(sc(x0 - 4, y0 - 4, x1 + 4, y1 + 4), radius=(WIN_R + 4) * S, fill=(3, 3, 4))
    knob(img); power(img)
    badge = logo_mask(BADGE[2] * S).filter(ImageFilter.MaxFilter(5))
    img.paste((150, 152, 158), (BADGE[0] * S, BADGE[1] * S - badge.height // 2), badge)
    return img

def cut_mask():
    m = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(m)
    for box in WINS + (DISP,):
        d.rounded_rectangle(sc(*box), radius=WIN_R * S, fill=255)
    return m

# ---------------------------------------------------------------- windows
def windows():
    g = Image.new("RGB", (W * S, H * S), WIN_COL)
    glow = Image.new("RGB", g.size, (0, 0, 0)); gd = ImageDraw.Draw(glow)
    core = Image.new("RGB", g.size, (0, 0, 0)); cd = ImageDraw.Draw(core)
    def both(fn):
        fn(gd, GLOW, True); fn(cd, CORE, False)
    for cx in CXS:
        # outer row: 0..100 %, evenly spaced
        for i in range(21):
            f = i / 20
            major = i % 2 == 0
            seg = [pt(cx, R_MAJ if major else R_MIN, f), pt(cx, R_OUT, f)]
            gd.line(seg, fill=GLOW, width=(12 if major else 8) * S)
            cd.line(seg, fill=CORE, width=(5 if major else 3) * S)
            if major:
                for dd, col in ((gd, GLOW), (cd, TXT)):
                    dd.text(pt(cx, R_LAB, f), str(i * 5), font=font(30), fill=col, anchor="mm")
        # inner row: dBFS at their true positions
        for db in (None, -20, -12, -9, -6, -3, 0):
            f = 0.0 if db is None else 10 ** (db / 20)
            seg = [pt(cx, R_DB_IN, f), pt(cx, R_DB_OUT, f)]
            gd.line(seg, fill=GLOW, width=11 * S)
            cd.line(seg, fill=CORE, width=5 * S)
            lab = "-∞" if db is None else ("0" if db == 0 else str(db))
            for dd, col in ((gd, GLOW), (cd, TXT)):
                dd.text(pt(cx, R_DB_LAB, f), lab, font=font(27), fill=col, anchor="mm")
        for dd, col in ((gd, GLOW), (cd, TXT)):
            dd.text((cx * S, (WINS[0][3] - 40) * S), "dBFS / %", font=font(32), fill=col, anchor="mm")
    g = ImageChops.add(g, glow.filter(ImageFilter.GaussianBlur(12 * S)))
    g = ImageChops.add(g, glow.filter(ImageFilter.GaussianBlur(3 * S)))
    g = ImageChops.lighter(g, core)
    # volume display: dark navy with a faint dot matrix
    x0, y0, x1, y1 = DISP
    d = ImageDraw.Draw(g)
    d.rectangle(sc(x0, y0, x1, y1), fill=DISP_BG)
    for y in range(y0 + 8, y1 - 4, 7):
        for x in range(x0 + 8, x1 - 4, 7):
            d.ellipse(sc(x - 1.6, y - 1.6, x + 1.6, y + 1.6), fill=DISP_DOT)
    # soft reflection on the meter windows
    m = Image.new("L", g.size, 0); md = ImageDraw.Draw(m)
    for x0, y0, x1, y1 in WINS:
        md.polygon(sc(x0, y0, x0 + 300, y0, x0 + 120, y1, x0, y1), fill=12)
    g.paste((255, 255, 255), (0, 0), m.filter(ImageFilter.GaussianBlur(30 * S)))
    return g

# ---------------------------------------------------------------- needle
def needle():
    h = NEEDLE_OUT - NEEDLE_IN
    n = Image.new("RGBA", (NEEDLE_W * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(n)
    c = NEEDLE_W * S / 2
    d.polygon([(c - 2.6 * S, h * S), (c + 2.6 * S, h * S), (c + 1.1 * S, 0), (c - 1.1 * S, 0)], fill=(255, 46, 34, 255))
    out = Image.alpha_composite(n.filter(ImageFilter.GaussianBlur(3 * S)), n)
    return out.resize((NEEDLE_W, h), Image.LANCZOS)

# ---------------------------------------------------------------- readout placement
def readout_x():
    """Centre x of the 3 right-aligned DSEG cells: the display is sized to them."""
    return (DISP[0] + DISP[2]) // 2

# ---------------------------------------------------------------- build
plate = faceplate()
cut = cut_mask()
bgr = plate.copy(); bgr.paste(windows(), (0, 0), cut)
fgr = plate.convert("RGBA"); fgr.putalpha(ImageChops.invert(cut))
os.makedirs(OUT, exist_ok=True)
shutil.copy(DSEG, os.path.join(OUT, os.path.basename(DSEG)))
bgr.resize((W, H), Image.LANCZOS).save(f"{OUT}/{NAME}-bgr.png")
fgr.resize((W, H), Image.LANCZOS).save(f"{OUT}/{NAME}-fgr.png")
needle().save(f"{OUT}/{NAME}-needle.png")
with open(f"{OUT}/{NAME}.meters.txt", "w") as f:
    f.write(f"""[{NAME}]
meter.type = circular
channels = 2
ui.refresh.period = 0.033
bgr.filename = {NAME}-bgr.png
fgr.filename = {NAME}-fgr.png
indicator.filename = {NAME}-needle.png
steps.per.degree = 2
start.angle = {SPAN}
stop.angle = {-SPAN}
distance = {NEEDLE_IN + (NEEDLE_OUT - NEEDLE_IN) // 2}
left.origin.x = {CXS[0]}
left.origin.y = {PY}
right.origin.x = {CXS[1]}
right.origin.y = {PY}
meter.x = 0
meter.y = 0
screen.bgr = {NAME}-bgr.png
volume.text.x = {readout_x()}
volume.text.y = {(DISP[1] + DISP[3]) // 2}
volume.text.size = {VOL_SIZE}
volume.text.color = {CORE[0]},{CORE[1]},{CORE[2]}
volume.text.font = {os.path.basename(DSEG)}
volume.text.format = {{:!>3.0f}}
volume.text.format.text = {{:!>3}}
""")
print("done", OUT)
