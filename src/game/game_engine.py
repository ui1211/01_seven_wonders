# src/game/game_engine.py
from __future__ import annotations

import random

from src.data.cards import create_cards
from src.round_scene_manager import RoundSceneManager


class GameState:
    PLAY = 0
    RESULT = 1
    SUMMARY = 2


def _smoothstep(t: float) -> float:
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    return t * t * (3.0 - 2.0 * t)


class GameEngine:
    def __init__(self, scene_manager, object_pool):
        self.scene_manager = scene_manager
        self.cards = create_cards()
        self.object_pool = object_pool

        self.state = GameState.PLAY
        self.current_scene_id = 0

        self.world_risk = 0
        self.world_risk_max = 100

        self.popup_text = ""
        self.popup_timer = 0
        self.popup_success = True

        self.pending_damage = {}
        self.damage_timer = 0
        self.damage_duration = 30

        self.deck = []
        self.hand = []
        self.graveyard = []
        self.init_hand_size = 5
        self.max_hand_size = 7
        self.max_deck_size = 12

        self.recycling = False
        self.recycle_timer = 0

        self.max_rounds = 5
        self.round_index = 1
        self.round_results = []
        self.round_result_timer = 0

        self.objects = []

        self.anim_card = None
        self._anim_phase = None
        self._anim_t = 0
        self._anim_dur = 0
        self._anim_from = (0, 0)
        self._anim_to = (0, 0)
        self._anim_target_obj = None
        self._pending_grave_xy = None

        self.draw_cost = 12
        self.fail_cost = 30
        self.success_cost = -5

        self._return_anims = {}

        self.round_scene_manager = RoundSceneManager()
        self.current_intro_text = ""
        self.last_play = None

    def reset_game(self):
        self.world_risk = 0
        self.state = GameState.PLAY
        self.current_scene_id = 0
        self.round_index = 1
        self.round_results = []
        self.round_result_timer = 0
        self.pending_damage = {}
        self.damage_timer = 0
        self.popup_text = ""
        self.popup_timer = 0
        self.popup_success = True

        self.anim_card = None
        self._anim_phase = None
        self._anim_t = 0
        self._anim_dur = 0
        self._anim_from = (0, 0)
        self._anim_to = (0, 0)
        self._anim_target_obj = None
        self._pending_grave_xy = None
        self._return_anims = {}

        for c in self.cards:
            c.in_graveyard = False
            c.drag = False

    def start_round(self, slots):
        self.state = GameState.PLAY
        self.current_scene_id = 0
        self.popup_text = ""
        self.popup_timer = 0
        self.popup_success = True
        self.pending_damage = {}
        self.damage_timer = 0

        self.anim_card = None
        self._anim_phase = None
        self._anim_t = 0
        self._anim_dur = 0
        self._anim_target_obj = None
        self._pending_grave_xy = None
        self._return_anims = {}
        self.last_play = None

        self.current_intro_text = self.round_scene_manager.start_round_intro()

        picked = random.sample(self.object_pool, k=min(len(slots), len(self.object_pool)))
        self.objects = []
        for (x, y), base in zip(slots, picked):
            o = self.clone_obj(base)
            o.x = x
            o.y = y
            o.alive = True
            self.objects.append(o)

    def build_deck(self):
        self.deck = random.sample([c for c in self.cards], self.max_deck_size)
        random.shuffle(self.deck)
        self.hand = []
        self.graveyard = []

        for c in self.deck:
            c.in_graveyard = False
            c.drag = False

    def draw_initial_hand(self):
        while len(self.hand) < self.init_hand_size and self.deck:  # self.max_hand_size and self.deck:
            self.hand.append(self.deck.pop())

    def draw_one(self):
        if len(self.hand) >= self.max_hand_size:
            return False

        if not self.deck:
            self.recycle_graveyard_to_deck()

        if not self.deck:
            return False

        card = self.deck.pop()
        card.in_graveyard = False
        card.drag = False
        self.hand.append(card)

        self._apply_risk(self.draw_cost)

        return True

    def recycle_graveyard_to_deck(self):
        if not self.graveyard or self.recycling:
            return

        self.recycling = True
        self.recycle_timer = 30

    def clone_obj(self, o):
        from src.model.object import Obj

        return Obj(
            o.name,
            o.max_hp,
            o.max_mp,
            o.max_tp,
            o.x,
            o.y,
            o.image_path,
            scene_hp=o.scene_map.get("hp"),
            scene_mp=o.scene_map.get("mp"),
            scene_tp=o.scene_map.get("tp"),
        )

    def is_animating(self, card) -> bool:
        return self.anim_card == card

    def can_play_card(self, card) -> bool:
        if self.state != GameState.PLAY:
            return False
        if self.damage_timer > 0:
            return False
        if self.anim_card is not None:
            return False
        if card.in_graveyard:
            return False
        return True

    def request_return_to_hand(self, card, dur: int = 10):
        if card is None:
            return
        if card.in_graveyard:
            return
        if self.anim_card is not None and self.anim_card == card:
            return
        if getattr(card, "drag", False):
            card.drag = False
        self._return_anims[card] = {"t": dur, "dur": dur, "from": (int(card.x), int(card.y))}

    def play_card(self, card, obj, play_success, play_fail, grave_next_xy):
        if not self.can_play_card(card):
            return

        card.drag = False

        roll = random.randint(1, 100)
        success = roll <= card.success

        self.popup_success = success
        self.popup_text = f"【{'成功' if success else '失敗'}】: 目標:{card.success} 出目:{roll} "
        self.popup_timer = 60

        base_dmg = {"hp": card.atk, "mp": card.mgc, "tp": card.tec}
        self._apply_risk(card.cost)

        if success:
            play_success()
            target_obj = obj
            dmg_map = base_dmg
            self._apply_risk(self.success_cost)
        else:
            play_fail()
            alive_objs = [o for o in self.objects if o.alive]
            target_obj = random.choice(alive_objs) if alive_objs else obj
            status_keys = ["hp", "mp", "tp"]
            dmg_values = [card.atk, card.mgc, card.tec]
            dmg_map = {status_keys[i]: dmg_values[i] for i in range(3) if dmg_values[i] > 0}
            self._apply_risk(self.fail_cost)

        self.last_play = {
            "card_name": getattr(card, "name", ""),
            "target_name": getattr(target_obj, "name", ""),
            "success": bool(success),
        }

        self.pending_damage = {
            target_obj: {
                dtype: {"start": getattr(target_obj, dtype), "damage": dmg} for dtype, dmg in dmg_map.items() if dmg > 0
            }
        }
        self.damage_timer = self.damage_duration

        self.anim_card = card
        self._anim_target_obj = target_obj
        self._pending_grave_xy = grave_next_xy

        self._anim_phase = "to_obj"
        self._anim_dur = 12
        self._anim_t = self._anim_dur
        self._anim_from = (int(card.x), int(card.y))
        self._anim_to = (int(target_obj.x + target_obj.w // 2), int(target_obj.y + target_obj.h // 2))

    def update_timers(self):
        if self.popup_timer > 0:
            self.popup_timer -= 1

        if self.state == GameState.RESULT and self.round_result_timer > 0:
            self.round_result_timer -= 1

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
                    for dtype, _info in dmg_map.items():
                        if getattr(obj, dtype) == 0 and obj.alive:
                            obj.alive = False
                            self.resolve_object(obj, dtype)
                            break
                self.pending_damage = {}

                if self.world_risk >= self.world_risk_max:
                    self.finish_round(reason="risk")

        if self.recycling:
            self.recycle_timer -= 1
            if self.recycle_timer <= 0:
                self.deck = self.graveyard
                self.graveyard = []
                random.shuffle(self.deck)
                self.recycling = False

    def update_motion(self, hand_poses, grave_poses, grave_next_xy):
        for card, st in list(self._return_anims.items()):
            if st["t"] <= 0:
                self._return_anims.pop(card, None)
                continue

            pose = hand_poses.get(card)
            if pose is None:
                st["t"] -= 1
                continue

            st["t"] -= 1
            p = 1 - (st["t"] / st["dur"])
            p = _smoothstep(p)

            sx, sy = st["from"]
            tx, ty = int(pose.x), int(pose.y)

            card.x = int(sx + (tx - sx) * p)
            card.y = int(sy + (ty - sy) * p)

            if st["t"] <= 0:
                card.x = int(pose.x)
                card.y = int(pose.y)
                self._return_anims.pop(card, None)

        if self.anim_card is None:
            return

        if self._anim_t <= 0:
            if self._anim_phase == "to_obj":
                self._anim_phase = "to_grave"
                self._anim_dur = 14
                self._anim_t = self._anim_dur
                self._anim_from = (int(self.anim_card.x), int(self.anim_card.y))
                if self._pending_grave_xy is None:
                    self._pending_grave_xy = grave_next_xy
                self._anim_to = (int(self._pending_grave_xy[0]), int(self._pending_grave_xy[1]))
                return

            if self._anim_phase == "to_grave":
                card = self.anim_card
                card.in_graveyard = True

                if card in self.hand:
                    self.hand.remove(card)
                if card not in self.graveyard:
                    self.graveyard.append(card)

                card.x = int(self._anim_to[0])
                card.y = int(self._anim_to[1])

                self.anim_card = None
                self._anim_phase = None
                self._anim_t = 0
                self._anim_dur = 0
                self._anim_target_obj = None
                self._pending_grave_xy = None

                if not self.deck and not self.hand and self.graveyard:
                    self.recycle_graveyard_to_deck()

                return

        self._anim_t -= 1
        p = 1 - (self._anim_t / self._anim_dur) if self._anim_dur > 0 else 1.0
        p = _smoothstep(p)

        sx, sy = self._anim_from
        tx, ty = self._anim_to

        self.anim_card.x = int(sx + (tx - sx) * p)
        self.anim_card.y = int(sy + (ty - sy) * p)

        if self._anim_phase == "to_obj" and self._anim_t <= 3 and self._pending_grave_xy is None:
            self._pending_grave_xy = grave_next_xy

    def request_next(self):
        if self.state != GameState.RESULT:
            return
        if self.round_result_timer > 0:
            return

        if self.round_index < self.max_rounds:
            self.round_index += 1
            return "next_round"

        self.state = GameState.SUMMARY
        return "to_summary"

    def resolve_object(self, obj, dmg_type):
        next_scene = obj.scene_map.get(dmg_type)
        if next_scene is not None:
            self.current_scene_id = next_scene
            self.finish_round(reason="clear")

    def finish_round(self, reason: str):
        if self.state in (GameState.RESULT, GameState.SUMMARY):
            return

        play = self.last_play or {"card_name": "", "target_name": "", "success": None}

        if reason == "risk":
            result_text = self.scene_manager.get_text(99)
            self.round_results.append(
                {
                    "round": self.round_index,
                    "intro": self.current_intro_text,
                    "play": play,
                    "result": result_text,
                    "kind": "risk",
                }
            )
            self.state = GameState.SUMMARY
            return

        result_text = self.scene_manager.get_text(self.current_scene_id)

        self.round_results.append(
            {
                "round": self.round_index,
                "intro": self.current_intro_text,
                "play": play,
                "result": result_text,
                "kind": "clear",
            }
        )

        self.state = GameState.RESULT
        self.round_result_timer = 15

    def _apply_risk(self, amount: int):
        self.world_risk += amount
        self.world_risk = max(0, min(self.world_risk, self.world_risk_max))

        if self.world_risk >= self.world_risk_max:
            self.finish_round(reason="risk")

    def build_story_text(self):
        connectors = ["その後", "やがて", "次に", "さらに", "そして"]

        parts = []
        for i, r in enumerate(self.round_results):
            intro = r.get("intro", "")
            result = r.get("result", "")
            kind = r.get("kind", "")

            play = r.get("play") or {}
            card_name = play.get("card_name", "")
            target_name = play.get("target_name", "")
            success = play.get("success", None)

            if i == 0:
                prefix = ""
            else:
                prefix = connectors[(i - 1) % len(connectors)] + "、"

            segs = []

            if intro:
                segs.append(f"{intro}{result}")

            if kind == "risk":
                pass

            parts.append(prefix + "".join(segs))

        return "".join(parts)
