from __future__ import annotations

from src.scene.base_scene import SceneRuntime
from src.scene.card_game_scene_base import CardGameSceneBase


class PlayScene(CardGameSceneBase):
    def update(self, runtime: SceneRuntime, mx: int, my: int):
        self._update_card_game(runtime, mx, my, runtime.game.objects)

    def draw(self, runtime: SceneRuntime):
        self._draw_card_game(runtime, runtime.game.objects, intro_text=runtime.game.current_intro_text)
