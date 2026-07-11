#!/usr/bin/env python3
"""Regenerate the normalized die-cut sticker assets in stickers/.

The three square "app tile" marks (Change.org, Duolingo, Instagram) share
one corner-radius fraction, taken from Instagram's official 2016 icon
(~0.198 of the tile side), so the set reads as one sticker sheet instead
of three slightly different squares. Sources are official/public assets
committed in stickers/ (no Icons8):

  change-org-flat.svg   hand-derived flat Change.org mark, rx matched
  src-instagram.svg     official gradient icon (Wikimedia Commons, PD)
  src-duolingo-512.png  official PWA icon (duolingo.com manifest); the
                        circular icon is center-cropped full-bleed and
                        masked to the shared radius
  src-google-g.svg      official Google "G" (Wikimedia Commons) — not a
                        tile; kept as a free-standing glyph

Each mark is scaled by a per-asset visual-mass factor, centered on a
shared transparent canvas, and given a uniform off-white die-cut border
baked into the alpha silhouette. Drop shadows stay in CSS.
"""
import io
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
STICKERS = ROOT / "stickers"

CANVAS = 320                 # square output canvas, px (~4.5x the 70px display size)
CONTENT = 236                # content box at visual-mass factor 1.0
BORDER = 16                  # die-cut thickness at canvas scale (~3.5px at 70px)
BORDER_COLOR = (253, 253, 251, 255)   # off-white, a touch brighter than --bg
TILE_RADIUS_FRAC = 0.198     # corner radius / tile side, from the official IG icon
DUO_CROP = 360               # center-crop side on the 512px circular Duolingo icon

# (output, source, kind, visual-mass factor). Tiles share one factor by
# construction (same shape); the free-standing Google G reads slightly
# smaller so it gets a touch more.
SOURCES = [
    ("sticker-change.png",    "change-org-flat.svg",   "svg",      0.92),
    ("sticker-duolingo.png",  "src-duolingo-512.png",  "duo-tile", 0.92),
    ("sticker-instagram.png", "src-instagram.svg",     "svg",      0.92),
    ("sticker-google.png",    "src-google-g.svg",      "svg",      0.97),
]


def render_svg(name: str, px: int = 400) -> Image.Image:
    # cairosvg handles the gradient defs magick's MSVG renderer drops
    png = cairosvg.svg2png(
        url=str(STICKERS / name), output_width=px, output_height=px
    )
    return Image.open(io.BytesIO(png)).convert("RGBA")


def rounded_mask(side: int, radius_frac: float) -> Image.Image:
    """Anti-aliased rounded-rect mask, drawn 4x supersampled."""
    ss = 4
    big = Image.new("L", (side * ss, side * ss), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        (0, 0, side * ss - 1, side * ss - 1),
        radius=int(side * ss * radius_frac), fill=255,
    )
    return big.resize((side, side), Image.LANCZOS)


def load(source: str, kind: str) -> Image.Image:
    if kind == "svg":
        return render_svg(source)
    if kind == "duo-tile":
        # official circular icon -> full-bleed center crop -> shared tile radius
        img = Image.open(STICKERS / source).convert("RGBA")
        c = img.width // 2
        half = DUO_CROP // 2
        img = img.crop((c - half, c - half, c + half, c + half))
        img.putalpha(rounded_mask(img.width, TILE_RADIUS_FRAC))
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


def normalize(source: str, kind: str, factor: float) -> Image.Image:
    img = load(source, kind)
    img = img.crop(img.getchannel("A").getbbox())
    target = int(CONTENT * factor)
    scale = target / max(img.size)
    img = img.resize(
        (round(img.width * scale), round(img.height * scale)), Image.LANCZOS
    )
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.alpha_composite(img, ((CANVAS - img.width) // 2, (CANVAS - img.height) // 2))
    return die_cut(canvas)


def main() -> None:
    for out, src, kind, factor in SOURCES:
        normalize(src, kind, factor).save(STICKERS / out)
        print(f"wrote stickers/{out}")


if __name__ == "__main__":
    main()
