# main.py
import pyxel

from src.app.game_loop import GameLoop
from src.data.objects import create_object_pool
from src.game.game_engine import GameEngine
from src.option import HEIGHT, WIDTH
from src.scene_manager import SceneManager
from src.ui.input_controller import InputController
from src.ui.layout_manager import LayoutManager
from src.ui.renderer.renderer import Renderer
from src.ui.theme import WARM_16, apply_palette


CARD_IMAGE_PATH = "./assets/images/trading_card03_yellow.png"
FONT_PATH = "assets/misaki_gothic.bdf"
STARTING_HAND_SIZE = 3


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="B Demo")
        apply_palette(WARM_16)
        pyxel.mouse(True)

        font = pyxel.Font(FONT_PATH)

        scene_manager = SceneManager()
        layout = LayoutManager(WIDTH, HEIGHT)
        input_controller = InputController()

        object_pool = create_object_pool()
        game = GameEngine(scene_manager, object_pool)

        renderer = Renderer(font, None, WIDTH, HEIGHT)
        images = self.load_images(object_pool, renderer)
        renderer.set_images(images)

        self.init_sounds()

        self.start_game(game, layout)

        loop = GameLoop(
            pyxel=pyxel,
            width=WIDTH,
            height=HEIGHT,
            scene_manager=scene_manager,
            layout=layout,
            input_controller=input_controller,
            game=game,
            renderer=renderer,
            images=images,
        )

        pyxel.run(loop.update, loop.draw)

    def start_game(self, game, layout):
        game.build_deck()
        game.draw_initial_hand()
        slots = layout.object_slots(STARTING_HAND_SIZE)
        game.start_round(slots)

    def load_images(self, object_pool, renderer):
        images = self._load_card_image(renderer)
        images.update(self._load_object_images(object_pool, renderer))
        return images

    def _load_card_image(self, renderer):
        images = {}
        raw_card = pyxel.Image.from_image(CARD_IMAGE_PATH)
        images["card"] = self.resize_image(
            raw_card,
            renderer.card_w,
            renderer.card_h,
        )
        return images

    def _load_object_images(self, object_pool, renderer):
        images = {}
        for obj in object_pool:
            path = obj.image_path
            if path not in images:
                raw = pyxel.Image.from_image(path)
                images[path] = self.resize_image(
                    raw,
                    renderer.object_w,
                    renderer.object_h,
                )
        return images

    def init_sounds(self):
        pyxel.sound(1).set("c2", "t", "7", "n", 15)
        pyxel.sound(2).set("c4e4", "p", "7", "f", 10)
        pyxel.sound(3).set("g2f2", "n", "6", "f", 20)

    @staticmethod
    def resize_image(src, w, h):
        dst = pyxel.Image(w, h)
        for y in range(h):
            for x in range(w):
                sx = int(x * src.width / w)
                sy = int(y * src.height / h)
                dst.pset(x, y, src.pget(sx, sy))
        return dst


App()
