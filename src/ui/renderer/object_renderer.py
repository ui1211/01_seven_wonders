from __future__ import annotations

import pyxel


class ObjectRenderer:
    def __init__(self, text, images, object_w, object_h, bar_w, bar_h):
        self.text = text
        self.images = images
        self.object_w = object_w
        self.object_h = object_h
        self.bar_w = bar_w
        self.bar_h = bar_h

    def draw_bar(self, x, y, value, max_value, col):

        pyxel.rect(x, y, self.bar_w, self.bar_h, 5)

        w = int(self.bar_w * value / max_value) if max_value > 0 else 0

        pyxel.rect(x, y, w, self.bar_h, col)
        pyxel.rectb(x, y, self.bar_w, self.bar_h, 0)

    def draw(self, obj):

        img = self.images.get(obj.image_path)

        if img:
            pyxel.rect(obj.x, obj.y, self.object_w, self.object_h, 3)
            pyxel.blt(obj.x + 2, obj.y, img, 0, 0, self.object_w, self.object_h, 0)
        else:
            pyxel.rect(obj.x, obj.y, self.object_w, self.object_h, 2)

        self.text.draw(obj.x + 2, obj.y - 12, str(obj.name), 0)

        self.draw_bar(obj.x, obj.y + self.object_h + 2, obj.hp, obj.max_hp, 14)
        self.draw_bar(obj.x, obj.y + self.object_h + 8, obj.mp, obj.max_mp, 13)
        self.draw_bar(obj.x, obj.y + self.object_h + 14, obj.tp, obj.max_tp, 7)
