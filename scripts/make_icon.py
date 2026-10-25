from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "deepseek_pet" / "assets" / "DSniang1.png"
DST = ROOT / "src" / "deepseek_pet" / "assets" / "icon.ico"

image = Image.open(SRC).convert("RGBA")
image.save(
    DST,
    format="ICO",
    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
print(DST)
