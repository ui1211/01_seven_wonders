# src/ui/input_controller.py
from __future__ import annotations


class InputController:
    def __init__(self):
        self.dragging_card = None

    def on_mouse_down(self, cards, hand_poses, mx: int, my: int, card_w: int, card_h: int):
        if self.dragging_card is not None:
            return

        hovered = None
        ordered = sorted(cards, key=lambda x: getattr(hand_poses.get(x), "z", -999), reverse=True)

        for c in ordered:
            pose = hand_poses.get(c)
            if pose is None:
                continue
            w = int(card_w * pose.scale)
            h = int(card_h * pose.scale)
            if (pose.x - w // 2 < mx < pose.x + w // 2) and (pose.y - h // 2 < my < pose.y + h // 2):
                hovered = c
                break

        if hovered is None:
            return

        hovered.drag = True
        hovered.x = mx
        hovered.y = my
        self.dragging_card = hovered

    def on_mouse_move(self, mx: int, my: int):
        if self.dragging_card is None:
            return
        self.dragging_card.x = mx
        self.dragging_card.y = my

    def on_mouse_up(self, objects, mx: int, my: int):
        c = self.dragging_card
        if c is None:
            return None, None

        c.drag = False
        self.dragging_card = None

        for o in objects:
            if not o.alive:
                continue
            if o.x < mx < o.x + o.w and o.y < my < o.y + o.h:
                return c, o

        return c, None
