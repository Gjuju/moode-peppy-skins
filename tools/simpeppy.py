# Emulates circular.set_sprite: bgr restored on previous rect (+4), needle drawn, fgr re-blitted on union.
import sys, math, random, glob, configparser
from PIL import Image, ImageChops
d = sys.argv[1]; c = configparser.ConfigParser(); c.read(glob.glob(f"{d}/*meters.txt")[0]); s = c[c.sections()[0]]
bgr = Image.open(f"{d}/" + s["bgr.filename"]).convert("RGBA"); fgr = Image.open(f"{d}/" + s["fgr.filename"]).convert("RGBA")
nd = Image.open(f"{d}/" + s["indicator.filename"]); dist = int(s["distance"])
a0, a1 = float(s["start.angle"]), float(s["stop.angle"]); ox, oy = int(s["left.origin.x"]), int(s["left.origin.y"])
def sprite(f):
    a = a0 + (a1 - a0) * f; r = nd.rotate(a, expand=True, resample=Image.BICUBIC); t = math.radians(a)
    cx, cy = ox - dist * math.sin(t), oy - dist * math.cos(t); x, y = int(cx - r.width / 2), int(cy - r.height / 2)
    return r, (x, y, x + r.width, y + r.height)
scr = bgr.copy(); scr.alpha_composite(fgr); random.seed(1); f = 0.0; prev = None
for i in range(600):
    f = min(1, max(0, f + random.uniform(-0.08, 0.08))); spr, rc = sprite(f)
    if prev:
        g = (prev[0] - 4, prev[1] - 4, prev[2] + 4, prev[3] + 4); scr.paste(bgr.crop(g), g[:2])
        u = (min(g[0], rc[0]), min(g[1], rc[1]), max(g[2], rc[2]), max(g[3], rc[3]))
    else: u = rc
    scr.alpha_composite(spr, rc[:2]); reg = scr.crop(u); reg.alpha_composite(fgr.crop(u)); scr.paste(reg, u[:2]); prev = rc
spr, rc = sprite(f); clean = bgr.copy(); clean.alpha_composite(spr, rc[:2]); clean.alpha_composite(fgr)
diff = ImageChops.difference(scr.convert("RGB"), clean.convert("RGB")).convert("L")
print("max diff", diff.getextrema()[1], "px >12:", sum(1 for v in diff.get_flattened_data() if v > 12))
