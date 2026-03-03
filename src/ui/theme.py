# src/ui/theme.py
import pyxel

WARM_16 = [
    0x1B1410,  # 0 bg (deep warm brown)
    0xF2E6D9,  # 1 text (warm light)
    0xC9B39B,  # 2 panel light (sand)
    0x8E7A66,  # 3 panel mid (taupe)
    0x5A4638,  # 4 panel dark (brown)
    0xD6A15E,  # 5 accent (mustard)
    0xC56B4F,  # 6 red (terracotta)
    0x7E9A6B,  # 7 green (sage)
    0x5C8DAE,  # 8 blue (muted azure)
    0x8A6FAF,  # 9 violet (dusty purple)
    0x5F8C7A,  # 10 teal-gray (cool muted)
    0x2B211B,  # 11 deeper bg
    0xFFF7EE,  # 12 highlight
    0xBFD0D8,  # 13 cool light blue
    0xA84F3D,  # 14 strong red
    0x3B2A22,  # 15 outline
]


def apply_palette(palette_16):
    if len(palette_16) != 16:
        raise ValueError("palette_16 must be length 16")
    for i, c in enumerate(palette_16):
        # pyxel.colors[i] は 0xRRGGBB
        pyxel.colors[i] = c
