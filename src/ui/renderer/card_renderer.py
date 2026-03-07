from __future__ import annotations

import pyxel


class CardRenderer:
    def __init__(self, text, images, card_w, card_h):
        self.text = text
        self.images = images
        self.card_w = card_w
        self.card_h = card_h

    def draw(self, card, cx, cy, scale=1.0):

        w = int(self.card_w * scale)
        h = int(self.card_h * scale)

        x = cx - w // 2
        y = cy - h // 2

        pyxel.blt(x, y, self.images["card"], 0, 0, w, h, 0)

        if card.in_graveyard:
            return

        self.text.draw(x + int(w * 0.17), y + int(h * 0.08), str(card.name), 0)

        mid_y = y + int(h * 0.60)

        if card.atk > 0:
            self.text.draw(x + int(w * 0.17), mid_y, f"ATK:{card.atk}", 14)
            mid_y += 10

        if card.mgc > 0:
            self.text.draw(x + int(w * 0.17), mid_y, f"MGC:{card.mgc}", 13)
            mid_y += 10

        if card.tec > 0:
            self.text.draw(x + int(w * 0.17), mid_y, f"TEC:{card.tec}", 7)
            mid_y += 10

        if card.atk < 0 and card.mgc < 0 and card.tec < 0:
            mid_y += 10

        suc = getattr(card, "success", 0)
        cost = getattr(card, "cost", 0)

        self.text.draw(x + int(w * 0.17), mid_y, f"{suc}% C:{cost}", 0)
