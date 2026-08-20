"""Convert a portrait photo into the ASCII art block used by the profile SVG.

One-shot tool - re-run only when the avatar changes, then commit the result:
    python3 tools/make_ascii.py assets/avatar.png > assets/ascii_art.txt

Two independent decisions per cell:
  * an elliptical mask decides whether the cell is drawn at all (this is what
    removes the tree and wall behind the subject)
  * inside the mask, luminance picks the glyph, dense-for-dark, so the hair
    reads as a solid mass and the lit side of the face opens up
"""
import argparse
from PIL import Image, ImageEnhance, ImageOps, ImageFilter, ImageDraw

# Dense -> sparse. "fine" gives smooth gradients, "block" gives crisp tonal steps.
RAMPS = {
    "fine": "@%#WM8&B$0OQqpdbkhaomZUXYJCLunxrjft/|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "block": "@%#*+=-:. ",
    "mid": "@%#WM8bkao*ZXJCunxrjft/|()1[]?-_+~<>i!l;:,^`'. ",
}


def ellipse_mask(size, cx, cy, rx, ry, feather):
    w, h = size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse(
        [(cx - rx) * w, (cy - ry) * h, (cx + rx) * w, (cy + ry) * h], fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather * min(w, h)))


def build(path, cols, crop, contrast, brightness, gamma, lo, hi, aspect,
          vig, cover, invert, ink, ramp):
    img = Image.open(path).convert("L")
    w, h = img.size
    l, t, r, b = crop
    img = img.crop((int(w * l), int(h * t), int(w * r), int(h * b)))

    mask = ellipse_mask(img.size, *vig) if vig else Image.new("L", img.size, 255)

    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = img.filter(ImageFilter.SMOOTH)
    img = ImageOps.autocontrast(img, cutoff=2)

    cw, ch = img.size
    rows = max(1, int(cols * (ch / cw) / aspect))
    img = img.resize((cols, rows), Image.LANCZOS)
    mask = mask.resize((cols, rows), Image.LANCZOS)
    px, mp = img.load(), mask.load()

    out = []
    for y in range(rows):
        line = []
        for x in range(cols):
            if mp[x, y] / 255.0 < cover:
                line.append(" ")
                continue
            v = min(max((px[x, y] / 255.0 - lo) / (hi - lo), 0.0), 1.0)
            if invert:
                v = 1.0 - v
            if (1.0 - v) < ink:              # too little ink to be worth a glyph
                line.append(" ")
                continue
            idx = int((v ** gamma) * (len(ramp) - 1))
            line.append(ramp[min(idx, len(ramp) - 1)])
        out.append("".join(line).rstrip())
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("src", nargs="?", default="assets/avatar.png")
    p.add_argument("--cols", type=int, default=48)
    p.add_argument("--crop", default="0.22,0.15,0.84,0.78", help="l,t,r,b fractions")
    p.add_argument("--contrast", type=float, default=1.55)
    p.add_argument("--brightness", type=float, default=1.0)
    p.add_argument("--gamma", type=float, default=1.0, help=">1 opens the shadows")
    p.add_argument("--lo", type=float, default=0.0, help="black point")
    p.add_argument("--hi", type=float, default=1.0, help="white point")
    p.add_argument("--aspect", type=float, default=1.9)
    p.add_argument("--vignette", default="0.50,0.50,0.45,0.51,0.035",
                   help="cx,cy,rx,ry,feather fractions; 'none' to disable")
    p.add_argument("--invert", action="store_true",
                   help="dense glyphs for BRIGHT areas (positive rendering)")
    p.add_argument("--ramp", default="fine", choices=sorted(RAMPS),
                   help="glyph ramp: fine | mid | block")
    p.add_argument("--ink", type=float, default=0.0,
                   help="blank any cell whose density falls below this")
    p.add_argument("--cover", type=float, default=0.55,
                   help="mask value above which a cell is drawn")
    a = p.parse_args()
    crop = tuple(float(x) for x in a.crop.split(","))
    vig = None if a.vignette == "none" else tuple(
        float(x) for x in a.vignette.split(","))
    print(build(a.src, a.cols, crop, a.contrast, a.brightness, a.gamma,
                a.lo, a.hi, a.aspect, vig, a.cover, a.invert, a.ink, RAMPS[a.ramp]))


if __name__ == "__main__":
    main()
