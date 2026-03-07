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
        is_enemy=False,
        can_talk=False,
        topics=None,
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
        self.h = 50
        self.alive = True
        self.is_enemy = bool(is_enemy)
        self.can_talk = bool(can_talk)
        self.topics = list(topics or [])

        self.scene_map = {"hp": scene_hp, "mp": scene_mp, "tp": scene_tp}
