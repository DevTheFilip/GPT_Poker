from kivymd.uix.widget import MDWidget
from kivy.graphics import Color, Ellipse, Rectangle
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image

class Chip(MDWidget):
    def __init__(self, amount, **kwargs):
        super().__init__(**kwargs)
        self.amount = amount
        self.size_hint = (None, None)
        self.size = (50, 50)  # Set a default size for the chip
        self.image = Image(source='Table/chip.png', size=self.size)
        self.ammo = MDLabel(text=f"{self.amount}", pos=(10, 0))
        self.add_widget(self.image)
        self.add_widget(self.ammo)
        self.bind(pos=self.update_rect)
        self.rotation = 0

    def update_rect(self, *args):
        self.image.pos = (self.pos[0], self.pos[1])
        self.ammo.pos = (self.image.pos[0]+65, self.image.pos[1]-12)
        self.ammo.text = f"{self.amount}"
        self.image.size = (75,75)