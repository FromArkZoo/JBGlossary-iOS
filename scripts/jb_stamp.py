"""Canonical 'JB' stamp for every icon in the JB Glossary suite.

ONE source of truth — every per-app render script (and the in-place restamp
script) imports `apply_jb_stamp` so the JB on every icon is pixel-identical.
If the JB needs to change, change it here and re-run the renderers.

Recipe (matched to the design family — high-contrast Didone, subtle italic):
- Font:     Didot Normal (index 0 in Didot.ttc)
- Size:     150pt
- Shear:    0.18  (~10° forward slant — synthetic italic on the upright cut)
- Ink:      #14181C  (near-black, same as the suite's INK)
- Anchor:   (95, 75) top-left padding
- Erase:    paint BG over (0,0)-(360,260) before stamping so any old JB is
            wiped without disturbing the main glyph below.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ICONS_MIRROR_DIR = Path(__file__).parent.parent / "icons"

DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
DIDOT_NORMAL_INDEX = 0

JB_SIZE_PT = 150
JB_SHEAR = 0.18
JB_INK = (20, 24, 28)
JB_ANCHOR = (95, 75)
JB_ERASE_RECT = (0, 0, 360, 260)

SUITE_BG = (245, 239, 230)

CANVAS_SIZE = 1024
MAIN_SIZE_PT = 900       # locked point size so every single-letter icon shares cap-height
MAIN_Y_OFFSET = 40       # vertical nudge below mathematical center for visual balance


def _render_slanted(text: str, font: ImageFont.FreeTypeFont,
                    fill: tuple[int, int, int], shear: float) -> Image.Image:
    """Render text to a transparent RGBA layer with a forward shear."""
    pad = 60
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + pad * 2
    h = bbox[3] - bbox[1] + pad * 2
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(
        (pad - bbox[0], pad - bbox[1]), text, font=font, fill=fill
    )
    new_w = w + int(shear * h) + 10
    return layer.transform(
        (new_w, h),
        Image.AFFINE,
        (1, shear, -shear * h, 0, 1, 0),
        resample=Image.BICUBIC,
    )


def render_main_glyph(
    img: Image.Image,
    text: str,
    color: tuple[int, int, int],
    size_pt: int = MAIN_SIZE_PT,
    y_offset: int = MAIN_Y_OFFSET,
) -> Image.Image:
    """Paste a centered slanted-Didot glyph onto `img` at the family's locked
    point size. Use this for every single-letter icon so cap-heights match."""
    font = ImageFont.truetype(DIDOT, size_pt, index=DIDOT_NORMAL_INDEX)
    layer = _render_slanted(text, font, color, JB_SHEAR)
    box = layer.getbbox()
    cropped = layer.crop(box)
    cw, ch = cropped.size
    px = (img.width - cw) // 2
    py = (img.height - ch) // 2 + y_offset
    img.paste(cropped, (px, py), cropped)
    return img


def apply_jb_stamp(
    img: Image.Image,
    bg: tuple[int, int, int] = SUITE_BG,
    erase: bool = True,
) -> Image.Image:
    """Paint the canonical JB stamp onto `img` in place. Returns the image."""
    if erase:
        ImageDraw.Draw(img).rectangle(JB_ERASE_RECT, fill=bg)

    font = ImageFont.truetype(DIDOT, JB_SIZE_PT, index=DIDOT_NORMAL_INDEX)
    layer = _render_slanted("JB", font, JB_INK, JB_SHEAR)
    box = layer.getbbox()
    cropped = layer.crop(box)
    img.paste(cropped, JB_ANCHOR, cropped)
    return img
