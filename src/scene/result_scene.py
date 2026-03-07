from __future__ import annotations

from src.scene.base_scene import BaseScene, SceneRuntime, STARTING_OBJECT_SLOT_COUNT


class ResultScene(BaseScene):
    def update(self, runtime: SceneRuntime, mx: int, my: int):
        pyxel = runtime.pyxel
        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return

        if not runtime.hit_rect(
            mx,
            my,
            runtime.result_btn_x,
            runtime.result_btn_y,
            runtime.result_btn_w,
            runtime.result_btn_h,
        ):
            return

        act = runtime.game.request_next()
        if act == "next_round":
            slots = runtime.layout.object_slots(STARTING_OBJECT_SLOT_COUNT)
            runtime.game.start_round(slots)

    def draw(self, runtime: SceneRuntime):
        pyxel = runtime.pyxel
        pyxel.cls(0)

        text = runtime.scene_manager.get_text(runtime.game.current_scene_id)
        runtime.renderer.ui.draw_label_box(24, runtime.height // 2 - 20, runtime.width - 48, 40)
        runtime.renderer.text.draw_center(runtime.width // 2, runtime.height // 2 - 6, text, 7)

        label = "つづける" if runtime.game.round_index < runtime.game.max_rounds else "まとめへ"
        runtime.renderer.ui.draw_button(
            runtime.result_btn_x,
            runtime.result_btn_y,
            runtime.result_btn_w,
            runtime.result_btn_h,
            label,
        )
