
from collections import defaultdict
import copy
import json
from os import system
import random
import time
MAX_HEALTH = 20
MAX_MP = 20

FIELD_WIDTH = 3
FIELD_HEIGHT = 2

# class for handling decks 
class Deck:
    def __init__(self,name="New Deck",deck_list=[],num_cards=0):
        self.name = name
        self.num_cards = num_cards
        self.card_list = deck_list
    
    def save_deck(self):
        pass

    def load_deck(self):
        pass
    

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
        self.deck_recharge_counter = 0
        self.mp_recharge_counter = 0  
        self.hand = [] 
        self.mp = MAX_MP
        self.max_mp = MAX_MP
        self.field = [[None for _ in range(FIELD_HEIGHT)] for _ in range(FIELD_WIDTH)]
        
        if not deck:
            self.deck = Deck(deck_name)
        else:
            self.deck = Deck(deck_name,deck)
        
        self.limbo = []
        super().__init__(0,player_name)
    
    # get all party members on the player's side
    def get_party_members(self):
        pass

# class for running the simulator
class Simulator:
    def __init__(self):
        # initalize the player and opponent
        self.opponent = Player("Opponent")
        self.player = Player("You")

        self.current_character = None
        self.turn_order = []
        self.turns = 0
        self.conditional = None 
        pass
    
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
            self.turn_order.append([self.player,0])
            self.turn_order.append([self.opponent,1])
        elif turn_pick == "2":
            print("You're going second")
            self.turn_order.append([self.opponent,1])
            self.turn_order.append([self.player,0])
        self.opponent.field[1][0] = self.opponent
        self.player.field[1][1] = self.player
        input("Press Enter")

    # turn order
    # {character, party}
    def set_turn_order(self):
        all_characters = []
        teams = defaultdict(list)

        # get characters from opponent
        for y in range(FIELD_HEIGHT):
            for x in range(FIELD_WIDTH):
                if self.opponent.field[x][y]:
                    all_characters.append(self.opponent.field[x][y])
                    teams[0].append(self.opponent.field[x][y])
        
        # get characters from player
        for y in range(FIELD_HEIGHT):
            for x in range(FIELD_WIDTH):
                if self.player.field[x][y]:
                    all_characters.append(self.player.field[x][y])
                    teams[1].append(self.player.field[x][y])
        
        from operator import attrgetter
        all_characters = sorted(all_characters, key=attrgetter('speed'))

        del self.turn_order
        self.turn_order = []
        for character in all_characters:
            for index in teams:
                if character in teams[index]:
                    self.turn_order.append([character,index])
        
        return self.turn_order

    def input_for_turn(self):
        pass
    
    def input_space():
        pass 

    def display(self):
        system("cls")
        def print_at(text, x, y):
            print(f"\033[%d;%dH{text}" % (y, x))

        TURN_ORDER_X = 50
        TURN_ORDER_Y = 3
        
        ENEMY_INFO_X = 0
        ENEMY_INFO_Y = TURN_ORDER_Y 

        PLAYER_INFO_X = ENEMY_INFO_X
        PLAYER_INFO_Y = ENEMY_INFO_Y+10
        
        # print turn order
        print_at(f"Current Turn: {self.current_character.name}",TURN_ORDER_X,TURN_ORDER_Y)
        print_at("Up next",TURN_ORDER_X,TURN_ORDER_Y+2)
        for index,character in enumerate(self.turn_order):
            print_at(character[0].name,TURN_ORDER_X,TURN_ORDER_Y+index+3)
        
        # print field info 
        print_at(f"Enemy HP: {None}/{None}",ENEMY_INFO_X,ENEMY_INFO_Y)
        print_at(f"Enemy MP: {None}/{None}",ENEMY_INFO_X,ENEMY_INFO_Y+1)
        for y in range(0,FIELD_HEIGHT):
            for x in range(1,FIELD_WIDTH+1):
                if self.opponent.field[x-1][y]:
                    print_at("X",ENEMY_INFO_X+x,ENEMY_INFO_Y+3+y)
                else:
                    print_at(".",ENEMY_INFO_X+x,ENEMY_INFO_Y+3+y)
        
        print_at(f"Your HP: {None}/{None}",PLAYER_INFO_X,PLAYER_INFO_Y)
        print_at(f"Your MP: {None}/{None}",PLAYER_INFO_X,PLAYER_INFO_Y+1)
        for y in range(0,FIELD_HEIGHT):
            for x in range(1,FIELD_WIDTH+1):
                if self.player.field[x-1][y]:
                    print_at("X",PLAYER_INFO_X+x,PLAYER_INFO_Y+3+y)
                else:
                    print_at(".",PLAYER_INFO_X+x,PLAYER_INFO_Y+3+y)

        # print cards in your hand 
        print_at("Your Hand:",PLAYER_INFO_X,PLAYER_INFO_Y+FIELD_HEIGHT+4)

    def main_loop(self):
        self.initialize_game()
        running_game = True
        while running_game:
            if not self.turn_order:
                self.turn_order = self.set_turn_order()
            turn_selector = self.turn_order.pop()
            self.current_character = turn_selector[0]
            
            # print information on screen
            self.display()
            
             
            # # if player character 
            if turn_selector[1] == 1:
                input("What will you do?")
            # # if CPU
            elif turn_selector[1] == 0:
                input("Press Enter")


if __name__ == "__main__":

    # Set the random seed
    random.seed(time.time())

    # load the card database json
    with open('extracted_card_data.json','r') as card_data:
        card_database = json.load(card_data)

    main_simulator = Simulator()

    main_simulator.main_loop()