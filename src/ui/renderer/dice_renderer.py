from __future__ import annotations

import math

import pyxel


class DiceRenderer:
    def __init__(self, text):
        self.text = text

    def _roll_offset(self, t, seed_x, seed_y, amp):

        x = (
            math.sin(t * 0.27 + seed_x) * amp
            + math.sin(t * 0.61 + seed_y) * amp * 0.6
            + math.sin(t * 1.33 + seed_x * 2) * amp * 0.3
        )

        y = (
            math.cos(t * 0.31 + seed_y) * amp
            + math.cos(t * 0.73 + seed_x) * amp * 0.6
            + math.cos(t * 1.21 + seed_y * 2) * amp * 0.3
        )

        return x, y

    def draw(self, layout, game):

        if not game.dice_anim:
            return

        cx = layout.width // 2
        cy = int(layout.height * 0.45)

        size = 45
        gap = 12

        # 時間
        t = pyxel.frame_count

        # 減速係数 (sin減衰)
        phase = min(1.0, (game.dice_duration - game.dice_timer) / game.dice_duration)
        amp = (1 - phase) ** 2 * 32

        # ダイス1
        dx1, dy1 = self._roll_offset(t, 1.3, 2.1, amp)

        # ダイス2
        dx2, dy2 = self._roll_offset(t, 4.7, 3.2, amp)

        x1 = int(cx - size - gap + dx1)
        x2 = int(cx + gap + dx2)

        y1 = int(cy + dy1)
        y2 = int(cy + dy2)

        pyxel.rect(x1, y1, size, size, 6)
        pyxel.rect(x2, y2, size, size, 8)

        pyxel.rectb(x1, y1, size, size, 12)
        pyxel.rectb(x2, y2, size, size, 12)

        # 回転風のサイズ変化
        scale1 = 0.8 + abs(math.sin(t * 0.25)) * 0.4
        scale2 = 0.8 + abs(math.sin(t * 0.31)) * 0.4

        self.text.draw_center(
            x1 + size // 2,
            y1 + int(size * scale1 / 2) - 4,
            str(game.dice_tens),
            12,
        )

        self.text.draw_center(
            x2 + size // 2,
            y2 + int(size * scale2 / 2) - 4,
            str(game.dice_ones),
            12,
        )

        self.text.draw_center(
            cx,
            cy - 20,
            "ROLL",
            8,
        )
