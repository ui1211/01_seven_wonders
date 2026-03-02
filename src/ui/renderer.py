# src/ui/renderer.py
from __future__ import annotations


class Renderer:
    def __init__(self, font, images, width: int, height: int):
        self.font = font
        self.images = images
        self.width = int(width)
        self.height = int(height)

        self.card_w = int(width * 0.09)
        self.card_h = int(self.card_w * 1.4)

    def draw_text(self, pyxel, x: int, y: int, text: str, col: int):
        # pyxel.text(x + 1, y + 1, text, 0, self.font)
        pyxel.text(x, y, text, col, self.font)

    def draw_text_center(self, pyxel, cx: int, y: int, text: str, col: int):
        x = int(cx - (len(text) * 4) // 2)
        self.draw_text(pyxel, x, y, text, col)

    def draw_label_box(self, pyxel, x: int, y: int, w: int, h: int):
        pyxel.rect(x, y, w, h, 0)
        pyxel.rectb(x, y, w, h, 7)

    def draw_button(self, pyxel, x: int, y: int, w: int, h: int, label: str):
        pyxel.rect(x, y, w, h, 7)
        pyxel.rectb(x, y, w, h, 0)
        self.draw_text_center(pyxel, x + w // 2, y + (h // 2) - 3, label, 0)

    def draw_bar(self, pyxel, x, y, value, max_value, col):
        pyxel.rect(x, y, 44, 5, 5)
        w = int(44 * value / max_value) if max_value > 0 else 0
        pyxel.rect(x, y, w, 5, col)
        pyxel.rectb(x, y, 44, 5, 0)

    def draw_hud(self, pyxel, round_index: int, max_rounds: int, risk: int, risk_max: int):

        ratio = risk / risk_max
        if ratio < 0.3:
            col = 3
        elif ratio < 0.7:
            col = 10
        else:
            col = 8

        self.draw_text(pyxel, 10, 5, f"{round_index}/{max_rounds}", 7)
        self.draw_text(pyxel, 62, 5, "きけんど", 7)
        risk_w = int(200 * risk / risk_max) if risk_max > 0 else 0
        pyxel.rect(20, 14, 200, 6, 0)
        pyxel.rect(20, 14, risk_w, 6, col)
        pyxel.rectb(20, 14, 200, 6, 7)

    def draw_card(self, pyxel, card, pose):
        self.draw_card_at(pyxel, card, pose.x, pose.y, pose.scale)

    def draw_card_at(self, pyxel, card, cx: int, cy: int, scale: float = 1.0):
        w = int(self.card_w * scale)
        h = int(self.card_h * scale)

        x = int(cx - w // 2)
        y = int(cy - h // 2)

        pyxel.blt(x, y, self.images["card"], 0, 0, w, h)

        if card.in_graveyard:
            pyxel.rect(x, y, w, 12, 0)
            self.draw_text(pyxel, x + 4, y + 2, "USED", 8)
            return

        # pyxel.rect(x, y, w, 12, 7)
        self.draw_text(pyxel, x + 4, y + 2, str(card.name), 0)

        stats = []
        if card.atk > 0:
            stats.append(("ATK", card.atk, 8))
        if card.mgc > 0:
            stats.append(("MGC", card.mgc, 12))
        if card.tec > 0:
            stats.append(("TEC", card.tec, 3))

        mid_y = y + h // 3 - 6
        sx = x + 6
        for label, value, col in stats:
            pyxel.text(sx, mid_y, f"{label}:{value}", col, self.font)
            mid_y += 10

        suc = getattr(card, "success", 0)
        cost = getattr(card, "cost", 0)
        self.draw_text(pyxel, x + 6, mid_y, f"{suc}%  C:{cost}", 0)

    def draw_object(self, pyxel, obj):
        img = self.images.get(obj.image_path)

        if img:
            pyxel.blt(obj.x, obj.y, img, 0, 0, obj.w, obj.h)
        else:
            pyxel.rect(obj.x, obj.y, obj.w, obj.h, 2)

        name_w = max(40, len(str(obj.name)) * 4 + 10)
        self.draw_label_box(pyxel, obj.x - 2, obj.y - 14, name_w, 12)
        self.draw_text(pyxel, obj.x + 2, obj.y - 12, str(obj.name), 7)

        self.draw_bar(pyxel, obj.x, obj.y + 45, obj.hp, obj.max_hp, 8)
        self.draw_bar(pyxel, obj.x, obj.y + 52, obj.mp, obj.max_mp, 12)
        self.draw_bar(pyxel, obj.x, obj.y + 59, obj.tp, obj.max_tp, 3)

    def draw_popup(self, pyxel, layout, text: str, success: bool):
        popup_w = 230
        popup_x, popup_y = layout.popup_position(popup_w)

        if success:
            bg = 3
            border = 11
            text_col = 0
        else:
            bg = 8
            border = 7
            text_col = 7

        pyxel.rect(popup_x, popup_y, popup_w, 26, bg)
        pyxel.rectb(popup_x, popup_y, popup_w, 26, border)
        self.draw_text(pyxel, popup_x + 8, popup_y + 9, text, text_col)
