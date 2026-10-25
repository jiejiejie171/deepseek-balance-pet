"""Derive the hand-drawn bubble layers from the upstream character art.

The upstream DSniang02.png is a flat composition of DSniang1.png at (414, 415)
plus a hand-drawn thought bubble: a large bubble, a medium circle and a small
circle. This script removes the character to produce the bubble-only layers
used by the pet window, so the three parts can be revealed in sequence (small
circle -> medium circle -> large bubble) while keeping the original skin.

Dev-only: requires Pillow and numpy.
"""

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "src" / "deepseek_pet" / "assets"
FULL = ASSETS / "DSniang02.png"
CHAR = ASSETS / "DSniang1.png"
OUT = ASSETS / "whale_bubble.png"

CHAR_OFFSET = (414, 415)
MAIN_BOX = (70, 10, 838, 515)
MID_BOX = (305, 525, 402, 598)
SMALL_BOX = (410, 619, 479, 674)
PART_BOXES = {"main": MAIN_BOX, "mid": MID_BOX, "small": SMALL_BOX}


def main() -> None:
    full = Image.open(FULL).convert("RGBA")
    char_img = Image.open(CHAR).convert("RGBA")
    width, height = full.size

    char_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    char_layer.alpha_composite(char_img, CHAR_OFFSET)

    full_px = np.array(full).astype(np.float32)
    char_px = np.array(char_layer).astype(np.float32)
    bubble_px = full_px.copy()
    bubble_px[:, :, 3] = full_px[:, :, 3] * (1.0 - char_px[:, :, 3] / 255.0)
    bubble = Image.fromarray(np.clip(bubble_px, 0, 255).astype(np.uint8), "RGBA")

    clean = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for box in PART_BOXES.values():
        crop = bubble.crop(box)
        clean.paste(crop, box[:2], crop)
    clean.save(OUT)

    for name, box in PART_BOXES.items():
        part = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        crop = clean.crop(box)
        part.paste(crop, box[:2], crop)
        part_path = ASSETS / f"bubble_{name}.png"
        part.save(part_path)
        print(part_path)


if __name__ == "__main__":
    main()
