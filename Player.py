from kivymd.uix.widget import MDWidget
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
import Chip


class Player(ButtonBehavior, MDWidget):
    def __init__(self, name, _index,_play, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.money = 100
        self.dealer_status = False
        self.index = _index
        self.debt = 1
        self.pot = 0
        self.out = False
        self.folded = False
        self.play_type = _play
        self.size_hint = (None, None)
        self.size = (200, 200)
        self.cards = []
        self.is_all_in = False
        self.NamePos = self.pos
        self.selected = False
        with self.canvas:
            if not self.dealer_status:
                self.color_instruction = Color(0, 0, 0, 0.5)  # Red color for players
            else:
                self.color_instruction = Color(1, 1, 1, 1)  # Blue color for dealer
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.card_images = [Image(size_hint=(None, None), size=(100, 150), opacity=1) for _ in range(2)]
        for card_image in self.card_images:
            self.add_widget(card_image)
        self.name_label = Label(text=self.name, pos=(self.pos[0], self.pos[1] + 160), color=[0, 0, 0, 1])

        #Play_Type_Label
        self.play_type_label = Label(text=self.play_type)
        self.add_widget(self.play_type_label)
        self.bind(pos=self.update_rect)

        self.chips = Chip.Chip(self.money)
        self.add_widget(self.chips)
        self.chips.pos = (self.pos[0] + 50, self.pos[1] + 50)  # Adjust position as needed

        self.add_widget(self.name_label)
        self.bind(pos=self.update_rect)
        self.card_images[0].opacity = 0
        self.card_images[1].opacity = 0

    def update_rect(self, *args):
        self.rect.pos = self.pos
        for i, card_image in enumerate(self.card_images):
            card_image.pos = (self.pos[0] + i * 100, self.pos[1] - 10)
        self.name_label.pos = (self.pos[0] + 20, self.pos[1] + 160)
        self.play_type_label.pos = (self.pos[0], self.pos[1] + 230)
        self.play_type_label.color = [0, 0.5, 1, 1]
        if  not self.is_all_in:
            self.chips.ammo.text = f"{self.money}"
            self.chips.image.opacity = 1
            self.chips.pos = (self.pos[0] , self.pos[1] + 210)  # Update chip position  # Adjust position as needed
        else:
            self.chips.ammo.text = f"ALL IN"
            self.chips.image.opacity = 0
            self.chips.pos = (self.pos[0] , self.pos[1] + 210)  # Update chip position
        self.chips.update_rect()
    def on_out(self):
        self.out = True
        self.fold()

    def on_press(self):
        if self.name == "Dealer":
            return
        self.selected = not self.selected
        if self.selected:
            self.color_instruction.rgba = (0, 0.7, 0.1, 1)  # Highlight selected player
        else:
            self.color_instruction.rgba = (0, 0, 0, 0.5)  # Reset color
        # Ensure correct reference to PokerTable
        if hasattr(self.parent, 'show_action_buttons'):
            self.parent.show_action_buttons(self)
        elif hasattr(self.parent.parent, 'show_action_buttons'):
            self.parent.parent.show_action_buttons(self)
    def add_card(self, card, index):
        self.cards.append(card)
        self.card_images[index].source = card.image.source
        self.card_images[index].opacity = 0  # Start with opacity 0 for animation

    def clear_cards(self):
        self.cards = []
        for card_image in self.card_images:
            card_image.opacity = 0

    def fold(self):
        self.clear_cards()
        self.pot = 0
        self.folded = True
        self.update_labels()
        self.opacity = 0

    def get_cards(self):
        return self.cards

    def place_bet(self, amount):
        if amount <= self.money:
            self.money -= amount
            self.pot += amount
            self.update_labels()
            return True
        return False

    def all_in(self):
        self.pot += self.money
        self.is_all_in = True
        self.money = 0
        self.update_labels()
        self.update_rect()


    def update_labels(self):
        self.chips.amount = self.money
        self.chips.update_rect()
        if self.dealer_status:
            self.name_label.text = self.name+ "-The Dealer"
            self.opacity = 1.4
            self.name_label.color = [1, 0, 0, 1]
        else:
            self.name_label.color = [0, 0, 0, 1]
            self.color_instruction = Color(0, 0, 0, 0.5)
            self.name_label.text = self.name
            self.opacity = 1
