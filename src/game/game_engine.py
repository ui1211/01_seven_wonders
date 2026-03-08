# src/game/game_engine.py
from __future__ import annotations

import random
from enum import IntEnum

from src.data.cards import create_cards, create_reward_cards, create_topic_card
from src.round_scene_manager import RoundSceneManager


class SceneStatus(IntEnum):
    PLAY = 0
    RESULT = 1
    SUMMARY = 2
    BATTLE = 3
    TALK = 4


# Backward compatibility for existing imports
GameState = SceneStatus


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
        self.reward_cards = create_reward_cards()
        self.object_pool = object_pool

        self._state = SceneStatus.PLAY
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
        self.battle_enemy = None
        self.talk_target = None
        self.talk_topics = []
        self.talk_topic_cursor = 0
        self.info_modal_active = False
        self.info_modal_title = ""
        self.info_modal_text = ""

        self.dice_anim = False
        self.dice_timer = 0
        self.dice_duration = 36
        self.dice_stop_timer = 8
        self.dice_tens = 0
        self.dice_ones = 0
        self.dice_roll = None

        self._dice_card = None
        self._dice_obj = None
        self._dice_grave_xy = None
        self._dice_play_success = None
        self._dice_play_fail = None

    def reset_game(self):
        self.world_risk = 0
        self.set_scene_status(SceneStatus.PLAY)
        self.current_scene_id = 0
        self.round_index = 1
        self.round_results = []
        self.round_result_timer = 0
        self.pending_damage = {}
        self.damage_timer = 0
        self.popup_text = ""
        self.popup_timer = 0
        self.popup_success = True
        self.battle_enemy = None
        self.talk_target = None
        self.talk_topics = []
        self.talk_topic_cursor = 0
        self.info_modal_active = False
        self.info_modal_title = ""
        self.info_modal_text = ""

        self.anim_card = None
        self._anim_phase = None
        self._anim_t = 0
        self._anim_dur = 0
        self._anim_from = (0, 0)
        self._anim_to = (0, 0)
        self._anim_target_obj = None
        self._pending_grave_xy = None
        self._return_anims = {}

        self.dice_anim = False
        self.dice_timer = 0
        self.dice_tens = 0
        self.dice_ones = 0
        self.dice_roll = None
        self.dice_wait_timer = 0
        self.dice_wait_duration = 25
        self._dice_card = None
        self._dice_obj = None
        self._dice_grave_xy = None
        self._dice_play_success = None
        self._dice_play_fail = None

        for c in self.cards:
            c.in_graveyard = False
            c.drag = False

    def start_round(self, slots):
        self.set_scene_status(SceneStatus.PLAY)
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
        self.battle_enemy = None
        self.talk_target = None
        self.talk_topics = []
        self.talk_topic_cursor = 0
        self.info_modal_active = False
        self.info_modal_title = ""
        self.info_modal_text = ""

        self.dice_anim = False
        self.dice_timer = 0
        self.dice_tens = 0
        self.dice_ones = 0
        self.dice_roll = None
        self._dice_card = None
        self._dice_obj = None
        self._dice_grave_xy = None
        self._dice_play_success = None
        self._dice_play_fail = None

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
            is_enemy=o.is_enemy,
            can_talk=o.can_talk,
            topics=o.topics,
        )

    def is_animating(self, card) -> bool:
        return self.anim_card == card

    def can_play_card(self, card) -> bool:
        if self.state not in (SceneStatus.PLAY, SceneStatus.BATTLE, SceneStatus.TALK):
            return False
        if self.info_modal_active:
            return False
        if self.damage_timer > 0:
            return False
        if self.anim_card is not None:
            return False
        if self.dice_anim:
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

        self._dice_card = card
        self._dice_obj = obj
        self._dice_grave_xy = grave_next_xy
        self._dice_play_success = play_success
        self._dice_play_fail = play_fail

        self.dice_anim = True
        self.dice_timer = self.dice_duration
        self.dice_tens = random.randint(0, 9)
        self.dice_ones = random.randint(0, 9)
        self.dice_roll = None

    def update_timers(self):
        if self.popup_timer > 0:
            self.popup_timer -= 1

        if self.state == SceneStatus.RESULT and self.round_result_timer > 0:
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

        if self.dice_anim:
            if self.dice_timer > 0:
                self.dice_timer -= 1

                if self.dice_timer > self.dice_stop_timer:
                    self.dice_tens = random.randint(0, 9)
                    self.dice_ones = random.randint(0, 9)
                elif self.dice_timer == self.dice_stop_timer:
                    self.dice_tens = random.randint(0, 9)
                    self.dice_ones = random.randint(0, 9)

                    roll = self.dice_tens * 10 + self.dice_ones
                    if roll == 0:
                        roll = 100
                    self.dice_roll = roll

                    card = self._dice_card
                    obj = self._dice_obj
                    start_state = self.state
                    success = roll <= card.success

                    self.popup_success = success
                    self.popup_text = f"{'成功' if success else '失敗'} 目標:{card.success} 出目:{roll}"
                    self.popup_timer = 60

                    base_dmg = {"hp": card.atk, "mp": card.mgc, "tp": card.tec}
                    self._apply_risk(card.cost)

                    if success:
                        self._dice_play_success()
                        target_obj = obj
                        dmg_map = base_dmg
                        self._apply_risk(self.success_cost)
                    else:
                        self._dice_play_fail()
                        alive_objs = [o for o in self.objects if o.alive]
                        target_obj = random.choice(alive_objs) if alive_objs else obj
                        status_keys = ["hp", "mp", "tp"]
                        dmg_values = [card.atk, card.mgc, card.tec]
                        dmg_map = {status_keys[i]: dmg_values[i] for i in range(3) if dmg_values[i] > 0}
                        self._apply_risk(self.fail_cost)

                    # TALK scene uses topic objects; only TEC success resolves topic,
                    # and target object's TEC is reduced on both success/fail.
                    if self.state == SceneStatus.TALK and getattr(obj, "is_talk_topic", False):
                        tec_damage = max(0, int(card.tec))
                        if tec_damage <= 0:
                            tec_damage = max(0, int(card.atk), int(card.mgc))
                        talk_target = self.talk_target if self.talk_target is not None else obj
                        topic_index = int(getattr(obj, "topic_index", -1))
                        success = bool(success and int(card.tec) > 0)
                        self.popup_success = success

                        if success and 0 <= topic_index < len(self.talk_topics):
                            self.talk_topics[topic_index]["resolved"] = True
                            topic_text = str(self.talk_topics[topic_index].get("text", "話題"))
                            topic_card = create_topic_card(topic_text)
                            where, granted = self._grant_card(topic_card, prefer_hand=True)
                            info = f"{topic_text}の情報を獲得。{granted.name}を{('手札' if where == 'hand' else '山札')}に追加。"
                            self.open_info_modal("情報獲得", info)

                        target_obj = talk_target
                        dmg_map = {"tp": tec_damage} if tec_damage > 0 else {}

                    self.last_play = {
                        "card_name": getattr(card, "name", ""),
                        "target_name": getattr(target_obj, "name", ""),
                        "success": bool(success),
                    }

                    self.pending_damage = (
                        {
                            target_obj: {
                                dtype: {"start": getattr(target_obj, dtype), "damage": dmg}
                                for dtype, dmg in dmg_map.items()
                                if dmg > 0
                            }
                        }
                        if dmg_map
                        else {}
                    )
                    self.damage_timer = self.damage_duration if self.pending_damage else 0

                    self.anim_card = card
                    self._anim_target_obj = target_obj
                    self._pending_grave_xy = self._dice_grave_xy

                    self._anim_phase = "to_obj"
                    self._anim_dur = 12
                    self._anim_t = self._anim_dur
                    self._anim_from = (int(card.x), int(card.y))
                    self._anim_to = (int(target_obj.x + target_obj.w // 2), int(target_obj.y + target_obj.h // 2))

                    # Enter battle immediately when ATK damage is applied to an enemy.
                    if (
                        self.state == SceneStatus.PLAY
                        and dmg_map.get("hp", 0) > 0
                        and getattr(target_obj, "is_enemy", False)
                    ):
                        self.enter_battle(target_obj)
                    elif (
                        self.state == SceneStatus.PLAY
                        and dmg_map.get("tp", 0) > 0
                        and getattr(target_obj, "can_talk", False)
                    ):
                        self.enter_talk(target_obj)

                    if start_state == SceneStatus.BATTLE:
                        counter = random.randint(4, 12)
                        self._apply_risk(counter)
                        self.popup_text = f"{self.popup_text} / 反撃! 危険度+{counter}"
                        self.popup_success = False
                        self.popup_timer = 70

            if self.dice_timer <= 0:
                self.dice_anim = False
                self._dice_card = None
                self._dice_obj = None
                self._dice_grave_xy = None
                self._dice_play_success = None
                self._dice_play_fail = None

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
        if self.state != SceneStatus.RESULT:
            return
        if self.round_result_timer > 0:
            return

        if self.round_index < self.max_rounds:
            self.round_index += 1
            return "next_round"

        self.set_scene_status(SceneStatus.SUMMARY)
        return "to_summary"

    def resolve_object(self, obj, dmg_type):
        if self.state == SceneStatus.TALK and obj is self.talk_target and dmg_type == "tp":
            self._grant_random_reward(obj, dmg_type)
            self.finish_talk()
            return
        self._grant_random_reward(obj, dmg_type)
        next_scene = obj.scene_map.get(dmg_type)
        if next_scene is not None:
            self.current_scene_id = next_scene
            self.finish_round(reason="clear")

    def finish_round(self, reason: str):
        if self.state in (SceneStatus.RESULT, SceneStatus.SUMMARY):
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
            self.set_scene_status(SceneStatus.SUMMARY)
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

        self.set_scene_status(SceneStatus.RESULT)
        self.round_result_timer = 15

    @property
    def state(self) -> SceneStatus:
        return self._state

    @state.setter
    def state(self, value):
        self._state = SceneStatus(value)

    def set_scene_status(self, status: SceneStatus):
        self._state = SceneStatus(status)

    def is_scene_status(self, status: SceneStatus) -> bool:
        return self._state == SceneStatus(status)

    def open_info_modal(self, title: str, text: str):
        self.info_modal_active = True
        self.info_modal_title = str(title)
        self.info_modal_text = str(text)

    def close_info_modal(self):
        self.info_modal_active = False
        self.info_modal_title = ""
        self.info_modal_text = ""

    def _clone_card(self, card):
        if hasattr(card, "clone"):
            return card.clone()
        from src.model.card import Card

        return Card(card.name, card.success, card.atk, card.mgc, card.tec, card.cost)

    def _grant_card(self, card, prefer_hand: bool = True):
        c = self._clone_card(card)
        c.in_graveyard = False
        c.drag = False
        if prefer_hand and len(self.hand) < self.max_hand_size:
            self.hand.append(c)
            return "hand", c
        self.deck.append(c)
        random.shuffle(self.deck)
        return "deck", c

    def _enhance_random_card(self):
        pool = [c for c in [*self.hand, *self.deck] if not c.in_graveyard]
        if not pool:
            return None, ""
        target = random.choice(pool)
        mode = random.choice(["atk", "mgc", "tec", "cost"])
        if mode == "cost":
            before = target.cost
            target.enhance("cost", -2)
            return target, f"{target.name}: COST {before}->{target.cost}"
        before = getattr(target, mode)
        target.enhance(mode, 3)
        return target, f"{target.name}: {mode.upper()} {before}->{before + 3}"

    def _grant_random_reward(self, defeated_obj, by_type: str):
        reward_kind = random.choice(["card", "enhance", "draw"])
        if reward_kind == "card":
            bonus = random.choice(self.reward_cards)
            where, granted = self._grant_card(bonus, prefer_hand=True)
            self.popup_text = f"報酬: {granted.name} を{('手札' if where == 'hand' else '山札')}に追加"
            self.popup_success = True
            self.popup_timer = 70
            return
        if reward_kind == "enhance":
            _target, msg = self._enhance_random_card()
            if msg:
                self.popup_text = f"報酬: 強化! {msg}"
            else:
                self.popup_text = "報酬: 強化対象なし"
            self.popup_success = True
            self.popup_timer = 70
            return

        draw_n = 2 if by_type == "tp" else 1
        drawn = 0
        for _ in range(draw_n):
            if self._draw_one_reward():
                drawn += 1
        self.popup_text = f"報酬: {drawn}枚ドロー"
        self.popup_success = True
        self.popup_timer = 70

    def _draw_one_reward(self):
        if len(self.hand) >= self.max_hand_size:
            return False
        if not self.deck:
            if not self.graveyard:
                return False
            self.deck = self.graveyard
            self.graveyard = []
            random.shuffle(self.deck)
        if not self.deck:
            return False
        card = self.deck.pop()
        card.in_graveyard = False
        card.drag = False
        self.hand.append(card)
        return True

    def enter_battle(self, obj):
        if obj is None:
            return
        if not getattr(obj, "alive", False):
            return
        if not getattr(obj, "is_enemy", False):
            return
        self.battle_enemy = obj
        self.set_scene_status(SceneStatus.BATTLE)

    def exit_battle(self):
        self.battle_enemy = None
        self.set_scene_status(SceneStatus.PLAY)

    def finish_battle(self):
        enemy = self.battle_enemy
        if enemy is not None:
            next_scene = enemy.scene_map.get("hp")
            if next_scene is not None:
                self.current_scene_id = next_scene
        self.battle_enemy = None
        self.finish_round(reason="clear")

    def enter_talk(self, obj):
        if obj is None:
            return
        if not getattr(obj, "alive", False):
            return
        if not getattr(obj, "can_talk", False):
            return

        self.talk_target = obj
        self.talk_topic_cursor = 0
        topics = [str(t) for t in getattr(obj, "topics", []) if str(t).strip()]
        if not topics:
            topics = ["様子を伺う", "事情を聞く", "落ち着かせる"]
        self.talk_topics = [{"text": t, "resolved": False} for t in topics]
        self.set_scene_status(SceneStatus.TALK)

    def finish_talk(self):
        target = self.talk_target
        if target is not None:
            next_scene = target.scene_map.get("tp")
            if next_scene is not None:
                self.current_scene_id = next_scene
        self.talk_target = None
        self.talk_topics = []
        self.talk_topic_cursor = 0
        self.finish_round(reason="clear")

    def _apply_risk(self, amount: int):
        self.world_risk += amount
        self.world_risk = max(0, min(self.world_risk, self.world_risk_max))

        if self.world_risk >= self.world_risk_max:
            self.finish_round(reason="risk")

    def build_story_text(self):
        connectors = ["そして", "やがて", "次に", "さらに", "その後"]

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
                prefix = connectors[(i - 1) % len(connectors)] + "。"

            segs = []

            if intro:
                segs.append(f"{intro}{result}")

            if kind == "risk":
                pass

            parts.append(prefix + "".join(segs))

        return "".join(parts)


