
from collections import defaultdict
import copy
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

# game rules
MAX_HEALTH = 20
MAX_MP = 20
MAX_DECK_CARDS = 20
MAX_HAND_SIZE = 4

FIELD_WIDTH = 3
FIELD_HEIGHT = 2

global card_database

# display information
TURN_ORDER_X = 50
TURN_ORDER_Y = 3

ENEMY_INFO_X = 0
ENEMY_INFO_Y = TURN_ORDER_Y 

PLAYER_INFO_X = ENEMY_INFO_X
PLAYER_INFO_Y = ENEMY_INFO_Y+10

PLAYER_INPUT_X = PLAYER_INFO_X
PLAYER_INPUT_Y = PLAYER_INFO_Y+FIELD_HEIGHT+17

NEXT_CARD_IN_DECK_X = TURN_ORDER_X 
NEXT_CARD_IN_DECK_Y = PLAYER_INFO_Y+5

# display functions
class colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def set_color(color_val,text):
    return color_val + text + colors.RESET

def input_at(text, x, y):
    response = input(f"\033[%d;%dH{text}" % (y, x))
    return response

def print_at(text, x, y):
    print(f"\033[%d;%dH{text}" % (y, x))

# class for handling decks 
class Deck:
    def __init__(self,name="New Deck",deck_list=[],num_cards=0):
        self.name = name
        self.num_cards = num_cards
        self.card_list = deck_list
        self.limbo = []
        self.in_game_deck = []
        self.hand = []
    
    # initialize game hand
    def get_hand(self):
        self.limbo = []
        self.in_game_deck = copy.deepcopy(self.card_list)
        random.shuffle(self.in_game_deck)
        self.hand = []
        for _ in range(MAX_HAND_SIZE):
            self.hand.append(self.card_list.pop())

    def save_deck(self):
        pass

    def load_deck(self):
        pass
    
    def __str__(self):
        deck_string = ""
        deck_string += f"{self.name}\n"
        deck_string += f'NUM_CARDS: {self.num_cards}\n'
        deck_string += f'DECK LIST:\n'
        for card in self.card_list:
            deck_string += f'{card}\n'
        deck_string += '\n'
        deck_string += f'IN_GAME DECK LIST:\n'
        for card in self.in_game_deck:
            deck_string += f'{card}\n'
        deck_string += '\n'
        deck_string += f'IN_GAME HAND:\n'
        for card in self.hand:
            deck_string += f'{card}\n'
        deck_string += f'IN_GAME LIMBO:\n'        
        for card in self.limbo:
            deck_string += f'{card}\n'

        return deck_string
    
# class for characters in battle
class Character:
    def __init__(self,type,name="NO NAME"):
        self.char_type = None
        self.name = name
        if type == 0:
            self.char_type = "Player"
            self.health = MAX_HEALTH
            self.max_health = MAX_HEALTH
            self.mp = MAX_MP
            self.max_mp = MAX_MP
            self.speed = 1
        elif type == 1:
            self.char_type = "Demon"
            self.health = 5
            self.max_health = 5
            self.mp = 5
            self.max_mp = 5
            self.speed = 2

'''
    hand - current hand of the player
    health/max_health - current health of the player's main character
    mp/max_mp - current mp of the player's party
    field - position of party members for the player's party
    deck - the deck the player is using 
'''
class Player(Character):

    # player field operations
    def add_character_to_field(self,character,x,y):
        self.field[y][x] = character

    def remove_from_field(self,x,y):
        self.field[y][x] = None 

    def swap_on_field(self,x1,y1,x2,y2):
        temp_char = copy.deepcopy(self.field[y2][x2])
        self.field[y2][x2] = self.field[y1][x1]
        self.field[y1][x1] = temp_char

    def __init__(self, player_name="Player", deck_name="New Deck", deck=None):
        self.hand = [] 
        self.mp = MAX_MP
        self.max_mp = MAX_MP
        self.field = [[None for _ in range(FIELD_HEIGHT)] for _ in range(FIELD_WIDTH)]
        
        if not deck:
            self.deck = Deck(deck_name)
        else:
            self.deck = Deck(deck_name,deck)
        
        super().__init__(0,player_name)
    
    # get all party members on the player's side
    def get_party_members(self):
        pass

    def __str__(self):
        return ""
        pass


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
        self.opponent.field[1][0] = self.opponent
        self.player.field[1][1] = self.player

        self.opponent.deck.get_hand()
        self.player.deck.get_hand()
        self.add_to_game_log(f'GAME START\n')
        self.add_to_game_log(f'Player - {str(self.player)}\n')
        self.add_to_game_log(f'Player Deck - {str(self.player.deck)}\n')
        self.add_to_game_log(f'Opponent - {str(self.opponent)}\n')
        self.add_to_game_log(f'Opponent Deck - {str(self.opponent.deck)}\n')
        

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
        if self.current_character == self.turn_order[0][0]:
            info = self.turn_order.pop()
            self.turn_order.append([info[0],info[1]])
        
        return self.turn_order

    def input_for_turn(self):
        pass
    
    def input_space():
        pass 

    def display(self):
        system("cls")
        
        # print turn order
        print_at(f"Current Turn: {self.current_character.name}",TURN_ORDER_X,TURN_ORDER_Y)
        print_at("Up next",TURN_ORDER_X,TURN_ORDER_Y+2)
        for index,character in enumerate(self.turn_order):
            print_at(character[0].name,TURN_ORDER_X,TURN_ORDER_Y+index+3)
        
        # print field info 
        print_at(f"Enemy HP: {self.opponent.health}/{self.opponent.max_health}",ENEMY_INFO_X,ENEMY_INFO_Y)
        print_at(f"Enemy MP: {self.opponent.mp}/{self.opponent.max_mp}",ENEMY_INFO_X,ENEMY_INFO_Y+1)
        for y in range(0,FIELD_HEIGHT):
            for x in range(1,FIELD_WIDTH+1):
                if self.opponent.field[x-1][y]:
                    if self.current_character == self.opponent.field[x-1][y]:
                        print_at(set_color(colors.RED,"X"),ENEMY_INFO_X+x,ENEMY_INFO_Y+3+y)
                    else:
                        print_at("X",ENEMY_INFO_X+x,ENEMY_INFO_Y+3+y)
                else:
                    print_at(".",ENEMY_INFO_X+x,ENEMY_INFO_Y+3+y)
        
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