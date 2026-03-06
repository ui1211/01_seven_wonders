from __future__ import annotations

import pyxel


class TextRenderer:
    def __init__(self, font):
        self.font = font

    def draw(self, x: int, y: int, text: str, col: int):
        pyxel.text(x, y, text, col, self.font)

    def width(self, text: str) -> int:
        w = 0
        for c in text:
            if ord(c) < 128:
                w += 4
            else:
                w += 8
        return w

    def draw_center(self, cx: int, y: int, text: str, col: int):
        x = cx - self.width(text) // 2
        self.draw(x, y, text, col)
