"""Apply the canonical JB stamp to every existing icon in place, and mirror
each into the top-level icons/ folder.

Use this for icons whose full render recipe isn't preserved (e.g. AI). For
Glossary G / Law / Finance, prefer running the per-app render script so the
main glyph is also produced from a known recipe — those scripts mirror to
icons/ themselves.
"""
from pathlib import Path
from PIL import Image

from jb_stamp import ICONS_MIRROR_DIR, apply_jb_stamp

ROOT = Path(__file__).parent.parent / "Targets"
# (xcasset path, mirror filename)
ICONS = [
    (ROOT / "AI/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png",      "ai.png"),
    (ROOT / "Law/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png",     "law.png"),
    (ROOT / "Pharma/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png",  "glossary.png"),
    (ROOT / "Finance/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png", "finance.png"),
]


def restamp(path: Path, mirror_name: str) -> None:
    if not path.exists():
        print(f"SKIP (missing): {path}")
        return
    img = Image.open(path).convert("RGB")
    apply_jb_stamp(img)
    img.save(path, "PNG")
    ICONS_MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    img.save(ICONS_MIRROR_DIR / mirror_name, "PNG")
    print(f"restamped: {path.relative_to(Path.home())}  →  icons/{mirror_name}")


if __name__ == "__main__":
    for path, name in ICONS:
        restamp(path, name)
