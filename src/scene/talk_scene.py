from __future__ import annotations

from dataclasses import dataclass

from src.scene.base_scene import SceneRuntime
from src.scene.card_game_scene_base import CardGameSceneBase


@dataclass
class TopicBubble:
    topic_index: int
    name: str
    text: str
    x: int = 0
    y: int = 0
    w: int = 72
    h: int = 28
    alive: bool = True
    hp: int = 1
    mp: int = 1
    tp: int = 1
    max_hp: int = 1
    max_mp: int = 1
    max_tp: int = 1
    is_talk_topic: bool = True


class TalkScene(CardGameSceneBase):
    def __init__(self):
        self._target_id = None
        self._anim_t = 0
        self._anim_dur = 18
        self._from = (0, 0)
        self._topic_tick = 0
        self._topic_interval = 120
        self._last_cursor_key = ()

    @staticmethod
    def _smoothstep(t: float) -> float:
        if t <= 0:
            return 0.0
        if t >= 1:
            return 1.0
        return t * t * (3.0 - 2.0 * t)

    def _ensure_anim_setup(self, runtime: SceneRuntime):
        target = runtime.game.talk_target
        tid = id(target) if target is not None else None
        if tid == self._target_id:
            return

        self._target_id = tid
        self._topic_tick = 0
        self._last_cursor_key = ()
        if target is None:
            self._anim_t = 0
            return

        self._from = (int(target.x), int(target.y))
        self._anim_t = self._anim_dur

    def _window_rect(self, runtime: SceneRuntime):
        _deck_x, deck_y, _deck_w, _deck_h = runtime.deck_rect()
        x = 14
        y = 20
        w = runtime.width - 28
        h = max(72, (deck_y - 22) - y)
        return x, y, w, h

    def _center_pos(self, runtime: SceneRuntime):
        wx, wy, ww, wh = self._window_rect(runtime)
        obj_w = runtime.renderer.obj.object_w
        obj_h = runtime.renderer.obj.object_h
        cx = wx + ww // 2 - obj_w // 2
        cy = wy + wh // 2 - obj_h // 2 + 6
        return cx, cy

    def _current_pos(self, runtime: SceneRuntime):
        cx, cy = self._center_pos(runtime)
        if self._anim_t <= 0:
            return cx, cy

        p = 1.0 - (self._anim_t / self._anim_dur)
        p = self._smoothstep(p)
        sx, sy = self._from
        x = int(sx + (cx - sx) * p)
        y = int(sy + (cy - sy) * p)
        return x, y

    def _visible_topic_indices(self, runtime: SceneRuntime):
        topics = runtime.game.talk_topics or []
        unresolved = [i for i, t in enumerate(topics) if not t.get("resolved", False)]
        if not unresolved:
            return []
        if len(unresolved) <= 3:
            return unresolved

        key = tuple(unresolved)
        if key != self._last_cursor_key:
            runtime.game.talk_topic_cursor = 0
            self._last_cursor_key = key

        self._topic_tick += 1
        if self._topic_tick >= self._topic_interval:
            self._topic_tick = 0
            runtime.game.talk_topic_cursor = (runtime.game.talk_topic_cursor + 1) % len(unresolved)

        start = runtime.game.talk_topic_cursor % len(unresolved)
        return [unresolved[(start + i) % len(unresolved)] for i in range(3)]

    def _build_bubbles(self, runtime: SceneRuntime, target_x: int, target_y: int):
        topics = runtime.game.talk_topics or []
        indices = self._visible_topic_indices(runtime)
        if not indices:
            return []

        cx = target_x + runtime.renderer.obj.object_w // 2
        base_y = target_y - 46
        offsets = [-88, 0, 88]
        bubbles = []
        for offset, idx in zip(offsets, indices):
            text = str(topics[idx].get("text", "話題"))
            bubble = TopicBubble(topic_index=idx, name=text, text=text)
            bubble.x = int(cx + offset - bubble.w // 2)
            bubble.y = int(base_y - (10 if offset == 0 else 0))
            bubbles.append(bubble)
        return bubbles

    def _draw_bubble(self, runtime: SceneRuntime, bubble: TopicBubble):
        ui = runtime.renderer.ui
        text = runtime.renderer.text
        ui.draw_label_box(bubble.x, bubble.y, bubble.w, bubble.h)
        msg = bubble.text
        max_chars = max(4, (bubble.w - 8) // 8)
        if len(msg) > max_chars:
            msg = msg[: max_chars - 3] + "..."
        text.draw_center(bubble.x + bubble.w // 2, bubble.y + bubble.h // 2 - 4, msg, 7)

    def _info_modal_rect(self, runtime: SceneRuntime):
        w = min(220, runtime.width - 28)
        h = 84
        x = runtime.width // 2 - w // 2
        y = runtime.height // 2 - h // 2
        return x, y, w, h

    def _draw_info_modal(self, runtime: SceneRuntime):
        game = runtime.game
        if not game.info_modal_active:
            return

        x, y, w, h = self._info_modal_rect(runtime)
        runtime.renderer.ui.draw_label_box(x, y, w, h)
        runtime.renderer.text.draw_center(runtime.width // 2, y + 12, game.info_modal_title or "情報", 10)
        runtime.renderer.text.draw_center(runtime.width // 2, y + 32, game.info_modal_text or "", 7)
        runtime.renderer.ui.draw_button(x + w // 2 - 36, y + h - 24, 72, 16, "次へ")

    def _handle_info_modal_click(self, runtime: SceneRuntime, mx: int, my: int):
        game = runtime.game
        if not game.info_modal_active:
            return False
        pyxel = runtime.pyxel
        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return True

        x, y, w, h = self._info_modal_rect(runtime)
        bx = x + w // 2 - 36
        by = y + h - 24
        if runtime.hit_rect(mx, my, bx, by, 72, 16):
            game.close_info_modal()
        return True

    def update(self, runtime: SceneRuntime, mx: int, my: int):
        self._ensure_anim_setup(runtime)
        if self._anim_t > 0:
            self._anim_t -= 1

        if self._handle_info_modal_click(runtime, mx, my):
            return

        target = runtime.game.talk_target
        if target is None or not getattr(target, "alive", False):
            return

        x, y = self._current_pos(runtime)
        target.x = x
        target.y = y
        target.w = runtime.renderer.obj.object_w
        target.h = runtime.renderer.obj.object_h

        bubbles = self._build_bubbles(runtime, x, y)
        self._update_card_game(runtime, mx, my, bubbles)

    def draw(self, runtime: SceneRuntime):
        pyxel = runtime.pyxel
        pyxel.cls(0)
        self._ensure_anim_setup(runtime)

        target = runtime.game.talk_target
        target_name = getattr(target, "name", "")

        wx, wy, ww, wh = self._window_rect(runtime)
        runtime.renderer.ui.draw_label_box(wx, wy, ww, wh)

        bubbles = []
        if target is not None:
            x, y = self._current_pos(runtime)
            target.x, target.y = x, y
            runtime.renderer.obj.draw(target)
            bubbles = self._build_bubbles(runtime, x, y)

        for bubble in bubbles:
            self._draw_bubble(runtime, bubble)

        self._draw_card_game(runtime, [])
        runtime.renderer.text.draw_center(runtime.width // 2, wy + 12, "TALK", 8)
        runtime.renderer.text.draw_center(runtime.width // 2, wy + 28, f"Target: {target_name}", 7)
        self._draw_info_modal(runtime)
