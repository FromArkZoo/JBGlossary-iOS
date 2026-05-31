"""Render the JB Insurance app icon — single 'I' on cream, deep-teal accent."""
from PIL import Image
from pathlib import Path

from jb_stamp import (
    SUITE_BG, CANVAS_SIZE, ICONS_MIRROR_DIR,
    apply_jb_stamp, render_main_glyph,
)

ACCENT = (28, 93, 107)           # #1C5D6B deep teal — trust & protection
MIRROR_NAME = "insurance.png"

OUT = Path(__file__).parent.parent / "Targets" / "Insurance" / "Resources" / \
      "Assets.xcassets" / "AppIcon.appiconset" / "icon-1024.png"


def render():
    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), SUITE_BG)
    render_main_glyph(img, "I", ACCENT)
    apply_jb_stamp(img)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    ICONS_MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    img.save(ICONS_MIRROR_DIR / MIRROR_NAME, "PNG")
    print(f"Wrote {OUT} (+ icons/{MIRROR_NAME})")


if __name__ == "__main__":
    render()
