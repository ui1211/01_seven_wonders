# src/ui/layout_manager.py
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class SimplePose:
    x: int
    y: int
    angle: float
    scale: float
    z: int


@dataclass(frozen=True)
class Pose:
    x: int
    y: int
    scale: float
    z: int


class LayoutManager:
    def __init__(self, width: int, height: int):
        self.width = int(width)
        self.height = int(height)

    def object_slots(self, n: int):
        margin_x = self.width * 0.1
        usable_w = self.width * 0.8
        y = int(self.height * 0.35)

        if n <= 1:
            return [(self.width // 2, y)]

        gap = usable_w / (n - 1)
        return [(int(margin_x + gap * i), y) for i in range(n)]

    def popup_position(self, popup_w: int):
        x = (self.width - int(popup_w)) // 2
        y = int(self.height * 0.7)
        return x, y

    def graveyard_next_xy(self, grave_count: int):
        gx = int(self.width * 0.88)
        gy = int(self.height * 0.75)
        return gx + grave_count * 2, gy + grave_count * 2

    def hand_poses(self, cards, mx, my, card_w: int, card_h: int):
        poses = {}
        n = len(cards)
        if n == 0:
            return poses

        zone_y = int(self.height * 0.72)

        center_x = self.width // 2
        center_y = zone_y + int(self.height * 0.35)

        radius = int(self.height * 0.28)
        spread = 50

        for i, c in enumerate(cards):
            if getattr(c, "drag", False):
                poses[c] = SimplePose(int(c.x), int(c.y), 0.0, 1.12, 2000)
                continue

            t = (i / max(1, n - 1)) - 0.5
            angle = t * spread
            rad = math.radians(angle)

            x = int(center_x + radius * math.sin(rad))
            y = int(center_y - radius * math.cos(rad))

            poses[c] = SimplePose(x, y, angle, 1.0, i)

        hovered = None
        for c in reversed(cards):
            p = poses[c]
            if self._hit(mx, my, p, card_w, card_h):
                hovered = c
                break

        for c in cards:
            p = poses[c]
            if getattr(c, "drag", False):
                continue
            if c == hovered:
                p.scale = 1.16
                p.angle = 0.0
                p.y -= 30
                p.z = 999
            else:
                p.z = poses[c].z

        return poses

    def graveyard_poses(self, cards):
        gx = int(self.width * 0.88)
        gy = int(self.height * 0.75)

        grave = [c for c in cards if c.in_graveyard]
        poses = {}
        for i, c in enumerate(grave):
            poses[c] = Pose(x=gx + i * 2, y=gy + i * 2, scale=0.78, z=-100 - i)
        return poses

    def _hit(self, mx, my, pose, card_w: int, card_h: int):
        w = int(card_w * pose.scale)
        h = int(card_h * pose.scale)
        return pose.x - w // 2 < mx < pose.x + w // 2 and pose.y - h // 2 < my < pose.y + h // 2
