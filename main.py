import random

import pyxel

from src.model.card import Card
from src.model.object import Obj
from src.option import HEIGHT, WIDTH
from src.scene_manager import SceneManager


class GameState:
    PLAY = 0
    RESULT = 1


class App:
    def __init__(self):

        pyxel.init(WIDTH, HEIGHT, title="B Demo")
        pyxel.mouse(True)

        self.font = pyxel.Font("assets/misaki_gothic.bdf")

        self.scene_manager = SceneManager()
        self.state = GameState.PLAY
        self.current_scene_id = 0

        self.world_risk = 0
        self.world_risk_max = 100

        self.popup_text = ""
        self.popup_timer = 0
        self.popup_success = True
        # self.flash_timer = 0
        # self.flash_target = None

        self.pending_damage = {}  # {obj: {dtype: amount}}
        self.damage_timer = 0
        self.damage_duration = 30  # 約0.5秒

        self.init_game()

        pyxel.run(self.update, self.draw)

    # -----------------------------
    # 初期化
    # -----------------------------
    def init_game(self):

        raw_force = pyxel.Image.from_image("./assets/images/trading_card03_yellow.png")
        raw_npc = pyxel.Image.from_image("./assets/images/sleep_nezou_bad_onaka_man.png")
        raw_shadow = pyxel.Image.from_image("./assets/images/akuma_shadow.png")
        raw_door = pyxel.Image.from_image("./assets/images/door.png")

        self.cards = [
            Card("ちから", 60, 15, 0, 5, 30, 150, 10),
            Card("まほう", 80, 0, 15, 5, 95, 150, 50),
            Card("ぎじゅつ", 40, 5, 0, 15, 160, 150, 30),
        ]

        self.objects = [
            Obj("扉", 30, 10, 10, 20, 60, scene_hp=11, scene_mp=12, scene_tp=13),
            Obj("影", 20, 20, 20, 90, 60, scene_hp=21, scene_mp=22, scene_tp=23),
            Obj("住人", 40, 10, 10, 160, 60, scene_hp=31, scene_mp=32, scene_tp=33),
        ]

        self.img_card = self.resize_image(raw_force, 50, 70)
        self.img_npc = self.resize_image(raw_npc, 40, 40)
        self.img_shadow = self.resize_image(raw_shadow, 40, 40)
        self.img_door = self.resize_image(raw_door, 40, 40)

        pyxel.sound(1).set("c2", "t", "7", "n", 15)
        pyxel.sound(2).set("c4e4", "p", "7", "f", 10)
        pyxel.sound(3).set("g2f2", "n", "6", "f", 20)

    # -----------------------------
    # リセット
    # -----------------------------
    def reset_game(self):
        self.world_risk = 0
        self.state = GameState.PLAY
        self.current_scene_id = 0

        for o in self.objects:
            o.hp = o.max_hp
            o.mp = o.max_mp
            o.tp = o.max_tp
            o.alive = True

    # -----------------------------
    def resize_image(self, src, w, h):
        dst = pyxel.Image(w, h)
        for y in range(h):
            for x in range(w):
                sx = int(x * src.width / w)
                sy = int(y * src.height / h)
                dst.pset(x, y, src.pget(sx, sy))
        return dst

    # -----------------------------
    def update(self):

        if self.state == GameState.RESULT:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset_game()
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for c in self.cards:
                if self.hit(c, pyxel.mouse_x, pyxel.mouse_y):
                    c.drag = True

        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            for c in self.cards:
                if c.drag:
                    c.x = pyxel.mouse_x - c.w // 2
                    c.y = pyxel.mouse_y - c.h // 2

        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            for c in self.cards:
                if c.drag:
                    for o in self.objects:
                        if o.alive and self.hit(o, pyxel.mouse_x, pyxel.mouse_y):
                            self.apply_card(c, o)
                    c.drag = False
                    c.x, c.y = self.reset_pos(c)

        if self.popup_timer > 0:
            self.popup_timer -= 1

        # if self.flash_timer > 0:
        #     self.flash_timer -= 1

        if self.damage_timer > 0:
            self.damage_timer -= 1
            progress = 1 - (self.damage_timer / self.damage_duration)

            for obj, dmg_map in self.pending_damage.items():
                for dtype, info in dmg_map.items():

                    start_value = info["start"]
                    dmg = info["damage"]

                    target_value = max(0, start_value - dmg)
                    current = int(start_value - dmg * progress)

                    setattr(obj, dtype, max(target_value, current))

            if self.damage_timer == 0:
                for obj, dmg_map in self.pending_damage.items():
                    for dtype, info in dmg_map.items():
                        if getattr(obj, dtype) == 0 and obj.alive:
                            obj.alive = False
                            self.resolve_object(obj, dtype)
                            break

                self.pending_damage = {}

                if self.world_risk >= self.world_risk_max:
                    self.current_scene_id = 99
                    self.state = GameState.RESULT

    # -----------------------------
    def apply_card(self, card, obj):

        if self.damage_timer > 0:
            return

        roll = random.randint(1, 100)
        success = roll <= card.success

        self.popup_success = success

        self.popup_text = f"目標:{card.success} 出目:{roll} {'成功' if success else '失敗'}"
        self.popup_timer = 60

        base_dmg = {
            "hp": card.atk,
            "mp": card.mgc,
            "tp": card.tec,
        }

        self.world_risk = min(self.world_risk_max, self.world_risk + card.cost)

        if success:
            pyxel.play(0, 2)
            target_obj = obj
            dmg_map = base_dmg

        else:
            pyxel.play(0, 3)
            alive_objs = [o for o in self.objects if o.alive]
            target_obj = random.choice(alive_objs)
            status_keys = ["hp", "mp", "tp"]
            # random.shuffle(status_keys)

            dmg_values = [card.atk, card.mgc, card.tec]

            dmg_map = {status_keys[i]: dmg_values[i] for i in range(3) if dmg_values[i] > 0}

            self.world_risk = min(self.world_risk_max, self.world_risk + 35)

        self.pending_damage = {
            target_obj: {
                dtype: {"start": getattr(target_obj, dtype), "damage": dmg} for dtype, dmg in dmg_map.items() if dmg > 0
            }
        }

        self.damage_timer = self.damage_duration

    # -----------------------------
    def resolve_object(self, obj, dmg_type):

        next_scene = obj.scene_map.get(dmg_type)
        if next_scene is not None:
            self.current_scene_id = next_scene
            self.state = GameState.RESULT

    # -----------------------------
    def hit(self, obj, x, y):
        return obj.x < x < obj.x + obj.w and obj.y < y < obj.y + obj.h

    def reset_pos(self, card):
        if card.name == "ちから":
            return 30, 150
        if card.name == "まほう":
            return 95, 150
        if card.name == "ぎじゅつ":
            return 160, 150

    # -----------------------------
    def draw_bar(self, x, y, value, max_value, col):
        pyxel.rect(x, y, 40, 4, 5)
        w = int(40 * value / max_value)
        pyxel.rect(x, y, w, 4, col)

    # -----------------------------
    def draw(self):

        if self.state == GameState.RESULT:
            pyxel.cls(0)
            text = self.scene_manager.get_text(self.current_scene_id)
            pyxel.text(40, HEIGHT // 2 - 10, text, 7, self.font)
            pyxel.rect(70, HEIGHT // 2 + 20, 100, 20, 8)
            pyxel.text(95, HEIGHT // 2 + 26, "リトライ", 0, self.font)
            return

        pyxel.cls(1)

        pyxel.text(60, 5, "きけんど", 7, self.font)
        risk_w = int(200 * self.world_risk / self.world_risk_max)
        pyxel.rect(20, 12, risk_w, 5, 8)

        for o in self.objects:

            if o.name == "住人":
                pyxel.blt(o.x, o.y, self.img_npc, 0, 0, 40, 40)
            elif o.name == "影":
                pyxel.blt(o.x, o.y, self.img_shadow, 0, 0, 40, 40)
            else:
                pyxel.blt(o.x, o.y, self.img_door, 0, 0, 40, 40)

            pyxel.text(o.x, o.y - 6, o.name, 7, self.font)

            self.draw_bar(o.x, o.y + 45, o.hp, o.max_hp, 8)
            self.draw_bar(o.x, o.y + 50, o.mp, o.max_mp, 12)
            self.draw_bar(o.x, o.y + 55, o.tp, o.max_tp, 3)

        for c in self.cards:
            pyxel.blt(c.x, c.y, self.img_card, 0, 0, 50, 70)

            text_x = c.x + 4
            text_y = c.y + 4
            line_h = 8

            pyxel.text(text_x, text_y, f"{c.name}", 0, self.font)
            pyxel.text(text_x, text_y + line_h, f"ATK {c.atk}", 0, self.font)
            pyxel.text(text_x, text_y + line_h * 2, f"MGC {c.mgc}", 0, self.font)
            pyxel.text(text_x, text_y + line_h * 3, f"TEC {c.tec}", 0, self.font)
            pyxel.text(text_x, text_y + line_h * 4, f"SUC {c.success}%", 0, self.font)
            pyxel.text(text_x, text_y + line_h * 5, f"COST {c.cost}", 0, self.font)

        if self.popup_timer > 0:
            popup_w = 200
            popup_x = (WIDTH - popup_w) // 2
            popup_y = HEIGHT * 3 // 4

            if self.popup_success:
                bg = 3  # 緑系
                border = 11
                text_col = 0
            else:
                bg = 8  # 赤系
                border = 7
                text_col = 7

            pyxel.rect(popup_x, popup_y, popup_w, 24, bg)
            pyxel.rectb(popup_x, popup_y, popup_w, 24, border)
            pyxel.text(popup_x + 8, popup_y + 8, self.popup_text, text_col, self.font)


App()
