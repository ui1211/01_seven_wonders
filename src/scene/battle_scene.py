from __future__ import annotations

from src.scene.base_scene import SceneRuntime
from src.scene.card_game_scene_base import CardGameSceneBase


class BattleScene(CardGameSceneBase):
    def __init__(self):
        self._enemy_id = None
        self._anim_t = 0
        self._anim_dur = 18
        self._from = (0, 0)

    @staticmethod
    def _smoothstep(t: float) -> float:
        if t <= 0:
            return 0.0
        if t >= 1:
            return 1.0
        return t * t * (3.0 - 2.0 * t)

    def _ensure_anim_setup(self, runtime: SceneRuntime):
        enemy = runtime.game.battle_enemy
        eid = id(enemy) if enemy is not None else None
        if eid == self._enemy_id:
            return

        self._enemy_id = eid
        if enemy is None:
            self._anim_t = 0
            return

        self._from = (int(enemy.x), int(enemy.y))
        self._anim_t = self._anim_dur

    def _center_pos(self, runtime: SceneRuntime):
        obj_w = runtime.renderer.obj.object_w
        obj_h = runtime.renderer.obj.object_h
        wx, wy, ww, wh = self._battle_window_rect(runtime)
        cx = wx + ww // 2 - obj_w // 2
        cy = wy + wh // 2 - obj_h // 2 + 6
        return cx, cy

    def _battle_window_rect(self, runtime: SceneRuntime):
        deck_x, deck_y, deck_w, deck_h = runtime.deck_rect()
        _ = (deck_x, deck_w, deck_h)

        x = 14
        y = 24
        w = runtime.width - 28
        bottom = deck_y - 18
        h = max(64, bottom - y)
        return x, y, w, h

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

    def update(self, runtime: SceneRuntime, mx: int, my: int):
        self._ensure_anim_setup(runtime)

        if self._anim_t > 0:
            self._anim_t -= 1

        enemy = runtime.game.battle_enemy
        if enemy is None or not getattr(enemy, "alive", False):
            return

        x, y = self._current_pos(runtime)
        enemy.x = x
        enemy.y = y
        enemy.w = runtime.renderer.obj.object_w
        enemy.h = runtime.renderer.obj.object_h

        self._update_card_game(runtime, mx, my, [enemy])

    def draw(self, runtime: SceneRuntime):
        pyxel = runtime.pyxel
        pyxel.cls(0)
        self._ensure_anim_setup(runtime)

        enemy = runtime.game.battle_enemy
        enemy_name = getattr(enemy, "name", "")

        draw_targets = []
        if enemy is not None:
            x, y = self._current_pos(runtime)
            enemy.x, enemy.y = x, y
            draw_targets = [enemy]

        # Battle window is part of background layer, not foreground UI.
        wx, wy, ww, wh = self._battle_window_rect(runtime)
        runtime.renderer.ui.draw_label_box(wx, wy, ww, wh)

        self._draw_card_game(runtime, draw_targets)

        runtime.renderer.text.draw_center(runtime.width // 2, wy + 14, "BATTLE", 8)
        runtime.renderer.text.draw_center(runtime.width // 2, wy + 30, f"Enemy: {enemy_name}", 7)
