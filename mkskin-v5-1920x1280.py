#!/usr/bin/env python3
"""Scale moOde's v5 1280x720 Peppy meters to a 1920x1280 (3:2) screen.

Images are upscaled x4 with an ESRGAN model (spandrel) then reduced to x1.5
with LANCZOS; needles/indicators use plain LANCZOS. The 16:9 layout is centred
vertically (PAD px top/bottom): meter.y is offset by PAD and the screen
background is extended by repeating its edge rows.
"""
import argparse, os, re, shutil, sys, time
import numpy as np, torch
from PIL import Image
from spandrel import ModelLoader

F, PAD = 1.5, 100
SCREEN_W, SCREEN_H = 1920, 1280
TILE, OVL = 256, 16

def upscale4(model, rgb):
    """ESRGAN x4 on an RGB uint8 array, tiled."""
    h, w, _ = rgb.shape
    x = torch.from_numpy(rgb).permute(2, 0, 1).float().div(255).unsqueeze(0)
    out = torch.zeros(1, 3, h * 4, w * 4)
    with torch.inference_mode():
        for y0 in range(0, h, TILE):
            for x0 in range(0, w, TILE):
                ya, xa = max(y0 - OVL, 0), max(x0 - OVL, 0)
                yb, xb = min(y0 + TILE + OVL, h), min(x0 + TILE + OVL, w)
                t = model(x[:, :, ya:yb, xa:xb]).clamp(0, 1)
                th, tw = min(TILE, h - y0), min(TILE, w - x0)
                oy, ox = (y0 - ya) * 4, (x0 - xa) * 4
                out[:, :, y0*4:(y0+th)*4, x0*4:(x0+tw)*4] = t[:, :, oy:oy+th*4, ox:ox+tw*4]
    return (out[0].permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8)

def ai_scale(model, im):
    """x4 ESRGAN then LANCZOS down to x1.5; alpha scaled with LANCZOS only.
    Fully transparent margins are cropped first to save CPU time."""
    W, H = round(im.width * F), round(im.height * F)
    if im.mode != "RGBA":
        big = Image.fromarray(upscale4(model, np.asarray(im.convert("RGB"))))
        return big.resize((W, H), Image.LANCZOS)
    alpha = im.getchannel("A")
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bbox = alpha.getbbox()
    if not bbox:
        return out
    m = 4  # context margin around the crop
    l, t = max(bbox[0] - m, 0), max(bbox[1] - m, 0)
    r, b = min(bbox[2] + m, im.width), min(bbox[3] + m, im.height)
    crop = im.crop((l, t, r, b))
    rgb = Image.fromarray(upscale4(model, np.asarray(crop.convert("RGB"))))
    full_rgb = Image.new("RGB", (im.width * 4, im.height * 4))
    full_rgb.paste(rgb, (l * 4, t * 4))
    rgb = full_rgb.resize((W, H), Image.LANCZOS)
    a = alpha.resize((W, H), Image.LANCZOS)
    out = rgb.convert("RGBA"); out.putalpha(a)
    return out

def pad_screen(im):
    """Centre a 1920x1080 screen background on 1920x1280 by repeating edge rows."""
    arr = np.asarray(im)
    top = (SCREEN_H - arr.shape[0]) // 2
    bot = SCREEN_H - arr.shape[0] - top
    pads = ((top, bot), (0, 0)) + (((0, 0),) if arr.ndim == 3 else ())
    return Image.fromarray(np.pad(arr, pads, mode="edge"))

def scale_meters_txt(src, dst):
    px = re.compile(r"^(\s*)(distance|meter\.[xy]|(?:left|right|mono)\.origin\.[xy])(\s*=\s*)(-?\d+)\s*$")
    out = []
    for line in open(src):
        m = px.match(line)
        if m:
            v = round(int(m.group(4)) * F) + (PAD if m.group(2) == "meter.y" else 0)
            line = f"{m.group(1)}{m.group(2)}{m.group(3)}{v}\n"
        out.append(line)
    open(dst, "w").writelines(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="1280x720-moode folder")
    ap.add_argument("dst", help="output folder (recreated)")
    ap.add_argument("--model", required=True, help="x4 ESRGAN .pth (e.g. 4x-UltraSharp)")
    ap.add_argument("--only", help="comma-separated meter names to process")
    a = ap.parse_args()
    torch.set_num_threads(os.cpu_count())
    model = ModelLoader().load_from_file(a.model).eval().model
    if os.path.isdir(a.dst): shutil.rmtree(a.dst)
    os.makedirs(a.dst)
    only = a.only.split(",") if a.only else None
    for fn in sorted(os.listdir(a.src)):
        p, q = os.path.join(a.src, fn), os.path.join(a.dst, fn)
        if fn == "meters.txt":
            scale_meters_txt(p, q); continue
        if not fn.lower().endswith((".png", ".jpg")):
            shutil.copy2(p, q); continue
        if only and not any(fn.startswith(n + "-") for n in only):
            continue
        t0 = time.time()
        im = Image.open(p); im.load()
        if fn.endswith(("-needle.png", "-indicator.png")):
            res = im.resize((round(im.width * F), round(im.height * F)), Image.LANCZOS)
        else:
            res = ai_scale(model, im)
            if fn.endswith("-screen-bgr.png"):
                res = pad_screen(res)
        res.save(q)
        print(f"{fn}: {im.size} -> {res.size} ({time.time() - t0:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
