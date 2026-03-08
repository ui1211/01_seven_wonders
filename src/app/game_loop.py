from __future__ import annotations

from src.scene.base_scene import SceneRuntime
from src.scene.scene_router import SceneRouter


class GameLoop:
    def __init__(
        self,
        pyxel,
        width: int,
        height: int,
        scene_manager,
        layout,
        input_controller,
        game,
        renderer,
        images: dict,
    ):
        self.pyxel = pyxel
        self.width = int(width)
        self.height = int(height)

        retry_btn_x = 70
        retry_btn_y = self.height - 34
        retry_btn_w = 100
        retry_btn_h = 20

        result_btn_x = 70
        result_btn_y = self.height // 2 + 20
        result_btn_w = 100
        result_btn_h = 20

        self.runtime = SceneRuntime(
            pyxel=pyxel,
            width=self.width,
            height=self.height,
            scene_manager=scene_manager,
            layout=layout,
            input_controller=input_controller,
            game=game,
            renderer=renderer,
            images=images,
            retry_btn_x=retry_btn_x,
            retry_btn_y=retry_btn_y,
            retry_btn_w=retry_btn_w,
            retry_btn_h=retry_btn_h,
            result_btn_x=result_btn_x,
            result_btn_y=result_btn_y,
            result_btn_w=result_btn_w,
            result_btn_h=result_btn_h,
        )

        self.scene_router = SceneRouter.create_default()

    def update(self):
        pyxel = self.pyxel
        game = self.runtime.game
        layout = self.runtime.layout
        renderer = self.runtime.renderer

        mx, my = pyxel.mouse_x, pyxel.mouse_y

        hand_poses = layout.hand_poses(game.hand, mx, my, renderer.card.card_w, renderer.card.card_h)
        grave_poses = layout.graveyard_poses(game.graveyard)

        game.update_timers()
        game.update_motion(
            hand_poses=hand_poses,
            grave_poses=grave_poses,
            grave_next_xy=layout.graveyard_next_xy(len(game.graveyard)),
        )

        self.scene_router.update(game.state, self.runtime, mx, my)

    def draw(self):
        self.pyxel.cls(1)
        self.scene_router.draw(self.runtime.game.state, self.runtime)
