#!/usr/bin/env python3
import os, re, shutil
from PIL import Image
SRC, DST, F = "/opt/peppymeter/480x320", "/opt/peppymeter/1920x1280", 4
if os.path.isdir(DST): shutil.rmtree(DST)
os.makedirs(DST)
imgs = 0
for fn in os.listdir(SRC):
    p = os.path.join(SRC, fn)
    if fn.lower().endswith((".png",".jpg",".jpeg")):
        im = Image.open(p); im.resize((im.width*F, im.height*F), Image.LANCZOS).save(os.path.join(DST, fn)); imgs += 1
    elif os.path.isfile(p) and fn != "meters.txt":
        shutil.copy2(p, os.path.join(DST, fn))
def is_px(k): return k.endswith(".x") or k.endswith(".y") or k == "distance" or k.startswith("step.width")
out = []
for line in open(os.path.join(SRC,"meters.txt")):
    m = re.match(r"^(\s*)([\w.]+)(\s*=\s*)(-?\d+)\s*$", line)
    out.append(f"{m.group(1)}{m.group(2)}{m.group(3)}{int(m.group(4))*F}\n" if (m and is_px(m.group(2))) else line)
open(os.path.join(DST,"meters.txt"),"w").writelines(out)
print(f"scaled {imgs} imgs; meters.txt clean")
