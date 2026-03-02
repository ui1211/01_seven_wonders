# main.py
import pyxel

from src.data.objects import create_object_pool
from src.game.game_engine import GameEngine, GameState
from src.option import HEIGHT, WIDTH
from src.scene_manager import SceneManager
from src.ui.input_controller import InputController
from src.ui.layout_manager import LayoutManager
from src.ui.renderer import Renderer


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="B Demo")
        pyxel.mouse(True)

        self.font = pyxel.Font("assets/misaki_gothic.bdf")
        self.scene_manager = SceneManager()

        self.layout = LayoutManager(WIDTH, HEIGHT)
        self.input = InputController()

        self.object_pool = create_object_pool()
        self.game = GameEngine(self.scene_manager, self.object_pool)

        self.images = self.load_images()
        self.renderer = Renderer(self.font, self.images, WIDTH, HEIGHT)

        self.init_sounds()
        self.game.build_deck()
        self.game.draw_initial_hand()

        slots = self.layout.object_slots(3)
        self.game.start_round(slots)

        pyxel.run(self.update, self.draw)

    def load_images(self):
        images = {}

        raw_card = pyxel.Image.from_image("./assets/images/trading_card03_yellow.png")
        images["card"] = self.resize_image(raw_card, 50, 70)

        for obj in self.object_pool:
            path = obj.image_path
            if path not in images:
                raw = pyxel.Image.from_image(path)
                images[path] = self.resize_image(raw, 40, 40)

        return images

    def init_sounds(self):
        pyxel.sound(1).set("c2", "t", "7", "n", 15)
        pyxel.sound(2).set("c4e4", "p", "7", "f", 10)
        pyxel.sound(3).set("g2f2", "n", "6", "f", 20)

    def resize_image(self, src, w, h):
        dst = pyxel.Image(w, h)
        for y in range(h):
            for x in range(w):
                sx = int(x * src.width / w)
                sy = int(y * src.height / h)
                dst.pset(x, y, src.pget(sx, sy))
        return dst

    def _deck_rect(self):
        zone_y = int(HEIGHT * 0.72)
        deck_x = int(WIDTH * 0.05)
        return deck_x, zone_y, self.renderer.card_w, self.renderer.card_h

    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        hand_poses = self.layout.hand_poses(self.game.hand, mx, my, self.renderer.card_w, self.renderer.card_h)
        grave_poses = self.layout.graveyard_poses(self.game.graveyard)

        self.game.update_timers()
        self.game.update_motion(
            hand_poses=hand_poses,
            grave_poses=grave_poses,
            grave_next_xy=self.layout.graveyard_next_xy(len(self.game.graveyard)),
        )

        if self.game.state == GameState.SUMMARY:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                mx, my = pyxel.mouse_x, pyxel.mouse_y

                btn_x = 70
                btn_y = HEIGHT - 34
                btn_w = 100
                btn_h = 20

                if btn_x <= mx <= btn_x + btn_w and btn_y <= my <= btn_y + btn_h:
                    self.game.reset_game()
                    self.game.build_deck()
                    self.game.draw_initial_hand()
                    slots = self.layout.object_slots(3)
                    self.game.start_round(slots)

            return

        if self.game.state == GameState.RESULT:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
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
            if deck_x < mx < deck_x + w and deck_y < my < deck_y + h:
                self.game.draw_one()
            else:
                self.input.on_mouse_down(
                    cards=self.game.hand,
                    hand_poses=hand_poses,
                    mx=mx,
                    my=my,
                    card_w=self.renderer.card_w,
                    card_h=self.renderer.card_h,
                )

    def draw(self):
        pyxel.cls(1)

        if self.game.state == GameState.SUMMARY:
            pyxel.cls(0)

            story = self.game.build_story_text()

            self.renderer.draw_label_box(pyxel, 20, 40, WIDTH - 40, HEIGHT - 120)

            max_chars = (WIDTH - 60) // 8
            lines = [story[i : i + max_chars] for i in range(0, len(story), max_chars)]

            y = 60
            for line in lines:
                self.renderer.draw_text(pyxel, 30, y, line, 7)
                y += 12

            self.renderer.draw_button(pyxel, 70, HEIGHT - 34, 100, 20, "リトライ")
            return

        if self.game.state == GameState.RESULT:
            pyxel.cls(0)
            text = self.scene_manager.get_text(self.game.current_scene_id)
            self.renderer.draw_label_box(pyxel, 24, HEIGHT // 2 - 20, WIDTH - 48, 40)
            self.renderer.draw_text_center(pyxel, WIDTH // 2, HEIGHT // 2 - 6, text, 7)
            label = "つづける" if self.game.round_index < self.game.max_rounds else "まとめへ"
            self.renderer.draw_button(pyxel, 70, HEIGHT // 2 + 20, 100, 20, label)
            return

        self.renderer.draw_hud(
            pyxel, self.game.round_index, self.game.max_rounds, self.game.world_risk, self.game.world_risk_max
        )

        for o in self.game.objects:
            self.renderer.draw_object(pyxel, o)

        grave_poses = self.layout.graveyard_poses(self.game.graveyard)
        all_poses = {}
        all_poses.update(grave_poses)
        all_poses.update(
            self.layout.hand_poses(
                self.game.hand, pyxel.mouse_x, pyxel.mouse_y, self.renderer.card_w, self.renderer.card_h
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
            self.renderer.draw_card(pyxel, c, p)

        if self.game.anim_card is not None:
            self.renderer.draw_card_at(
                pyxel, self.game.anim_card, self.game.anim_card.x, self.game.anim_card.y, scale=1.12
            )

        if self.game.popup_timer > 0:
            self.renderer.draw_popup(pyxel, self.layout, self.game.popup_text, self.game.popup_success)

        if self.game.recycling:
            self.renderer.draw_text_center(pyxel, WIDTH // 2, HEIGHT // 2, "SHUFFLE...", 8)

        deck_x, deck_y, w, h = self._deck_rect()
        if self.game.deck:
            pyxel.blt(deck_x, deck_y, self.images["card"], 0, 0, w, h)
            self.renderer.draw_text(pyxel, deck_x + 6, deck_y + h + 2, f"{len(self.game.deck)}", 7)
            if len(self.game.hand) < self.game.max_hand_size:
                if (pyxel.frame_count // 30) % 2 == 0:
                    self.renderer.draw_text_center(pyxel, deck_x + w // 2, deck_y - 12, "CLICK ME!", 8)

        self.renderer.draw_label_box(pyxel, 20, HEIGHT / 4 - 60, WIDTH - 40, 30)
        self.renderer.draw_text(pyxel, 30, HEIGHT / 4 - 50, self.game.current_intro_text, 7)


App()
