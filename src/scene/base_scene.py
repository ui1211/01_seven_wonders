from __future__ import annotations

from dataclasses import dataclass


STARTING_OBJECT_SLOT_COUNT = 3


@dataclass
class SceneRuntime:
    pyxel: object
    width: int
    height: int
    scene_manager: object
    layout: object
    input_controller: object
    game: object
    renderer: object
    images: dict
    retry_btn_x: int
    retry_btn_y: int
    retry_btn_w: int
    retry_btn_h: int
    result_btn_x: int
    result_btn_y: int
    result_btn_w: int
    result_btn_h: int

    def deck_rect(self):
        zone_y = int(self.height * 0.72)
        deck_x = int(self.width * 0.05)
        return deck_x, zone_y, self.renderer.card.card_w, self.renderer.card.card_h

    @staticmethod
    def hit_rect(mx: int, my: int, x: int, y: int, w: int, h: int) -> bool:
        return x <= mx <= x + w and y <= my <= y + h

    def restart_round(self):
        self.game.reset_game()
        self.game.build_deck()
        self.game.draw_initial_hand()
        slots = self.layout.object_slots(STARTING_OBJECT_SLOT_COUNT)
        self.game.start_round(slots)


class BaseScene:
    def update(self, runtime: SceneRuntime, mx: int, my: int):
        return None

    def draw(self, runtime: SceneRuntime):
        return None
