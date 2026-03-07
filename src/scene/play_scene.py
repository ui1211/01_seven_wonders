from __future__ import annotations

from src.scene.base_scene import BaseScene, SceneRuntime


class PlayScene(BaseScene):
    def update(self, runtime: SceneRuntime, mx: int, my: int):
        pyxel = runtime.pyxel
        game = runtime.game
        layout = runtime.layout
        renderer = runtime.renderer

        hand_poses = layout.hand_poses(game.hand, mx, my, renderer.card.card_w, renderer.card.card_h)

        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            runtime.input_controller.on_mouse_move(mx, my)

        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            card, obj = runtime.input_controller.on_mouse_up(game.objects, mx, my)

            if card is not None:
                if obj is not None and obj.alive and game.can_play_card(card):
                    game.play_card(
                        card,
                        obj,
                        play_success=lambda: pyxel.play(0, 2),
                        play_fail=lambda: pyxel.play(0, 3),
                        grave_next_xy=layout.graveyard_next_xy(len(game.graveyard)),
                    )
                else:
                    game.request_return_to_hand(card)

        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return

        deck_x, deck_y, w, h = runtime.deck_rect()
        if runtime.hit_rect(mx, my, deck_x, deck_y, w, h):
            game.draw_one()
            return

        runtime.input_controller.on_mouse_down(
            cards=game.hand,
            hand_poses=hand_poses,
            mx=mx,
            my=my,
            card_w=renderer.card.card_w,
            card_h=renderer.card.card_h,
        )

    def draw(self, runtime: SceneRuntime):
        pyxel = runtime.pyxel
        game = runtime.game
        renderer = runtime.renderer

        renderer.hud.draw(
            game.round_index,
            game.max_rounds,
            game.world_risk,
            game.world_risk_max,
        )

        for obj in game.objects:
            renderer.obj.draw(obj)

        grave_poses = runtime.layout.graveyard_poses(game.graveyard)
        all_poses = {}
        all_poses.update(grave_poses)
        all_poses.update(
            runtime.layout.hand_poses(
                game.hand,
                pyxel.mouse_x,
                pyxel.mouse_y,
                renderer.card.card_w,
                renderer.card.card_h,
            )
        )

        all_cards = list({*game.hand, *game.graveyard})
        all_cards.sort(key=lambda c: getattr(all_poses.get(c), "z", 0))

        for card in all_cards:
            if game.is_animating(card):
                continue

            pose = all_poses.get(card)
            if pose is None:
                continue

            renderer.card.draw(card, pose.x, pose.y, pose.scale)

        if game.anim_card is not None:
            renderer.card.draw(
                game.anim_card,
                game.anim_card.x,
                game.anim_card.y,
                1.12,
            )

        if game.dice_anim:
            renderer.dice.draw(pyxel, game)

        if game.popup_timer > 0:
            renderer.ui.draw_popup(
                runtime.layout,
                game.popup_text,
                game.popup_success,
            )

        if game.recycling:
            renderer.text.draw_center(runtime.width // 2, runtime.height // 2, "SHUFFLE...", 8)

        deck_x, deck_y, w, h = runtime.deck_rect()
        if game.deck:
            pyxel.blt(deck_x, deck_y, runtime.images["card"], 0, 0, w, h)
            renderer.text.draw(deck_x + 6, deck_y + h + 2, f"{len(game.deck)}", 7)

            if len(game.hand) < game.max_hand_size and (pyxel.frame_count // 30) % 2 == 0:
                renderer.text.draw_center(int(deck_x + w // 2.5), deck_y - 12, "DRAW ME!", 6)

        renderer.ui.draw_label_box(20, int(runtime.height / 4 - 60), runtime.width - 40, 30)
        renderer.text.draw(30, int(runtime.height / 4 - 50), game.current_intro_text, 7)
