from __future__ import annotations


class Renderer:
    def __init__(self, writer, images, width: int, height: int):
        self.writer = writer
        self.images = images

        self.width = int(width)
        self.height = int(height)

        # -------------------
        # UIスケール
        # -------------------

        self.font_size = int(self.height * 0.025)

        self.card_w = int(self.width * 0.12)
        self.card_h = int(self.card_w * 1.4)

        self.object_w = int(self.width * 0.08)
        self.object_h = int(self.object_w * 1.2)

        self.bar_w = self.object_w  # int(self.width * 0.07)
        self.bar_h = int(self.height * 0.01)

        self.name_box_h = int(self.height * 0.02)

    def draw_text(self, x: int, y: int, text: str, col: int):
        self.writer.draw(x, y, text, self.font_size, col)

    def draw_text_center(self, cx: int, y: int, text: str, col: int):
        w = 0
        for c in text:
            if ord(c) < 128:
                w += int(self.font_size * 0.55)
            else:
                w += int(self.font_size * 0.9)

        x = int(cx - w / 2)
        self.draw_text(x, y, text, col)

    def draw_label_box(self, pyxel, x: int, y: int, w: int, h: int):
        pyxel.rect(x, y, w, h, 0)
        pyxel.rectb(x, y, w, h, 7)

    def draw_button(self, pyxel, x: int, y: int, w: int, h: int, label: str):
        pyxel.rect(x, y, w, h, 7)
        pyxel.rectb(x, y, w, h, 0)
        self.draw_text_center(x + w // 2, y + h // 2 - self.font_size // 2, label, 0)

    def draw_bar(self, pyxel, x, y, value, max_value, col):
        pyxel.rect(x, y, self.bar_w, self.bar_h, 5)

        w = int(self.bar_w * value / max_value) if max_value > 0 else 0

        pyxel.rect(x, y, w, self.bar_h, col)
        pyxel.rectb(x, y, self.bar_w, self.bar_h, 0)

    def draw_hud(self, pyxel, round_index: int, max_rounds: int, risk: int, risk_max: int):

        ratio = risk / risk_max

        if ratio < 0.3:
            col = 7
        elif ratio < 0.7:
            col = 5
        else:
            col = 14

        self.draw_text(int(self.width * 0.02), int(self.height * 0.02), f"{round_index}/{max_rounds}", 7)
        self.draw_text(int(self.width * 0.08), int(self.height * 0.02), "きけんど", 7)

        risk_x = int(self.width * 0.03)
        risk_y = int(self.height * 0.05)

        risk_w = int(self.width * 0.3)
        risk_h = int(self.height * 0.01)

        filled = int(risk_w * risk / risk_max) if risk_max > 0 else 0

        pyxel.rect(risk_x, risk_y, risk_w, risk_h, 0)
        pyxel.rect(risk_x, risk_y, filled, risk_h, col)
        pyxel.rectb(risk_x, risk_y, risk_w, risk_h, 7)

    def draw_card(self, pyxel, card, pose):
        self.draw_card_at(pyxel, card, pose.x, pose.y, pose.scale)

    def draw_card_at(self, pyxel, card, cx: int, cy: int, scale: float = 1.0):

        w = int(self.card_w * scale)
        h = int(self.card_h * scale)

        x = int(cx - w // 2)
        y = int(cy - h // 2)

        pyxel.blt(x, y, self.images["card"], 0, 0, w, h, 0)

        if card.in_graveyard:
            return

        self.draw_text(x + int(w * 0.05), y + int(h * 0.05), str(card.name), 0)

        stats = []

        if card.atk > 0:
            stats.append(("ATK", card.atk, 14))
        if card.mgc > 0:
            stats.append(("MGC", card.mgc, 13))
        if card.tec > 0:
            stats.append(("TEC", card.tec, 7))

        mid_y = y + int(h * 0.35)

        for label, value, col in stats:
            self.draw_text(x + int(w * 0.07), mid_y, f"{label}:{value}", col)
            mid_y += int(self.font_size * 0.9)

        suc = getattr(card, "success", 0)
        cost = getattr(card, "cost", 0)

        self.draw_text(x + int(w * 0.07), mid_y, f"{suc}% C:{cost}", 0)

    def draw_object(self, pyxel, obj):

        img = self.images.get(obj.image_path)

        if img:
            pyxel.rect(obj.x, obj.y, self.object_w, self.object_h, 3)
            pyxel.blt(obj.x + 2, obj.y, img, 0, 0, self.object_w, self.object_h, 0)
        else:
            pyxel.rect(obj.x, obj.y, self.object_w, self.object_h, 2)

        # name_w = max(int(self.width * 0.05), len(str(obj.name)) * self.font_size // 2)
        # self.draw_label_box(
        #     pyxel,
        #     obj.x - 2,
        #     obj.y - self.name_box_h,
        #     name_w,
        #     self.name_box_h,
        # )

        self.draw_text(obj.x + 2, obj.y - (self.name_box_h + 8), str(obj.name), 0)

        self.draw_bar(pyxel, obj.x, obj.y + self.object_h + 2, obj.hp, obj.max_hp, 14)
        self.draw_bar(pyxel, obj.x, obj.y + self.object_h + 8, obj.mp, obj.max_mp, 13)
        self.draw_bar(pyxel, obj.x, obj.y + self.object_h + 14, obj.tp, obj.max_tp, 7)

    def draw_popup(self, pyxel, layout, text: str, success: bool):

        popup_w = int(self.width * 0.35)

        popup_x, popup_y = layout.popup_position(popup_w)

        if success:
            bg = 7
            border = 11
            text_col = 12
        else:
            bg = 14
            border = 11
            text_col = 12

        popup_h = int(self.height * 0.05)

        pyxel.rect(popup_x, popup_y, popup_w, popup_h, bg)
        pyxel.rectb(popup_x, popup_y, popup_w, popup_h, border)

        self.draw_text(popup_x + int(self.width * 0.01), popup_y + int(popup_h * 0.35), text, text_col)
