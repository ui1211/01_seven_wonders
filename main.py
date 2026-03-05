# main.py
import pyxel
import PyxelUniversalFont as puf

from src.app.game_loop import GameLoop
from src.data.objects import create_object_pool
from src.game.game_engine import GameEngine
from src.option import HEIGHT, WIDTH
from src.scene_manager import SceneManager
from src.ui.input_controller import InputController
from src.ui.layout_manager import LayoutManager
from src.ui.renderer import Renderer
from src.ui.theme import MODERN_16, WARM_16, apply_palette


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="B Demo")
        apply_palette(WARM_16)
        # pyxel.images[0].load(0, 0, "./assets/assets0.png", incl_colors=True)
        pyxel.mouse(True)

        writer = puf.Writer("IPA_Gothic.ttf")

        scene_manager = SceneManager()
        layout = LayoutManager(WIDTH, HEIGHT)
        input_controller = InputController()

        object_pool = create_object_pool()
        game = GameEngine(scene_manager, object_pool)

        renderer = Renderer(writer, {}, WIDTH, HEIGHT)

        images = self.load_images(pyxel, object_pool, renderer)
        renderer.images = images

        self.init_sounds(pyxel)

        game.build_deck()
        game.draw_initial_hand()
        slots = layout.object_slots(3)
        game.start_round(slots)

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

    def load_images(self, pyxel, object_pool, renderer):
        images = {}

        raw_card = pyxel.Image.from_image("./assets/images/trading_card03_yellow.png")
        images["card"] = self.resize_image(
            pyxel,
            raw_card,
            renderer.card_w,
            renderer.card_h,
        )

        for obj in object_pool:
            path = obj.image_path
            if path not in images:
                raw = pyxel.Image.from_image(path)
                images[path] = self.resize_image(
                    pyxel,
                    raw,
                    renderer.object_w,
                    renderer.object_h,
                )

        return images

    def init_sounds(self, pyxel):
        pyxel.sound(1).set("c2", "t", "7", "n", 15)
        pyxel.sound(2).set("c4e4", "p", "7", "f", 10)
        pyxel.sound(3).set("g2f2", "n", "6", "f", 20)

    def resize_image(self, pyxel, src, w, h):
        dst = pyxel.Image(w, h)
        for y in range(h):
            for x in range(w):
                sx = int(x * src.width / w)
                sy = int(y * src.height / h)
                dst.pset(x, y, src.pget(sx, sy))
        return dst


App()
App()
