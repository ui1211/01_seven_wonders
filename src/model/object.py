class Obj:
    def __init__(
        self,
        name,
        hp,
        mp,
        tp,
        x,
        y,
        image_path,
        scene_hp=None,
        scene_mp=None,
        scene_tp=None,
    ):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.tp = tp
        self.max_hp = hp
        self.max_mp = mp
        self.max_tp = tp
        self.x = x
        self.y = y
        self.image_path = image_path
        self.w = 40
        self.h = 40
        self.alive = True

        self.scene_map = {"hp": scene_hp, "mp": scene_mp, "tp": scene_tp}
