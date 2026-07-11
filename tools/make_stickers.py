#!/usr/bin/env python3
"""Regenerate the normalized die-cut sticker assets in stickers/.

Each source logo is trimmed to its alpha bounds, scaled by a per-asset
visual-mass factor (full-bleed square marks read bigger than organic
silhouettes at the same pixel size), centered on a shared transparent
canvas, and given a uniform off-white die-cut border baked into the
alpha silhouette. Drop shadows stay in CSS.
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
STICKERS = ROOT / "stickers"

CANVAS = 320                 # square output canvas, px (~4.5x the 70px display size)
CONTENT = 236                # content box at visual-mass factor 1.0
BORDER = 16                  # die-cut thickness at canvas scale (~3.5px at 70px)
BORDER_COLOR = (253, 253, 251, 255)   # off-white, a touch brighter than --bg

# (output, source, visual-mass factor) — factors tuned by eye:
# full-bleed rounded squares (change, instagram) sit smaller than the
# duolingo owl's organic silhouette; the google G is in between.
SOURCES = [
    ("sticker-change.png",    "svg:change-org-flat.svg",         0.92),
    ("sticker-duolingo.png",  "icons8-duolingo-logo-100.png",    1.00),
    ("sticker-instagram.png", "icons8-instagram-100.png",        0.92),
    ("sticker-google.png",    "icons8-google-100.png",           0.97),
]


def load(source: str) -> Image.Image:
    if source.startswith("svg:"):
        svg = STICKERS / source[4:]
        tmp = STICKERS / ".svg-render.png"
        # -density renders the SVG at high resolution natively
        # (a post-load -resize would rasterize at 100px, then upscale blurry)
        subprocess.run(
            ["magick", "-background", "none", "-density", "384",
             str(svg), str(tmp)],
            check=True,
        )
        img = Image.open(tmp).convert("RGBA")
        img.load()
        tmp.unlink()
        return img
    return Image.open(STICKERS / source).convert("RGBA")


def die_cut(img: Image.Image) -> Image.Image:
    mask = img.getchannel("A").point(lambda a: 255 if a > 8 else 0)
    for _ in range(BORDER // 2):          # each MaxFilter(5) pass dilates ~2px
        mask = mask.filter(ImageFilter.MaxFilter(5))
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    base = Image.new("RGBA", img.size, (0, 0, 0, 0))
    base.paste(Image.new("RGBA", img.size, BORDER_COLOR), (0, 0), mask)
    return Image.alpha_composite(base, img)


def normalize(source: str, factor: float) -> Image.Image:
    img = load(source)
    img = img.crop(img.getchannel("A").getbbox())
    target = int(CONTENT * factor)
    scale = target / max(img.size)
    img = img.resize(
        (round(img.width * scale), round(img.height * scale)), Image.LANCZOS
    )
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.paste(img, ((CANVAS - img.width) // 2, (CANVAS - img.height) // 2), img)
    return die_cut(canvas)


def main() -> None:
    for out, src, factor in SOURCES:
        normalize(src, factor).save(STICKERS / out)
        print(f"wrote stickers/{out}")


if __name__ == "__main__":
    main()
