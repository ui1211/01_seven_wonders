# src/model/card.py
from __future__ import annotations


class Card:
    def __init__(self, name, success, atk, mgc, tec, cost):
        self.name = name
        self.success = int(success)
        self.atk = int(atk)
        self.mgc = int(mgc)
        self.tec = int(tec)
        self.cost = int(cost)

        self.in_graveyard = False
        self.drag = False

        self.x = 0
        self.y = 0
        self.scale = 1.0
        self.z = 0

        self.w = 50
        self.h = 70

    def clone(self):
        return Card(self.name, self.success, self.atk, self.mgc, self.tec, self.cost)

    def enhance(self, kind: str, amount: int):
        k = str(kind).lower()
        n = int(amount)
        if k == "cost":
            self.cost = max(-25, self.cost + n)
            return
        if k == "atk":
            self.atk = max(0, self.atk + n)
            return
        if k == "mgc":
            self.mgc = max(0, self.mgc + n)
            return
        if k == "tec":
            self.tec = max(0, self.tec + n)
