"""Render the JB Finance app icon — single 'F' on cream, royal purple."""
from PIL import Image
from pathlib import Path

from jb_stamp import (
    SUITE_BG, CANVAS_SIZE, ICONS_MIRROR_DIR,
    apply_jb_stamp, render_main_glyph,
)

ACCENT = (74, 44, 122)           # #4A2C7A royal purple
MIRROR_NAME = "finance.png"

OUT = Path(__file__).parent.parent / "Targets" / "Finance" / "Resources" / \
      "Assets.xcassets" / "AppIcon.appiconset" / "icon-1024.png"


def render():
    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), SUITE_BG)
    render_main_glyph(img, "F", ACCENT)
    apply_jb_stamp(img)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    ICONS_MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    img.save(ICONS_MIRROR_DIR / MIRROR_NAME, "PNG")
    print(f"Wrote {OUT} (+ icons/{MIRROR_NAME})")


if __name__ == "__main__":
    render()
