"""Render a standalone JB Pharma 'P' for the icons/ folder.

Marketing / reference only — the live app at Targets/Pharma/.../icon-1024.png
is the master Glossary G (the consolidated app ships under Pharma's bundle ID
for App Store continuity), so this script intentionally does NOT write there.
"""
from PIL import Image
from pathlib import Path

from jb_stamp import (
    SUITE_BG, CANVAS_SIZE, ICONS_MIRROR_DIR,
    apply_jb_stamp, render_main_glyph,
)

ACCENT = (140, 42, 38)           # #8C2A26 deep pharma brick / oxblood
MIRROR_NAME = "pharma.png"


def render():
    img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), SUITE_BG)
    render_main_glyph(img, "P", ACCENT)
    apply_jb_stamp(img)
    ICONS_MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    out = ICONS_MIRROR_DIR / MIRROR_NAME
    img.save(out, "PNG")
    print(f"Wrote icons/{MIRROR_NAME}")


if __name__ == "__main__":
    render()
