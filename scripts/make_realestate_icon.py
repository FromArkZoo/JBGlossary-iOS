"""Generate the JB Real Estate app icon matching the JB Glossary house style.

Cream background, "JB" in serif italic top-left, big serif "RE" lower-centre in
the earthy-clay brand colour (#A8593E from Sources/Industries/RealEstateBrand.swift).
Produces a 1024x1024 PNG at the standard AppIcon path.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "Targets/RealEstate/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

CREAM = (245, 239, 230)
INK = (20, 24, 29)
CLAY = (168, 89, 62)

BODONI = "/System/Library/Fonts/Supplemental/Bodoni 72.ttc"

img = Image.new("RGB", (1024, 1024), CREAM)
draw = ImageDraw.Draw(img)

jb_font = ImageFont.truetype(BODONI, 165, index=1)  # Book Italic
draw.text((78, 60), "JB", font=jb_font, fill=INK)

re_font = ImageFont.truetype(BODONI, 720, index=2)  # Bold
re_text = "RE"
bbox = draw.textbbox((0, 0), re_text, font=re_font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
x = (1024 - tw) // 2 - bbox[0]
y = (1024 - th) // 2 - bbox[1] + 90
draw.text((x, y), re_text, font=re_font, fill=CLAY)

img.save(OUT, "PNG")
print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
