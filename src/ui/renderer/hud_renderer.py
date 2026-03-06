from __future__ import annotations

import pyxel


class HudRenderer:
    def __init__(self, text, width, height):
        self.text = text
        self.width = width
        self.height = height

    def draw(self, round_index, max_rounds, risk, risk_max):

        ratio = risk / risk_max

        if ratio < 0.3:
            col = 7
        elif ratio < 0.7:
            col = 5
        else:
            col = 14

        self.text.draw(int(self.width * 0.02), int(self.height * 0.02), f"{round_index}/{max_rounds}", 7)
        self.text.draw(int(self.width * 0.08), int(self.height * 0.02), "きけんど", 7)

        risk_x = int(self.width * 0.03)
        risk_y = int(self.height * 0.05)

        risk_w = int(self.width * 0.3)
        risk_h = int(self.height * 0.01)

        filled = int(risk_w * risk / risk_max) if risk_max > 0 else 0

        pyxel.rect(risk_x, risk_y, risk_w, risk_h, 0)
        pyxel.rect(risk_x, risk_y, filled, risk_h, col)
        pyxel.rectb(risk_x, risk_y, risk_w, risk_h, 7)
