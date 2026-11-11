# PeppyMeter-exact needle placement: distance = pivot to needle image CENTER
import sys, math, configparser, glob
from PIL import Image
d, fl, fr, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
c = configparser.ConfigParser(); c.read(glob.glob(f"{d}/*meters.txt")[0]); s = c[c.sections()[0]]
scr = Image.open(f"{d}/" + s["screen.bgr"]).convert("RGBA")
mx, my = int(s["meter.x"]), int(s["meter.y"])
scr.paste(Image.open(f"{d}/" + s["bgr.filename"]).convert("RGBA"), (mx, my))
nd = Image.open(f"{d}/" + s["indicator.filename"]); dist = int(s["distance"])
a0, a1 = float(s["start.angle"]), float(s["stop.angle"])
for side, f in (("left", fl), ("right", fr)):
    ox, oy = int(s[side + ".origin.x"]) + mx, int(s[side + ".origin.y"]) + my
    a = a0 + (a1 - a0) * f; r = nd.rotate(a, expand=True, resample=Image.BICUBIC); t = math.radians(a)
    cx, cy = ox - dist * math.sin(t), oy - dist * math.cos(t)
    scr.alpha_composite(r, (int(cx - r.width / 2), int(cy - r.height / 2)))
scr.alpha_composite(Image.open(f"{d}/" + s["fgr.filename"]).convert("RGBA"), (mx, my))
scr = scr.convert("RGB"); scr.save(out); scr.resize((scr.width // 2, scr.height // 2), Image.LANCZOS).save(out.replace(".png", "-small.png"))
