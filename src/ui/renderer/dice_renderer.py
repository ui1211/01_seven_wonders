from __future__ import annotations

import pyxel


class DiceRenderer:
    def __init__(self, text):
        self.text = text

    def draw(self, layout, game):

        if not game.dice_anim:
            return

        cx = layout.width // 2
        cy = int(layout.height * 0.45)

        size = 28
        gap = 6

        x1 = cx - size - gap
        x2 = cx + gap

        pyxel.rect(x1, cy, size, size, 12)
        pyxel.rect(x2, cy, size, size, 12)

        pyxel.rectb(x1, cy, size, size, 0)
        pyxel.rectb(x2, cy, size, size, 0)

        self.text.draw_center(
            x1 + size // 2,
            cy + size // 2 - 4,
            str(game.dice_tens),
            0,
        )

        self.text.draw_center(
            x2 + size // 2,
            cy + size // 2 - 4,
            str(game.dice_ones),
            0,
        )

        self.text.draw_center(
            cx,
            cy - 12,
            "ROLL",
            8,
        )
