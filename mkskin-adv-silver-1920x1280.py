#!/usr/bin/env python3
"""Generate the 'adv-silver' PeppyMeter skin for a 1920x1280 screen.

Brushed-silver faceplate with a black glass window holding two blue backlit
fan meters and red needles rising from a pivot hidden under the faceplate.
Evenly spaced 0..100 % marks: with volume.curve = 0 the needle angle is linear
in the level, so even spacing is true.

The foreground (faceplate with the window cut out) only has fully opaque or
fully transparent pixels away from the window edge: PeppyMeter re-blits fgr
over areas whose bgr it did not restore, so translucent fgr pixels pile up.
Glows, glass reflection and shadows are baked into bgr.

usage: mkskin-adv-silver-1920x1280.py <v5 red-screen-bgr.png (moOde logo source)> <out-dir> [DSEG7 .ttf]

The volume readout uses DSEG7 Classic (SIL OFL 1.1, fonts-dseg), copied next to
the images.
"""
import math, os, shutil, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

LOGO_SRC, OUT = sys.argv[1], sys.argv[2]
DSEG = sys.argv[3] if len(sys.argv) > 3 else "/usr/share/fonts/truetype/dseg/DSEG7Classic-Regular.ttf"
NAME = "adv-silver"
W, H, S = 1920, 1280, 2                        # screen, supersampling
WIN = (60, 100, 1860, 600)                     # glass window
WIN_R = 16
CXS, PY = (440, 1480), 660                     # meter centres, pivot y (under the faceplate)
SPAN = 40                                      # start.angle = +SPAN, stop.angle = -SPAN
R_OUT, R_MAJ, R_MIN, R_LAB = 480, 330, 380, 520
NEEDLE_IN, NEEDLE_OUT, NEEDLE_W = 50, 440, 14
KNOB = (960, 940, 250)
POWER = (190, 1090, 66)
VOL_TEXT = (919, 508, 100)                     # bottom of the glass; 3 right-aligned cells of 82 px, 2 digits centred on the knob
VOL_FONT = os.path.basename(DSEG)
BADGE_W = 200                                  # faceplate moOde badge, mirrored from POWER

GLOW, CORE, TXT = (40, 90, 255), (150, 190, 255), (120, 165, 255)
GLASS_TOP, GLASS_BOT = (14, 16, 22), (4, 5, 8)

def font(size, bold=False):
    f = "/usr/share/fonts/truetype/lato/" + ("Lato-Semibold.ttf" if bold else "Lato-Regular.ttf")
    return ImageFont.truetype(f if os.path.exists(f) else "DejaVuSans.ttf", size * S)

def sc(*v): return [x * S for x in v]

def ang(f): return math.radians(SPAN - 2 * SPAN * f)       # 0 = up, + = left

def pt(cx, r, f):
    a = ang(f)
    return ((cx - r * math.sin(a)) * S, (PY - r * math.cos(a)) * S)

# ---------------------------------------------------------------- faceplate
def brushed(w, h, seed=7):
    rng = np.random.default_rng(seed)
    streak = rng.normal(0, 1, (h, max(8, w // 90)))
    streak = np.asarray(Image.fromarray(((streak + 4) * 32).clip(0, 255).astype(np.uint8))
                        .resize((w, h), Image.BICUBIC), dtype=np.float32) / 32 - 4
    fine = rng.normal(0, 1, (h, w)).astype(np.float32)
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    v = 0.80 - 0.10 * y + 0.035 * streak + 0.012 * fine
    rgb = np.stack([v * 0.975, v * 0.985, v * 1.0], axis=-1)
    return Image.fromarray((rgb.clip(0, 1) * 255).astype(np.uint8))

def logo_mask(width):
    """moOde logo from a v5 red-screen-bgr.png, as a full-contrast L mask of the given width."""
    src = Image.open(LOGO_SRC).convert("L")
    logo = src.crop(src.point(lambda v: 255 if v > 30 else 0).getbbox())
    lo, hi = logo.getextrema()
    logo = logo.point(lambda v: min(255, max(0, (v - lo) * 255 // max(1, hi - lo))))
    return logo.resize((width, round(logo.height * width / logo.width)), Image.LANCZOS)

def dome(d, cx, cy, r, light=230, dark=150):
    """Round silver push button: dark gap ring, radial-gradient cap, highlight."""
    d.ellipse(sc(cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=(70, 72, 76))
    for i in range(r, 0, -1):
        t = i / r
        g = int(dark + (light - dark) * (1 - t) ** 0.6)
        d.ellipse(sc(cx - i, cy - i, cx + i, cy + i), fill=(g, g, g + 3))
    d.ellipse(sc(cx - r * 0.55, cy - r * 0.75, cx + r * 0.15, cy - r * 0.2), fill=(245, 246, 250))

def knob(img):
    cx, cy, r = KNOB
    d = ImageDraw.Draw(img)
    d.ellipse(sc(cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22), fill=(58, 60, 64))
    d.ellipse(sc(cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), fill=(120, 122, 126))
    # spun-metal cap: angular sheen
    n = 2 * r * S
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n / 2
    th = np.arctan2(yy, xx)
    rr = np.hypot(xx, yy) / (n / 2)
    v = 0.70 + 0.16 * np.cos(2 * (th + 0.6)) + 0.05 * np.cos(6 * th) - 0.08 * rr
    rng = np.random.default_rng(3)
    v += 0.02 * np.asarray(Image.fromarray((rng.normal(128, 40, (n // 4, n // 4)).clip(0, 255)).astype(np.uint8))
                           .resize((n, n), Image.BICUBIC), dtype=np.float32) / 128 - 0.02
    cap = Image.fromarray((np.stack([v, v, v * 1.02], -1).clip(0, 1) * 255).astype(np.uint8))
    m = Image.new("L", (n, n), 0); ImageDraw.Draw(m).ellipse([0, 0, n - 1, n - 1], fill=255)
    img.paste(cap, ((cx - r) * S, (cy - r) * S), m)

def knob_glow(img):
    """Blue light ring on the left of the knob, baked in (opaque result)."""
    cx, cy, r = KNOB
    lay = Image.new("RGB", img.size, (0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.arc(sc(cx - r - 16, cy - r - 16, cx + r + 16, cy + r + 16), 140, 230, fill=GLOW, width=8 * S)
    glow = lay.filter(ImageFilter.GaussianBlur(10 * S))
    img = ImageChops.add(img, glow)
    img = ImageChops.add(img, ImageChops.multiply(lay, Image.new("RGB", img.size, (180, 200, 255))))
    return img

def faceplate():
    img = brushed(W * S, H * S)
    d = ImageDraw.Draw(img)
    # window recess: soft dark shadow ring around the glass
    x0, y0, x1, y1 = WIN
    sh = Image.new("L", img.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle(sc(x0 - 10, y0 - 10, x1 + 10, y1 + 14), radius=(WIN_R + 10) * S, fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(9 * S))
    img.paste((40, 42, 46), (0, 0), sh)
    d.rounded_rectangle(sc(x0 - 5, y0 - 5, x1 + 5, y1 + 5), radius=(WIN_R + 5) * S, fill=(52, 54, 58))
    d.rounded_rectangle(sc(x0 - 2, y0 - 2, x1 + 2, y1 + 2), radius=(WIN_R + 2) * S, fill=(20, 21, 24))
    dome(d, *POWER)
    badge = logo_mask(BADGE_W * S).filter(ImageFilter.MaxFilter(5))   # thicker engraved strokes
    bx, by = (W - POWER[0]) * S - badge.width // 2, POWER[1] * S - badge.height // 2
    img.paste((246, 247, 250), (bx, by + 2 * S), badge)        # engraving highlight
    img.paste((58, 60, 64), (bx, by), badge)
    knob(img)
    return knob_glow(img)

def window_mask():
    m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m).rounded_rectangle(sc(*WIN), radius=WIN_R * S, fill=255)
    return m

# ---------------------------------------------------------------- glass
def glass():
    x0, y0, x1, y1 = WIN
    g = Image.new("RGB", (W * S, H * S), GLASS_BOT)
    d = ImageDraw.Draw(g)
    for y in range(y0 * S, y1 * S, S):
        t = (y / S - y0) / (y1 - y0)
        c = tuple(int(GLASS_TOP[i] + (GLASS_BOT[i] - GLASS_TOP[i]) * t) for i in range(3))
        d.line([(x0 * S, y), (x1 * S, y)], fill=c, width=S)
    return g

def scales(g):
    glow = Image.new("RGB", g.size, (0, 0, 0)); gd = ImageDraw.Draw(glow)
    core = Image.new("RGB", g.size, (0, 0, 0)); cd = ImageDraw.Draw(core)
    for cx, label in zip(CXS, ("LEFT", "RIGHT")):
        for i in range(21):
            f = i / 20
            major = i % 2 == 0
            r_in = R_MAJ if major else R_MIN
            seg = [pt(cx, r_in, f), pt(cx, R_OUT, f)]
            gd.line(seg, fill=GLOW, width=(11 if major else 8) * S)
            cd.line(seg, fill=CORE, width=(5 if major else 3) * S)
            if major:
                x, y = pt(cx, R_LAB, f)
                for dd, col in ((gd, GLOW), (cd, TXT)):
                    dd.text((x, y), str(i * 5), font=font(30), fill=col, anchor="mm")
        arc = [pt(cx, R_MAJ - 22, k / 100) for k in range(101)]
        gd.line(arc, fill=GLOW, width=6 * S); cd.line(arc, fill=CORE, width=2 * S)
        for dd, col in ((gd, GLOW), (cd, TXT)):
            dd.text((cx * S, (PY - 200) * S), label + "  %", font=font(34, True), fill=col, anchor="mm")
    g = ImageChops.add(g, glow.filter(ImageFilter.GaussianBlur(14 * S)))
    g = ImageChops.add(g, glow.filter(ImageFilter.GaussianBlur(4 * S)))
    return ImageChops.lighter(g, core)

def reflection(g):
    x0, y0, x1, y1 = WIN
    m = Image.new("L", g.size, 0)
    ImageDraw.Draw(m).polygon(sc(x0, y0, x0 + 700, y0, x0 + 260, y1, x0, y1), fill=16)
    m = m.filter(ImageFilter.GaussianBlur(40 * S))
    g.paste((255, 255, 255), (0, 0), m)
    return g

# ---------------------------------------------------------------- needle
def needle():
    h = NEEDLE_OUT - NEEDLE_IN
    n = Image.new("RGBA", (NEEDLE_W * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(n)
    c = NEEDLE_W * S / 2
    d.polygon([(c - 3 * S, h * S), (c + 3 * S, h * S), (c + 1.2 * S, 0), (c - 1.2 * S, 0)], fill=(255, 50, 36, 255))
    glow = n.filter(ImageFilter.GaussianBlur(3 * S))
    out = Image.alpha_composite(glow, n)
    return out.resize((NEEDLE_W, h), Image.LANCZOS)

# ---------------------------------------------------------------- build
plate = faceplate()
win = window_mask()
g = reflection(scales(glass()))
bgr = plate.copy(); bgr.paste(g, (0, 0), win)
fgr = plate.convert("RGBA"); fgr.putalpha(ImageChops.invert(win))
os.makedirs(OUT, exist_ok=True)
shutil.copy(DSEG, os.path.join(OUT, VOL_FONT))
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
volume.text.x = {VOL_TEXT[0]}
volume.text.y = {VOL_TEXT[1]}
volume.text.size = {VOL_TEXT[2]}
volume.text.color = {TXT[0]},{TXT[1]},{TXT[2]}
volume.text.font = {VOL_FONT}
volume.text.format = {{:!>3.0f}}
volume.text.format.text = {{:!>3}}
""")
print("done", OUT)
