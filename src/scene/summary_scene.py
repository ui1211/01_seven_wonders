from __future__ import annotations

from src.scene.base_scene import BaseScene, SceneRuntime


class SummaryScene(BaseScene):
    def update(self, runtime: SceneRuntime, mx: int, my: int):
        pyxel = runtime.pyxel
        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return

        if runtime.hit_rect(
            mx,
            my,
            runtime.retry_btn_x,
            runtime.retry_btn_y,
            runtime.retry_btn_w,
            runtime.retry_btn_h,
        ):
            runtime.restart_round()

    def draw(self, runtime: SceneRuntime):
        pyxel = runtime.pyxel
        pyxel.cls(0)

        story = runtime.game.build_story_text()
        runtime.renderer.ui.draw_label_box(10, 40, runtime.width - 40, runtime.height - 120)

        max_chars = (runtime.width - 60) // 13
        lines = [story[i : i + max_chars] for i in range(0, len(story), max_chars)]

        y = 60
        for line in lines:
            runtime.renderer.text.draw(30, y, line, 7)
            y += 12

        runtime.renderer.ui.draw_button(
            runtime.retry_btn_x,
            runtime.retry_btn_y,
            runtime.retry_btn_w,
            runtime.retry_btn_h,
            "リトライ",
        )
