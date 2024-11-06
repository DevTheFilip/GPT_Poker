from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.widget import MDWidget
from kivy.graphics import Color, Ellipse, Rectangle
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from Player import Player
from Card import Card
from Table import PokerTable
from kivymd.uix.gridlayout import MDGridLayout
import random
import logging
import math

class PokerApp(MDApp):
    def build(self):
        layout = MDFloatLayout()

        # Create a grid layout
        grid_layout = MDGridLayout(cols=2, size_hint=(1, 1))

        # Add the poker table
        table = PokerTable()
        grid_layout.add_widget(table)

        # Create a vertical box layout for the buttons
        button_layout = MDBoxLayout(orientation='vertical', size_hint=(None, 1), width=200)

        deal_button = MDFlatButton(text="Start", size_hint=(1, None), height=50)
        deal_button.bind(on_release=lambda x: table.start_game())
        button_layout.add_widget(deal_button)


        next_phase=MDFlatButton(text="Next Phase", size_hint=(1, None), height=50)
        next_phase.bind(on_release=lambda x: table.next_phase())
        button_layout.add_widget(next_phase)

        # Add the button layout to the grid layout
        grid_layout.add_widget(button_layout)

        layout.add_widget(grid_layout)

        # Generate players
        players = table.players
        num_players = len(players)
        center_x = 0.5
        center_y = 0.5
        radius = 0.4  # Adjust radius as needed

        for i, player in enumerate(players):
            angle = 2 * math.pi * i / num_players
            player.pos_hint = {
                'center_x': center_x + radius * math.cos(angle),
                'center_y': center_y + radius * math.sin(angle)
            }
            layout.add_widget(player)
            print("Player Added")

        return layout

if __name__ == '__main__':
    PokerApp().run()