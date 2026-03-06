from __future__ import annotations

import pyxel


class UiRenderer:
    def __init__(self, text):
        self.text = text

    def draw_label_box(self, x: int, y: int, w: int, h: int):
        pyxel.rect(x, y, w, h, 0)
        pyxel.rectb(x, y, w, h, 7)

    def draw_button(self, x: int, y: int, w: int, h: int, label: str):

        pyxel.rect(x, y, w, h, 7)
        pyxel.rectb(x, y, w, h, 0)

        self.text.draw_center(
            x + w // 2,
            y + h // 2 - 4,
            label,
            0,
        )

    def draw_popup(self, layout, text: str, success: bool):

        popup_w = int(layout.width * 0.35)

        popup_x, popup_y = layout.popup_position(popup_w)

        if success:
            bg = 7
            border = 11
            text_col = 12
        else:
            bg = 14
            border = 11
            text_col = 12

        popup_h = int(layout.height * 0.05)

        pyxel.rect(popup_x, popup_y, popup_w, popup_h, bg)
        pyxel.rectb(popup_x, popup_y, popup_w, popup_h, border)

        self.text.draw(
            popup_x + 10,
            popup_y + int(popup_h * 0.35),
            text,
            text_col,
        )
