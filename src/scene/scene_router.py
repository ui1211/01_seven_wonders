from __future__ import annotations

from src.game.game_engine import SceneStatus
from src.scene.base_scene import SceneRuntime
from src.scene.battle_scene import BattleScene
from src.scene.play_scene import PlayScene
from src.scene.result_scene import ResultScene
from src.scene.summary_scene import SummaryScene


class SceneRouter:
    def __init__(self, scenes: dict, fallback_status: SceneStatus = SceneStatus.PLAY):
        self._scenes = scenes
        self._fallback_status = fallback_status

    @classmethod
    def create_default(cls):
        return cls(
            scenes={
                SceneStatus.PLAY: PlayScene(),
                SceneStatus.BATTLE: BattleScene(),
                SceneStatus.RESULT: ResultScene(),
                SceneStatus.SUMMARY: SummaryScene(),
            }
        )

    def update(self, status: SceneStatus, runtime: SceneRuntime, mx: int, my: int):
        scene = self._resolve(status)
        scene.update(runtime, mx, my)

    def draw(self, status: SceneStatus, runtime: SceneRuntime):
        scene = self._resolve(status)
        scene.draw(runtime)

    def _resolve(self, status: SceneStatus):
        return self._scenes.get(SceneStatus(status), self._scenes[self._fallback_status])
