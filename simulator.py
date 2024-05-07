
from collections import defaultdict
from datetime import datetime
from io import StringIO
import json
from os import system
import os
import random
import signal
import sys
import time
import traceback

from game_settings import FIELD_HEIGHT, FIELD_WIDTH, MAX_DECK_CARDS, MAX_HAND_SIZE
from graphics import ENEMY_INFO_X, ENEMY_INFO_Y, NEXT_CARD_IN_DECK_X, NEXT_CARD_IN_DECK_Y, PLAYER_INFO_X, PLAYER_INFO_Y, PLAYER_INPUT_X, PLAYER_INPUT_Y, TURN_ORDER_X, TURN_ORDER_Y, colors, input_at, print_at, set_color
from player import Player

card_dict_keys = [
    "Type",	
    "Name",	
    "Effects",	
    "MP Cost",	
    "Usability",	
    "Strength",	
    "Num Targets",	
    "Playable Copies",	
    "Rarity"
]

# class for running the simulator
class Simulator:

    def add_to_game_log(self,message):
        self.game_log.append(message)

    def save_game_log(self):
        current_time = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        os.makedirs("logs",exist_ok=True)
        with open(f"logs/{current_time}_log.txt",'w') as log_file:
            for log in self.game_log:
                log_file.write(log)

    def signal_handler(self, sig, frame):
        self.save_game_log()
        print('Ctrl+C captured, exiting...')
        sys.exit(0)

    def __str__(self):
        pass

    def __init__(self):
        # initalize the player and opponent
        opp_selected_cards = random.sample(card_database, MAX_DECK_CARDS)
        self.opponent = Player("Opponent",deck=opp_selected_cards)
        
        player_selected_cards = random.sample(card_database, MAX_DECK_CARDS)
        self.player = Player("You",deck=player_selected_cards)

        self.current_character = None
        self.turn_order = []
        self.turns = 0
        self.conditionals = []

        self.game_log = []
        
        signal.signal(signal.SIGINT, self.signal_handler)

    
    def initialize_game(self):
        # flipping coin, pick a side
        coin_side = ""
        while(coin_side != "H" and coin_side != "T"):
            coin_side = input("Flipping coin to determine who goes first (H/T):")
            coin_side = coin_side.upper()
        coin_toss = random.choice(["H", "T"])
        turn_pick = ""
        
        # if player won die roll, they pick
        if coin_toss == coin_side:
            while(turn_pick != "1" and turn_pick != "2"):
                turn_pick = input("Would you like to go first or second? (1/2):")
        else: # if opponent won, random pick
            turn_pick = random.choice(["1", "2"])

        if turn_pick == "1":
            print("You're going first")
            self.turn_order.append([self.opponent,1])
            self.turn_order.append([self.player,0])
        else:
            print("You're going second")
            self.turn_order.append([self.player,0])
            self.turn_order.append([self.opponent,1])
        
        # player character starting positions
        self.opponent.field[1][1] = self.opponent
        self.player.field[1][1] = self.player

        self.opponent.deck.get_hand()
        self.player.deck.get_hand()
        self.add_to_game_log(f'MATCH_INFO\n')
        self.add_to_game_log(f'Player - {str(self.player)}\n')
        self.add_to_game_log(f'Player Deck - {str(self.player.deck)}\n')
        self.add_to_game_log(f'Opponent - {str(self.opponent)}\n')
        self.add_to_game_log(f'Opponent Deck - {str(self.opponent.deck)}\n')
        self.add_to_game_log(f'GAME START\n')
        self.add_to_game_log(f'\n{self.turn_order[-1][0].name} is going first\n')
        input("Press Enter")

    # turn order
    # {character, party}
    def set_turn_order(self):
        all_characters = []
        teams = defaultdict(list)

        team_in_game = {0:self.player,1:self.opponent}

        for index in team_in_game:
            for y in range(FIELD_HEIGHT):
                for x in range(FIELD_WIDTH):
                    if team_in_game[index].field[x][y]:
                        all_characters.append(team_in_game[index].field[x][y])
                        teams[index].append(team_in_game[index].field[x][y])
        
        from operator import attrgetter
        all_characters = sorted(all_characters, key=attrgetter('speed'))

        del self.turn_order
        self.turn_order = []
        for character in all_characters:
            for index in teams:
                if character in teams[index]:
                    self.turn_order.append([character,index])
        
        # prevent a character going first back to back
        if self.current_character == self.turn_order[-1][0]:
            info = self.turn_order.pop()
            self.turn_order.insert(0,[info[0],info[1]])
        
        self.add_to_game_log(f'\nNEW TURN ORDER\n')
        for index in range(len(self.turn_order)-1,-1,-1):
            self.add_to_game_log(f'{self.turn_order[index][0].name} - {self.turn_order[index][1]}\n')
        self.add_to_game_log(f'\n')

        return self.turn_order

    def input_for_turn(self):
        pass
    
    def input_space():
        pass 

    def display(self):
        system("cls")
        
        # print turn order
        self.add_to_game_log(f'CURRENT TURN {self.current_character.name}\n')
        print_at(f"Current Turn: {self.current_character.name}",TURN_ORDER_X,TURN_ORDER_Y)
        print_at("Up next",TURN_ORDER_X,TURN_ORDER_Y+2)
        for index in range(len(self.turn_order)-1,-1,-1):
            print_at(self.turn_order[index][0].name,TURN_ORDER_X,TURN_ORDER_Y+index+3)
        
        # print field info 
        print_at(f"Enemy HP: {self.opponent.health}/{self.opponent.max_health}",ENEMY_INFO_X,ENEMY_INFO_Y)
        print_at(f"Enemy MP: {self.opponent.mp}/{self.opponent.max_mp}",ENEMY_INFO_X,ENEMY_INFO_Y+1)
        for y in range(FIELD_HEIGHT-1,-1,-1):
            for x in range(1,FIELD_WIDTH+1):
                if self.opponent.field[x-1][y]:
                    if self.current_character == self.opponent.field[x-1][y]:
                        print_at(set_color(colors.RED,"X"),ENEMY_INFO_X+x,ENEMY_INFO_Y+3+FIELD_HEIGHT-y)
                    else:
                        print_at("X",ENEMY_INFO_X+x,ENEMY_INFO_Y+3+FIELD_HEIGHT-y)
                else:
                    print_at(".",ENEMY_INFO_X+x,ENEMY_INFO_Y+3+FIELD_HEIGHT-y)
        
        print_at(f"Your HP: {self.player.health}/{self.player.max_health}",PLAYER_INFO_X,PLAYER_INFO_Y)
        print_at(f"Your MP: {self.player.mp}/{self.player.max_mp}",PLAYER_INFO_X,PLAYER_INFO_Y+1)
        for y in range(0,FIELD_HEIGHT):
            for x in range(1,FIELD_WIDTH+1):
                if self.player.field[x-1][y]:
                    if self.current_character == self.player.field[x-1][y]:
                        print_at(set_color(colors.BLUE,"X"),PLAYER_INFO_X+x,PLAYER_INFO_Y+3+y)
                    else:
                        print_at("X",PLAYER_INFO_X+x,PLAYER_INFO_Y+3+y)
                else:
                    print_at(".",PLAYER_INFO_X+x,PLAYER_INFO_Y+3+y)

        # print cards in your hand 
        print_at("Your Hand:",PLAYER_INFO_X,PLAYER_INFO_Y+FIELD_HEIGHT+4)
        for index in range(MAX_HAND_SIZE):
            card_name = f'{self.player.deck.hand[index]["Name"]} ({self.player.deck.hand[index]["Type"]}) - MP COST: {self.player.deck.hand[index]["MP Cost"]} - Uses Left: {self.player.deck.hand[index]["Usability"]}' if self.player.deck.hand[index] else ""
            card_description = ""
            if card_name:
                card_description = self.player.deck.hand[index]["Effects"]
            print_at(f'{index} - {card_name}',PLAYER_INFO_X,PLAYER_INFO_Y+FIELD_HEIGHT+6+index*3)
            print_at(f'{card_description}',PLAYER_INFO_X,PLAYER_INFO_Y+FIELD_HEIGHT+6+index*3+1)

        print_at("Next card from Deck:",NEXT_CARD_IN_DECK_X,NEXT_CARD_IN_DECK_Y)
        card_name = f'{self.player.deck.in_game_deck[0]["Name"]} ({self.player.deck.in_game_deck[0]["Type"]})' if self.player.deck.in_game_deck[0] else ""
        print_at(f'{card_name}',NEXT_CARD_IN_DECK_X,NEXT_CARD_IN_DECK_Y+1)

    def logic_handler(self,turn_selector):
        # set list of available actions based on character status and 
        # which character it is (player vs party member)
        turn_command_list = []
        if (self.current_character == self.player) or (self.current_character == self.opponent):
            turn_command_list = [
                "Use card",
                "Move to a nearby space",
                "Skip turn"
            ]
        else:
            turn_command_list = [
                "Use skill",
                "Use card",
                "Move to a nearby space",
                "Skip turn"
            ]

        if turn_selector[1] == 0:
            if len(self.player.deck.in_game_deck) < 0:
                turn_command_list.append("Recharge 5 cards to deck")
            
            if self.player.mp < self.player.max_mp:
                turn_command_list.append("Recharge 3 MP")     
        
            print_at("Commands",PLAYER_INPUT_X,PLAYER_INPUT_Y+1)
            
            for index, command in enumerate(turn_command_list):
                print_at(f'{index} - {command}',PLAYER_INPUT_X,PLAYER_INPUT_Y+index+2)
            choice = input_at("What will you do?:",PLAYER_INPUT_X,PLAYER_INPUT_Y+len(turn_command_list)+2)
        # # if opponent's turn
        elif turn_selector[1] == 1:
            if len(self.opponent.deck.in_game_deck) < 0:
                turn_command_list.append("Recharge 5 cards to deck")
            
            if self.opponent.mp < self.opponent.max_mp:
                turn_command_list.append("Recharge 3 MP")     
        
            input_at("Press Enter",PLAYER_INPUT_X,PLAYER_INPUT_Y)
  
    def main_loop(self):

        try:
            self.initialize_game()
            running_game = True
            while running_game:
                turn_selector = self.turn_order.pop()
                self.current_character = turn_selector[0]
                
                # print information on screen
                self.display()
                
                self.logic_handler(turn_selector)
                if not self.turn_order:
                    self.turn_order = self.set_turn_order()
        except Exception as e:
            traceback_output = StringIO()
            traceback.print_exc(file=traceback_output)
            traceback_string = traceback_output.getvalue()
            self.add_to_game_log(f'ERROR - {e}\n')
            self.add_to_game_log(f'TRACEBACK\n{traceback_string}')
            self.save_game_log()

if __name__ == "__main__":

    # Set the random seed
    random.seed(time.time())

    # load the card database json
    with open('extracted_card_data.json','r') as card_data:
        card_database = json.load(card_data)

    main_simulator = Simulator()

    main_simulator.main_loop()