from __future__ import annotations

from src.game.game_engine import GameState


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

        self.scene_manager = scene_manager
        self.layout = layout
        self.input = input_controller
        self.game = game
        self.renderer = renderer
        self.images = images

        self.retry_btn_x = 70
        self.retry_btn_y = self.height - 34
        self.retry_btn_w = 100
        self.retry_btn_h = 20

        self.result_btn_x = 70
        self.result_btn_y = self.height // 2 + 20
        self.result_btn_w = 100
        self.result_btn_h = 20

    def _deck_rect(self):
        zone_y = int(self.height * 0.72)
        deck_x = int(self.width * 0.05)
        return deck_x, zone_y, self.renderer.card.card_w, self.renderer.card.card_h

    def _hit_rect(self, mx: int, my: int, x: int, y: int, w: int, h: int) -> bool:
        return x <= mx <= x + w and y <= my <= y + h

    def _restart_round(self):
        self.game.reset_game()
        self.game.build_deck()
        self.game.draw_initial_hand()
        slots = self.layout.object_slots(3)
        self.game.start_round(slots)

    def update(self):
        pyxel = self.pyxel
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        hand_poses = self.layout.hand_poses(
            self.game.hand, mx, my, self.renderer.card.card_w, self.renderer.card.card_h
        )
        grave_poses = self.layout.graveyard_poses(self.game.graveyard)

        self.game.update_timers()

        self.game.update_motion(
            hand_poses=hand_poses,
            grave_poses=grave_poses,
            grave_next_xy=self.layout.graveyard_next_xy(len(self.game.graveyard)),
        )

        if self.game.state == GameState.SUMMARY:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                if self._hit_rect(
                    mx,
                    my,
                    self.retry_btn_x,
                    self.retry_btn_y,
                    self.retry_btn_w,
                    self.retry_btn_h,
                ):
                    self._restart_round()
            return

        if self.game.state == GameState.RESULT:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                if self._hit_rect(
                    mx,
                    my,
                    self.result_btn_x,
                    self.result_btn_y,
                    self.result_btn_w,
                    self.result_btn_h,
                ):
                    act = self.game.request_next()
                    if act == "next_round":
                        slots = self.layout.object_slots(3)
                        self.game.start_round(slots)
            return

        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            self.input.on_mouse_move(mx, my)

        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            card, obj = self.input.on_mouse_up(self.game.objects, mx, my)

            if card is not None:
                if obj is not None and obj.alive and self.game.can_play_card(card):
                    self.game.play_card(
                        card,
                        obj,
                        play_success=lambda: pyxel.play(0, 2),
                        play_fail=lambda: pyxel.play(0, 3),
                        grave_next_xy=self.layout.graveyard_next_xy(len(self.game.graveyard)),
                    )
                else:
                    self.game.request_return_to_hand(card)

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):

            deck_x, deck_y, w, h = self._deck_rect()

            if self._hit_rect(mx, my, deck_x, deck_y, w, h):
                self.game.draw_one()
            else:
                self.input.on_mouse_down(
                    cards=self.game.hand,
                    hand_poses=hand_poses,
                    mx=mx,
                    my=my,
                    card_w=self.renderer.card.card_w,
                    card_h=self.renderer.card.card_h,
                )

    def draw(self):

        pyxel = self.pyxel
        pyxel.cls(1)

        # ---------------------------
        # SUMMARY
        # ---------------------------

        if self.game.state == GameState.SUMMARY:

            pyxel.cls(0)

            story = self.game.build_story_text()

            self.renderer.ui.draw_label_box(10, 40, self.width - 40, self.height - 120)

            max_chars = (self.width - 60) // 13
            lines = [story[i : i + max_chars] for i in range(0, len(story), max_chars)]

            y = 60

            for line in lines:
                self.renderer.text.draw(30, y, line, 7)
                y += 12

            self.renderer.ui.draw_button(
                self.retry_btn_x,
                self.retry_btn_y,
                self.retry_btn_w,
                self.retry_btn_h,
                "リトライ",
            )

            return

        # ---------------------------
        # RESULT
        # ---------------------------

        if self.game.state == GameState.RESULT:

            pyxel.cls(0)

            text = self.scene_manager.get_text(self.game.current_scene_id)

            self.renderer.ui.draw_label_box(
                24,
                self.height // 2 - 20,
                self.width - 48,
                40,
            )

            self.renderer.text.draw_center(
                self.width // 2,
                self.height // 2 - 6,
                text,
                7,
            )

            label = "つづける" if self.game.round_index < self.game.max_rounds else "まとめへ"

            self.renderer.ui.draw_button(
                self.result_btn_x,
                self.result_btn_y,
                self.result_btn_w,
                self.result_btn_h,
                label,
            )

            return

        # ---------------------------
        # HUD
        # ---------------------------

        self.renderer.hud.draw(
            self.game.round_index,
            self.game.max_rounds,
            self.game.world_risk,
            self.game.world_risk_max,
        )

        # ---------------------------
        # OBJECT
        # ---------------------------

        for o in self.game.objects:
            self.renderer.obj.draw(o)

        # ---------------------------
        # CARD
        # ---------------------------

        grave_poses = self.layout.graveyard_poses(self.game.graveyard)

        all_poses = {}
        all_poses.update(grave_poses)
        all_poses.update(
            self.layout.hand_poses(
                self.game.hand,
                pyxel.mouse_x,
                pyxel.mouse_y,
                self.renderer.card.card_w,
                self.renderer.card.card_h,
            )
        )

        all_cards = list({*self.game.hand, *self.game.graveyard})
        all_cards.sort(key=lambda c: getattr(all_poses.get(c), "z", 0))

        for c in all_cards:

            if self.game.is_animating(c):
                continue

            p = all_poses.get(c)

            if p is None:
                continue

            self.renderer.card.draw(c, p.x, p.y, p.scale)

        if self.game.anim_card is not None:

            self.renderer.card.draw(
                self.game.anim_card,
                self.game.anim_card.x,
                self.game.anim_card.y,
                1.12,
            )

        # ---------------------------
        # DICE
        # ---------------------------

        if self.game.dice_anim:
            self.renderer.dice.draw(pyxel, self.game)

        # ---------------------------
        # POPUP
        # ---------------------------

        if self.game.popup_timer > 0:

            self.renderer.ui.draw_popup(
                self.layout,
                self.game.popup_text,
                self.game.popup_success,
            )

        # ---------------------------
        # SHUFFLE
        # ---------------------------

        if self.game.recycling:

            self.renderer.text.draw_center(
                self.width // 2,
                self.height // 2,
                "SHUFFLE...",
                8,
            )

        # ---------------------------
        # DECK
        # ---------------------------

        deck_x, deck_y, w, h = self._deck_rect()

        if self.game.deck:

            pyxel.blt(deck_x, deck_y, self.images["card"], 0, 0, w, h)

            self.renderer.text.draw(
                deck_x + 6,
                deck_y + h + 2,
                f"{len(self.game.deck)}",
                7,
            )

            if len(self.game.hand) < self.game.max_hand_size:

                if (pyxel.frame_count // 30) % 2 == 0:

                    self.renderer.text.draw_center(
                        int(deck_x + w // 2.5),
                        deck_y - 12,
                        "DRAW ME!",
                        6,
                    )

        # ---------------------------
        # INTRO
        # ---------------------------

        self.renderer.ui.draw_label_box(
            20,
            int(self.height / 4 - 60),
            self.width - 40,
            30,
        )

        self.renderer.text.draw(
            30,
            int(self.height / 4 - 50),
            self.game.current_intro_text,
            7,
        )
