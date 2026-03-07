from src.ui.renderer.card_renderer import CardRenderer
from src.ui.renderer.dice_renderer import DiceRenderer
from src.ui.renderer.hud_renderer import HudRenderer
from src.ui.renderer.object_renderer import ObjectRenderer
from src.ui.renderer.text_renderer import TextRenderer
from src.ui.renderer.ui_renderer import UiRenderer


class Renderer:
    def __init__(self, font, images, width, height):

        self.width = width
        self.height = height

        self.text = TextRenderer(font)

        self.card_w = int(width * 0.12)
        self.card_h = int(self.card_w * 1.4)

        self.object_w = int(width * 0.08)
        self.object_h = int(self.object_w * 1.2)

        self.bar_w = self.object_w
        self.bar_h = int(height * 0.01)

        self.ui = UiRenderer(self.text)
        self.card = CardRenderer(self.text, images, self.card_w, self.card_h)
        self.obj = ObjectRenderer(self.text, images, self.object_w, self.object_h, self.bar_w, self.bar_h)
        self.hud = HudRenderer(self.text, width, height)
        self.dice = DiceRenderer(self.text)

    def set_images(self, images):
        self.images = images
        self.card.images = images
        self.obj.images = images
        self.card.images = images
        self.obj.images = images
