import logging

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.uix.label import Label

import Chip
from Player import Player
from kivy.uix.image import Image
from kivy.animation import Animation


import requests
import logging
from openai import OpenAI
from Card import Card
import random

API_KEY = ''
class PokerTable(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 0.5, 0, 1)  # Green color
            self.table = Ellipse(size=(1200, 600))
        self.bind(pos=self.update_table, size=self.update_table)

        self.CardLayout = BoxLayout(orientation='horizontal', size_hint=(None, None))
        self.CardLayout.size = (self.width, 250)  # Set the height as needed
        self.CardLayout.spacing = 50
        self.add_widget(self.CardLayout)  # Always add to PokerTable
        self.card_number = 0
        self.Generated_Cards = []
        self.First_Person_Already_Selected = True
        self.players = Player_Generator(6)
        self.pot = 0
        self.cycle = 0
        self.last_player_that_raised = None
        self.total_raised = 0
        self.time = 0
        self.game_running = True
        self.preflop = True
        self.action_log = ""
        self.current_player_index = 0
        self.counter = 0
        self.dealer = None
        self.temp_dealer = None # Initialize temp_dealer
        self.selected_player = None  # Initialize selected_player
        self.someone_raised = False  # Track if someone has raised

        # Bind the size and pos properties to update card positions
        self.bind(size=self.update_card_positions, pos=self.update_card_positions)
        #POT LABEL
        self.Pot = 0
        self.PotLabel = Label(text=f"Pot: ${self.pot}", pos=(self.width / 2, self.height / 2))
        self.add_widget(self.PotLabel)
        self.PotLabel.pos = (self.width / 2, self.height / 2)


        #Money_Table
        self.TableChip = Chip.Chip(self.pot)
        self.add_widget(self.TableChip)
        self.TableChip.pos = (self.width / 2+10, self.height / 2+10)

        #WINNER LABEL
        self.Winner_Label = Label(text=f"Winner: {self.pot}", pos=(self.width / 2, self.height / 2),size=(750,750),font_size=150)
        self.Winner_Label.color = [0, 0.3, 0.5, 1]
        self.add_widget(self.Winner_Label)
        self.Winner_Label.pos = (self.width / 2, self.height / 2)
        self.Winner_Label.opacity = 0



    def delay_button(self):
        self.game_running = False
        self.show_action_buttons()


    def next_phase(self):
        self.show_action_buttons(self.selected_player)

    def call_action(self, instance = None):
        player = self.get_selected_player()
        if player:
            print(f"{player.name} calls")
            if(player.debt >= player.money):
                print("All in")
                player.is_all_in = True
                player.all_in()
                self.action_log += f"{player.name} is all in\n"
            else:
                self.action_log += f"{player.name} calls for " + str(player.debt) + "\n"
            player.money -= player.debt
            self.pot += player.debt
            player.debt = 0
            self.update_pot()
            player.update_labels()
            self.select_next_player()
            print(f"Left Debt: {player.debt}")
    def fold_action(self, instance = None):
        player = self.get_selected_player()
        if player:
            self.action_log += f"{player.name} folds\n"
            print(f"{player.name} folds")
            player.fold()
            self.select_next_player()


    def raising(self,ammount):
        self.pot += ammount
        self.total_raised += ammount
        self.update_pot()

    def raise_action(self,raise_amm, instance = None):
        print()
        player = self.get_selected_player()
        if player:
            raise_amount = raise_amm
            if raise_amount.isdigit():
                if(int(raise_amount)+player.debt <= player.money):
                    print(f"{player.name} raises by {raise_amount}")
                    self.action_log += f"{player.name} raises by {raise_amount}\n"
                    self.last_player_that_raised = player
                    self.someone_raised = True
                    player.money -= (int(raise_amount)+player.debt)
                    player.debt = 0
                    for playerz in self.players:
                        if playerz is not player:
                            playerz.debt = playerz.debt + int(raise_amount)
                    if int(raise_amount)+player.debt == player.money:
                        player.is_all_in = True
                        player.all_in()
                    self.raising(int(raise_amount))
                    self.update_pot()
                    player.update_labels()
                    self.select_next_player()

    def check_action(self, instance = None):
        player = self.get_selected_player()
        if player:
            print(f"{player.name} checks")
            self.action_log += f"{player.name} checks\n"
            # Implement check logic here
            self.select_next_player()

    def get_selected_player(self):
        for player in self.players:
            if player.selected:
                return player
        return None


    def Give_Money(self, player, amount):
        player.money += amount
        player.update_labels()

    def Show_Winer(self,player):
        print(f"Winner is {player.name}")
        print(f"Winner is {player.name}")
        print(f"Winner is {player.name}")
        print(f"Winner is {player.name}")
        self.Winner_Label.text = f"Winner is {player.name}"
        self.Winner_Label.opacity    = 1
        return


    def On_Winner_Choosen(self,player_name):
        for player in self.players:
            if player.name == player_name:
                self.Show_Winer(player)
                Clock.schedule_once(lambda dt: self.Game_Over(player),10)
                return


    def Game_Over(self,winner):
        self.Winner_Label.opacity = 0
        self.Give_Money(winner, self.pot)
        self.pot = 0
        self.preflop = True
        self.action_log = ""
        self.time = 0
        self.update_pot()
        self.First_Person_Already_Selected = True
        self.someone_raised = False
        self.counter = 0
        self.cycle =0

        self.Generated_Cards = []
        self.CardLayout.clear_widgets()
        for player in self.players:
            if player.money == 0:
                player.on_out()
            for instruction in self.selected_player.canvas.children:
                if isinstance(instruction, Color):
                    instruction.rgba = (0, 0, 0, 0.2)
            if not player.out:
                player.is_all_in = False
                player.folded = False
                player.clear_cards()
                player.debt = 1
                player.dealer_status = False
                player.update_labels()
                player.opacity = 1

        self.start_game()


    def select_next_player(self, *args):

        not_folded = 0
        self.selected_player
        for player in self.players:
            if not player.folded:
                not_folded += 1
                not_folded_id = player
        if not_folded == 1:
            self.Game_Over(not_folded_id)
            return

        if self.selected_player:
            self.selected_player.selected = False
            for instruction in self.selected_player.canvas.children:
                if isinstance(instruction, Color):
                    instruction.rgba = (0, 0, 0, 0.2)  # Reset color

        # Find the next player who has not folded
        while True:
            if self.time == 0:
                self.current_player_index = (self.big_blind_index+1) % len(self.players)
            else:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.selected_player = self.players[self.current_player_index]
            if not self.selected_player.folded :
                break
        self.time = 1

        self.selected_player.selected = True
        for instruction in self.selected_player.canvas.children:
            if isinstance(instruction, Color):
                instruction.rgba = (0, 1, 0, 1)  # Highlight selected player
        if self.current_player_index == self.temp_dealer.index:
            if  not self.preflop:
                self.new_cycle()

        if self.preflop:
            if(self.current_player_index == self.big_blind_index):
                self.preflop = False
                self.deal_first_three()
                self.current_player_index = (self.dealer.index -1) % len(self.players)
                self.temp_dealer = self.dealer

        self.show_action_buttons(self.selected_player)


    def chatgpt_choose_move(self,prompt):
        client = OpenAI()
        print(prompt)
        logging.basicConfig(level=logging.CRITICAL)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a {self.selected_player.play_type} poker player  . YOUR TASK IS TO WIN AS MUCH MONEY AS POSSIBLE. You are given the data for the poker. ONLY SAY CALL, FOLD, RAISE, CHECK"},
                {
                    "role": "user",
                    "content": f"{prompt}"
                }
            ]
        )
        respone = completion.choices[0].message.content
        print(respone)
        self.process_move(respone)
        return

    def process_move(self, move):
        # Split the move into components
        move_parts = move.split()
        if move_parts[0].upper() == "RAISE":
            raise_amount = move_parts[1]  # Assuming the second part is the amount
            print(raise_amount)
            if(raise_amount.isdigit()):
                if(int(raise_amount) < self.selected_player.money):
                    Clock.schedule_once(lambda dt: self.raise_action(raise_amount),2)
                else:
                    print("Wrong move")
                    self.Generate_Details(self.selected_player,"LAST MOVE WAS WRONG: " + move)
                    return
        elif move_parts[0].upper() == "CHECK":
            Clock.schedule_once(lambda dt: self.check_action(),2)
        elif move_parts[0].upper() == "ALL":
            Clock.schedule_once(lambda dt: self.call_action(),2)
        elif move_parts[0].upper() == "CALL":
            Clock.schedule_once(lambda dt: self.call_action(),2)
            pass
        elif move_parts[0].upper() == "FOLD":
            Clock.schedule_once(lambda dt: self.fold_action(),2)
            pass
        else:
            print("Invalid move.")

    def Choose_Move(self,next_move):
        return
        # print(next_move)
        # if next_move == "CALL":
        #     self.call_action()
        # elif next_move == "FOLD":
        #     self.fold_action()
        # elif next_move == "RAISE":
        #     self.raise_action()
        # elif next_move == "CHECK":
        #     self.check_action()
        # return

    def Generate_Details(self, player,other=""):
        data = other
        data = "Your Hand:  " + player.cards[0].card_id.replace('.png', '') + ", " + player.cards[1].card_id.replace('.png', '')
        data += "\nYour Total Money: " + str(player.money) + "\nThe current pot: " + str(self.pot)
        data += "\nCall Amount: " + str(player.debt)
        data += "\nCommunity cards on the table:"
        for card in self.CardLayout.children:
            data += card.card_id.replace('.png',' ') + " ,"

        data += "\nPrevious player actions:"

        if self.action_log != "":
            data += self.action_log
        else:
            data += "No moves were made until now!!\n"

        data +="\n You are : " + player.name
        data += "\nPrint the next best move for \n" + player.name +". Make sure that the move is posible"
        data+="\nIF you are rasing you need to specify the amount up to  EX: RAISE 10\n"

        # if player.debt == 0:
        #     data += "You can CHECK, RAISE (specify an amount) or FOLD\n"
        # else:
        #     # Calculate the maximum raise allowed after the call
        #     max_raise = player.money - player.debt  # Maximum you can raise without going broke
        #
        #     if player.money < player.debt:
        #         data += "You can ONLY FOLD, as you don't have enough money to call.\n"
        #         data += "YOU CANOT RISE OR CHECK\n"
        #     else:
        #         data += "You can ONLY CALL for " + str(player.debt) + ", "
        #         if max_raise > 0:
        #             data += "RAISE (specify an amount up to " + str(max_raise) + "), "
        #         data += "or FOLD\n"
        #
        # data += "MAKE SURE THAT IF YOU RAISE, THE MONEY YOU HAVE IS NOT LESS THAN THE RAISE AMOUNT + " + str(
        #     player.debt) + "\n"

        print(data)
        Clock.schedule_once(lambda dt: self.chatgpt_choose_move(data), 0.2)

    def show_action_buttons(self, player):
        print(self.game_running)
        print(player)
        if(self.game_running == True):
            self.Generate_Details(player)

    def start_player_cycle(self):
        self.game_running = True
        if self.First_Person_Already_Selected:
            self.First_Person_Already_Selected = False
            self.select_next_player()  # Select the first player immediately
            #Clock.schedule_interval(self.select_next_player, 999999999)  # Wait indefinitely



    def start_game(self):
        # Rotate through players to select a dealer
        if self.dealer is not None:
            self.current_player_index = self.dealer.index
            self.temp_dealer = self.dealer
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.dealer = self.players[self.current_player_index]
            self.temp_dealer = self.dealer
            if not self.dealer.out:
                print(f"{self.dealer.name} is the dealer")
                self.dealer.dealer_status = True
                self.dealer.update_labels()
                break
        # Assign small blind and big blind
        small_blind_index = (self.current_player_index + 1) % len(self.players)
        while self.players[small_blind_index].out:
            small_blind_index = (small_blind_index + 1) % len(self.players)
        self.big_blind_index = (small_blind_index + 1) % len(self.players)
        while self.players[self.big_blind_index].out:
            big_blind_index = (big_blind_index + 1) % len(self.players)

        small_blind_player = self.players[small_blind_index]
        big_blind_player = self.players[self.big_blind_index]

        # Deduct money for blinds
        if small_blind_player.money >= 1:
            small_blind_player.place_bet(1)
        else:
            small_blind_player.on_out()

        if big_blind_player.money >= 2:
            big_blind_player.place_bet(2)
        else:
            big_blind_player.on_out()

        # Update labels to reflect new money amounts
        small_blind_player.update_labels()
        big_blind_player.update_labels()

        # Deal the cards
        self.pot = 3
        self.total_raised = 1
        self.update_pot()
        self.someone_raised = False
        self.deal_cards()

    def get_chatgpt_response(self,prompt):
        client = OpenAI()
        print(prompt)

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a dealler in poker. YOU ONLY SAY THE PLAYER THAT WIN!! EX: Player 1 or Player 4"},
                {
                    "role": "user",
                    "content": f"{prompt}"
                }
            ]
        )
        respone = completion.choices[0].message.content
        print(respone)
        self.On_Winner_Choosen(respone)
        return

    def Checking_For_Winner(self):
        print ("Checking for winner")
        print ("Checking for winner")
        print ("Checking for winner")
        print ("Checking for winner")
        print ("Checking for winner")
        data = "This is the final state of a Poker game\n"
        data = data+"The players have the following cards:\n"
        for player in self.players:
            if not player.folded:
                cards = player.get_cards()
                data += f"{player.name} has {cards[0].card_id} and {cards[1].card_id}\n"
        data += "The table has: "
        for card in self.CardLayout.children:
            data += f"{card.card_id} ,"
        data = data+"PRINT ONLY THE WINNER!! ONLY THE WINNER!!"
        print(data)
        result = self.get_chatgpt_response(data)
        print(result)


    def new_cycle(self):
        data = ""
        data += "The table has: "
        for card in self.CardLayout.children:
            data += f"{card.card_id} ,"
        print(data)
        print("New cycle"+ str(self.cycle))
        if(self.cycle == 2):
            if not self.someone_raised :
                self.game_running = False
                self.Checking_For_Winner()
            else:
                self.someone_raised = False
                self.temp_dealer = self.last_player_that_raised
                return
            return
        self.cycle += 1
        card_id = self.generate_card_id()
        card = Card(card_id)
        self.total_raised = 0
        card.pos = self.dealer.pos
        card.size = (250, 250)
        final_pos = (self.width / 2 - card.width / 2, self.height / 2 - card.height / 2)

        def complete_animation(*args):
            self.CardLayout.add_widget(card)
            Clock.schedule_once(lambda dt: self.update_table(), 0.1)

        # Ensure CardLayout is added to PokerTable
        if self.CardLayout not in self.children:
            self.add_widget(self.CardLayout)

        animation = Animation(opacity=1, duration=0.5) + Animation(pos=final_pos, duration=0.2)
        animation.bind(on_complete=complete_animation)
        animation.start(card)
    def generate_card_id(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        suit = random.choice(suits)
        value = random.choice(values)
        result = f'{value}_of_{suit}.png'
        if result in self.Generated_Cards:
            return self.generate_card_id()
        self.Generated_Cards.append(result)
        return result


    #DEBUG
    def debug_cards(self):
        return
        data = ""
        data += "The table has: "
        for card in self.CardLayout.children:
            data += f"{card.card_id} ,"
        print(data)

    def deal_first_three(self):
        self.debug_cards()
        self.count_for_end = 0
        for i in range(3):
            print("Dealing first three cards")
            card_id = self.generate_card_id()
            print(f"Generated card ID: {card_id}")
            card = Card(card_id)
            card.opacity = 0  # Start with opacity 0 for animation

            # Set the card's initial position to the dealer's position
            card.pos = self.dealer.pos
            print(f"Card starting position (dealer's position): {self.dealer.pos}")

            # Add the card to the layout before animation
            self.CardLayout.add_widget(card)
            # Calculate the final position of the card on the table
            final_pos = (self.width / 2 - card.width / 2 + i * 110, self.height / 2 - card.height / 2)
            print(f"Card final position: {final_pos}")

            # Function to be called when the animation is complete
            def complete_animation(*args):
                card.opacity = 1
                self.update_card_positions()  # Ensure the cards are positioned correctly
                self.count_for_end += 1
                print(f"Counter: {self.count_for_end}")
                if self.count_for_end == 3:
                    self.start_player_cycle()

            # Animate the card from the dealer's position to the final position
            animation = Animation(opacity=1, duration=0.2) + Animation(pos=final_pos, duration=0.2)
            animation.bind(on_complete=complete_animation)
            animation.start(card)
            print(f"Card added to layout: {card}")

        # Ensure CardLayout is added to the PokerTable
        if self.CardLayout not in self.children:
            self.add_widget(self.CardLayout)
            print("CardLayout added to PokerTable")

    def deal_cards(self):
        self.current_card_index = 0
        self.current_player_index = 0
        self.total_cards = 2 * len(self.players)
        self.schedule_next_card()

    def schedule_next_card(self):
        if self.current_card_index < self.total_cards:
            Clock.schedule_once(self.deal_next_card, 0.2)



    def Generate_Preflop_Data(self, player,other=""):
        data = other
        data = "This is the pre-flop data for a Poker game\n"
        data = "Your Hand:  " + player.cards[0].card_id.replace('.png', '') + ", " + player.cards[1].card_id.replace('.png', '')
        data += "\nYour Total Money: " + str(player.money) + "\nThe current pot: " + str(self.pot)
        for card in self.CardLayout.children:
            data += card.card_id.replace('.png',' ') + " ,"

        data += "\nPrevious player actions:"

        if self.action_log != "":
            data += self.action_log
        else:
            data += "No moves were made until now!!\n"

        data +="\n You are : " + player.name
        data += "\nPrint the next best move for \n" + player.name +". Make sure that the move is posible"
        data+="\nIF you are rasing you need to specify the amount up to  EX: RAISE 10, RAISE 25\n"
        print(data)
        Clock.schedule_once(lambda dt: self.chatgpt_choose_move(data), 0.15)

    def pre_flop(self):
        self.game_running = True
        self.select_next_player()
        self.Generate_Preflop_Data(self.selected_player)
        # Implement pre-flop logic here
        pass

    def StartCard_anim_complete(self):
        print("StartCard_anim_complete")
        self.pre_flop()
        #self.deal_first_three()

    def deal_next_card(self, dt):
        player = self.players[self.current_player_index]
        card_index = self.current_card_index // len(self.players)
        card_id = self.generate_card_id()
        card = Card(card_id)
        self.debug_cards()
        Player_cards = []
        player.add_card(card, card_index)
        Player_cards.append(card)
        card.opacity = 0
        cardtwo = Card(card_id)
        cardtwo.opacity = 1  # Ensure the card is invisible initially
        self.add_widget(cardtwo)  # Add the card widget to the layout
        print(f"Dealt {card_id} to player {self.current_player_index + 1}")

        # Animate the card dealing from dealer to player

        def complete_animation(*args):
            self.remove_widget(cardtwo)
            player.card_images[card_index].opacity = 1
            self.counter += 1
            if self.counter == 12:
                self.StartCard_anim_complete()

        cardtwo.pos = self.dealer.pos  # Start from dealer's position
        cardtwo.size = (150,150)
        animation = Animation(opacity=1, duration=0.05) + Animation(pos=player.card_images[card_index].pos, duration=0.05)
        animation.bind(on_complete=complete_animation)
        animation.start(cardtwo)

        self.current_card_index += 1
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.schedule_next_card()

    def update_card_positions(self, *args):
        # Keep CardLayout size updated
        self.CardLayout.size = (self.width, 250)
        self.CardLayout.spacing = 50
        center_x = self.width / 2
        for i, card in enumerate(self.CardLayout.children):
            card.pos = (center_x - card.width / 2 + i * 110, self.height / 2 - card.height / 2)
            card.size = (250, 250)  # Adjust card size as needed
        if self.CardLayout not in self.children:
            self.add_widget(self.CardLayout)  # Ensure it's always part of PokerTable
            print("CardLayout added to PokerTable")

    def update_pot(self, *args):
        self.PotLabel.text = f"Pot: ${self.pot}"
        self.TableChip.amount = self.pot
        self.TableChip.update_rect()

    def update_player_labels(self, *args):
        for player in self.players:
            player.update_labels()
    def update_table(self, *args):
        self.TableChip.pos = (
        self.width / 1.5 - self.PotLabel.width / 1.5, self.height / 1.5 - self.PotLabel.height / 1.5)
        self.TableChip.ammo.opacity = 0
        self.table.size = (self.width, self.height)

        self.Winner_Label.size = (self.width*1, self.height)
        self.PotLabel.pos = (
        self.width / 1.5 - self.PotLabel.width / 1.5, self.height / 1.5 - self.PotLabel.height / 1.5)
        self.table.pos = (
            self.parent.width / 2 - self.table.size[0] / 2,
            self.parent.height / 2 - self.table.size[1] / 2
        )
        self.update_card_positions()


def Player_Generator(number_of_players):
    players = []
    type = ["Aggressive","Passive","Neutral"]
    for i in range(number_of_players):
        random_first_name = "Player"
        random_last_name = i
        random_name = f"{random_first_name} {random_last_name}"
        players.append(Player(random_name,i,type[random.randint(0,2)]))
    return players


