class Card:
    def __init__(self, name, success, atk, mgc, tec, x, y, cost):
        self.name = name
        self.success = success
        self.atk = atk
        self.mgc = mgc
        self.tec = tec
        self.x = x
        self.y = y
        self.w = 50
        self.h = 70
        self.drag = False
        self.cost = cost
