from kivymd.uix.widget import MDWidget
from kivy.graphics import Color, Ellipse, Rectangle
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
import copy
class Card(MDWidget):
    def __init__(self, card_id, **kwargs):
        super().__init__(**kwargs)
        self.card_id = card_id
        self.size_hint = (None, None)
        self.size = (250, 250)
        self.image = Image(source=f'cards/{card_id}', pos=self.pos, size=self.size)
        self.add_widget(self.image)
        self.bind(pos=self.update_rect)
        self.rotation = 0

    def update_rect(self, *args):
        self.image.pos = self.pos
