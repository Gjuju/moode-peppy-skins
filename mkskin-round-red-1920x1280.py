#!/usr/bin/env python3
"""Generate the 'round-red' PeppyMeter skin for a 1920x1280 screen.

Two round VU meters (black bezel, lower 'hill', reset button) with the
orange-to-yellow face of moOde's 'red' skin. Scale marks are placed for
PeppyMeter's needle mapping: level = peak amplitude in %, then
volume.curve (log1p(k*x)/log1p(k)), angle linear in that level.
0 VU is set at -3 dBFS by default: +3 VU = digital full scale.

usage: mkskin-round-red-1920x1280.py <red-screen-bgr.png> <out-dir> [curve] [0VU dBFS]

<red-screen-bgr.png> = any v5 red-screen-bgr.png, e.g. 1280x720-moode (source of the moOde logo).
Defaults (curve 0, 0 VU = -3 dBFS) match volume.curve = 0 in /etc/peppymeter/config.txt.
"""
import math, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

SRC_SCREEN, OUT = sys.argv[1], sys.argv[2]
CURVE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
NAME = "round-red"

W, H = 1920, 1280
S = 3                                  # supersampling
R = 440                                # bezel outer radius
CY = 500
CXS = (493, 1427)
RF = int(R * 0.87)                     # face (window) radius
PIV = int(R * 0.42)                    # pivot below meter center
RA = 360                               # scale arc radius from pivot
SPAN = 48                              # start.angle = +SPAN, stop.angle = -SPAN
STRIP_H = 960                          # height of the meter bgr/fgr strip
NEEDLE_DIST, NEEDLE_LEN, NEEDLE_W = 95, 305, 16

FACE_IN, FACE_OUT = (250, 196, 10), (240, 72, 24)   # sampled from red-bgr.png
INK, RED = (20, 12, 8), (226, 28, 22)

def font(size, bold=False):
    for f in (["Lato-Bold.ttf", "Lato-Semibold.ttf"] if bold else ["Lato-Medium.ttf", "Lato-Regular.ttf"]):
        for d in ("/usr/share/fonts/truetype/lato/",):
            if os.path.exists(d + f):
                return ImageFont.truetype(d + f, size * S)
    return ImageFont.truetype("DejaVuSans.ttf", size * S)

def frac_of_amp(a):                    # PeppyMeter level fraction for amplitude a (0..1)
    return math.log1p(CURVE * a) / math.log1p(CURVE) if CURVE > 0 else a

A0 = 10 ** (float(sys.argv[4] if len(sys.argv) > 4 else -3) / 20)                 # 0 VU amplitude
def frac_vu(db): return frac_of_amp(A0 * 10 ** (db / 20))
def frac_pct(p): return frac_of_amp(A0 * p / 100)

def ang(f): return math.radians(SPAN - 2 * SPAN * f)   # 0 = up, + = left

def pt(cx, py, r, f):
    a = ang(f)
    return ((cx - r * math.sin(a)) * S, (py - r * math.cos(a)) * S)

def hill_y(x, cx):                     # lower edge of the face window
    d = (x - cx) / (0.36 * R)
    return CY + 0.34 * R - 0.15 * R * math.exp(-d * d)

def window_mask(cx):
    m = Image.new("L", (W * S, STRIP_H * S), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([(cx - RF) * S, (CY - RF) * S, (cx + RF) * S, (CY + RF) * S], fill=255)
    poly = [(x * S, hill_y(x, cx) * S) for x in range(cx - R, cx + R + 1, 2)]
    poly += [((cx + R) * S, (CY + R) * S), ((cx - R) * S, (CY + R) * S)]
    d.polygon(poly, fill=0)
    return m

def radial(size, center, rmax, cin, cout):
    """Radial gradient image (RGB) of given size, supersampled coords."""
    small = Image.new("RGB", (size[0] // 8, size[1] // 8))
    px = small.load()
    for y in range(small.height):
        for x in range(small.width):
            t = min(1.0, math.hypot(x * 8 - center[0], y * 8 - center[1]) / rmax) ** 1.6
            px[x, y] = tuple(int(cin[i] + (cout[i] - cin[i]) * t) for i in range(3))
    return small.resize(size, Image.BICUBIC)

def arc(d, cx, py, r, f0, f1, width, fill):
    n = max(8, int((f1 - f0) * 200))
    pts = [pt(cx, py, r, f0 + (f1 - f0) * i / n) for i in range(n + 1)]
    d.line(pts, fill=fill, width=width * S, joint="curve")

def text_at(d, xy, s, fnt, fill):
    d.text(xy, s, font=fnt, fill=fill, anchor="mm")

def draw_face(img, d, cx, label):
    py = CY + PIV
    f0 = frac_vu(0)
    # main arc + red zone
    arc(d, cx, py, RA, frac_vu(-20) - 0.05, f0, 5, INK)
    arc(d, cx, py, RA, f0, 1.0, 5, RED)
    arc(d, cx, py, RA - 15, f0, 1.0, 22, RED)
    # dB marks
    fl, fs = font(42, True), font(28, True)
    for db in (-20, -10, -7, -5, -3, -2, -1, 0, 1, 2, 3):
        f = frac_vu(db)
        col = RED if db > 0 else INK
        d.line([pt(cx, py, RA - 2, f), pt(cx, py, RA + 30, f)], fill=col, width=5 * S)
        txt = str(abs(db)) if db != 0 else "0"
        text_at(d, pt(cx, py, RA + 62, f), txt, fl if abs(db) in (0, 3, 5, 10, 20) else fs, col)
    for db in (-15, -8, -6, -4):   # minor ticks
        f = frac_vu(db)
        d.line([pt(cx, py, RA, f), pt(cx, py, RA + 16, f)], fill=RED if db > 0 else INK, width=3 * S)
    # percent scale (of 0 VU) with dots
    fp = font(24)
    for p in (20, 40, 60, 80, 100):
        f = frac_pct(p)
        x, y = pt(cx, py, RA - 34, f)
        rr = 7 * S
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=INK)
        text_at(d, pt(cx, py, RA - 66, f), str(p), fp, INK)
    for p in (30, 50, 70, 90):
        x, y = pt(cx, py, RA - 34, frac_pct(p))
        rr = 4 * S
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=INK)
    # legends
    text_at(d, ((cx - 0.66 * R) * S, (CY + 0.06 * R) * S), "–", font(80, True), INK)
    text_at(d, ((cx + 0.70 * R) * S, (CY + 0.10 * R) * S), "+", font(80, True), RED)
    text_at(d, ((cx + 0.42 * R) * S, (CY + 0.14 * R) * S), "VU", font(96, True), INK)
    text_at(d, ((cx - 0.40 * R) * S, (CY + 0.16 * R) * S), label, font(34, True), INK)

def build_bgr():
    img = Image.new("RGB", (W * S, STRIP_H * S), (0, 0, 0))
    for cx, label in zip(CXS, ("LEFT", "RIGHT")):
        face = radial((2 * RF * S, 2 * RF * S), (RF * S, int(RF * 1.15) * S), RF * S * 1.05, FACE_IN, FACE_OUT)
        m = Image.new("L", face.size, 0)
        ImageDraw.Draw(m).ellipse([0, 0, face.width - 1, face.height - 1], fill=255)
        img.paste(face, ((cx - RF) * S, (CY - RF) * S), m)
        draw_face(img, ImageDraw.Draw(img), cx, label)
        # shadow + glass are baked here, not in fgr: PeppyMeter re-blits fgr over
        # areas whose bgr it did not restore, so translucent fgr pixels pile up
        win = window_mask(cx)
        sh = win.filter(ImageFilter.GaussianBlur(18 * S))
        sh = ImageChops.subtract(win, sh).point(lambda v: min(150, v * 2))
        img.paste((0, 0, 0), (0, 0), sh)
        gl = Image.new("L", img.size, 0)
        ImageDraw.Draw(gl).ellipse([(cx - RF * 0.95) * S, (CY - RF * 1.02) * S,
                                    (cx + RF * 0.55) * S, (CY - RF * 0.25) * S], fill=34)
        gl = ImageChops.multiply(gl.filter(ImageFilter.GaussianBlur(30 * S)), win)
        img.paste((255, 255, 240), (0, 0), gl)
    return img.resize((W, STRIP_H), Image.LANCZOS)

def build_fgr():
    out = Image.new("RGBA", (W * S, STRIP_H * S), (0, 0, 0, 0))
    for cx in CXS:
        win = window_mask(cx)
        # bezel body: vertical gradient, darker at the bottom
        body = Image.new("RGBA", (2 * R * S, 2 * R * S))
        bd = ImageDraw.Draw(body)
        for y in range(0, body.height, S):
            t = y / body.height
            g = int(16 - 10 * t)
            bd.line([(0, y), (body.width, y)], fill=(g, g, g + 1, 255), width=S)
        # radial fade: opaque around the face, fully transparent at the outer radius
        # (stays inside the 2R box, so no square edge), melts into the black screen
        bm = Image.new("L", (2 * R, 2 * R), 0)
        mp = bm.load()
        r0, r1 = RF + 22, R
        for y in range(2 * R):
            for x in range(2 * R):
                r = math.hypot(x - R + 0.5, y - R + 0.5)
                t = 1.0 if r <= r0 else max(0.0, 1 - (r - r0) / (r1 - r0))
                mp[x, y] = int(255 * t * t * (3 - 2 * t))
        bm = bm.resize(body.size, Image.BICUBIC)
        layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
        layer.paste(body, ((cx - R) * S, (CY - R) * S), bm)
        ld = ImageDraw.Draw(layer)
        # rim highlight + inner lip
        ld.ellipse([(cx - RF - 14) * S, (CY - RF - 14) * S, (cx + RF + 14) * S, (CY + RF + 14) * S],
                   outline=(8, 8, 8, 255), width=10 * S)
        # reset button
        bx, by, br = cx * S, (CY + PIV) * S, int(0.085 * R) * S   # button = needle pivot
        ld.ellipse([bx - br - 6 * S, by - br - 6 * S, bx + br + 6 * S, by + br + 6 * S], fill=(6, 6, 6, 255))
        ld.ellipse([bx - br, by - br, bx + br, by + br], fill=(26, 26, 28, 255))
        ld.ellipse([bx - br * 0.6, by - br * 0.8, bx + br * 0.2, by - br * 0.1], fill=(52, 52, 56, 255))
        # cut the window
        a = layer.getchannel("A")
        layer.putalpha(ImageChops.subtract(a, win))
        # hill top edge highlight
        edge = [(x * S, (hill_y(x, cx) + 3) * S) for x in range(cx - RF + 20, cx + RF - 19, 2)]
        ImageDraw.Draw(layer).line(edge, fill=(38, 38, 40, 255), width=3 * S)
        # screws inside the window bottom corners
        sd = ImageDraw.Draw(layer)
        for sx in (-1, 1):
            x = cx + sx * 0.70 * R
            y = hill_y(x, cx) - 26
            r = 13
            sd.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(150, 110, 40, 255), outline=(70, 50, 20, 255), width=2 * S)
            sd.line([((x - r * 0.7) * S, (y + r * 0.3) * S), ((x + r * 0.7) * S, (y - r * 0.3) * S)], fill=(70, 50, 20, 255), width=3 * S)
        out = Image.alpha_composite(out, layer)
    return out.resize((W, STRIP_H), Image.LANCZOS)

def build_needle():
    w, h = NEEDLE_W * S, NEEDLE_LEN * S
    n = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(n)
    c = w / 2
    d.polygon([(c - 3.5 * S, h), (c + 3.5 * S, h), (c + 1.5 * S, 0), (c - 1.5 * S, 0)], fill=(12, 8, 6, 255))
    return n.resize((NEEDLE_W, NEEDLE_LEN), Image.LANCZOS)

def build_screen():
    scr = Image.new("RGB", (W, H), (0, 0, 0))
    src = Image.open(SRC_SCREEN).convert("RGB")      # any v5 red-screen-bgr.png: logo on black
    logo = src.crop(src.convert("L").point(lambda v: 255 if v > 30 else 0).getbbox())
    logo = logo.resize((524, round(logo.height * 524 / logo.width)), Image.LANCZOS)
    scr.paste(logo, ((W - logo.width) // 2, 970))
    return scr

os.makedirs(OUT, exist_ok=True)
build_screen().save(f"{OUT}/{NAME}-screen-bgr.png")
build_bgr().save(f"{OUT}/{NAME}-bgr.png")
build_fgr().save(f"{OUT}/{NAME}-fgr.png")
build_needle().save(f"{OUT}/{NAME}-needle.png")
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
distance = {NEEDLE_DIST + NEEDLE_LEN // 2}
left.origin.x = {CXS[0]}
left.origin.y = {CY + PIV}
right.origin.x = {CXS[1]}
right.origin.y = {CY + PIV}
meter.x = 0
meter.y = 0
screen.bgr = {NAME}-screen-bgr.png
""")
print("done", OUT)
