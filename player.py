
'''
    hand - current hand of the player
    health/max_health - current health of the player's main character
    mp/max_mp - current mp of the player's party
    field - position of party members for the player's party
    deck - the deck the player is using 
'''
import copy
from character import Character
from deck import Deck
from game_settings import FIELD_HEIGHT, FIELD_WIDTH, MAX_MP

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

    def recharge_mp(self):
        self.mp += 3
        self.mp = self.mp % self.max_mp

    def __str__(self):
        returned_str = ""
        returned_str += f"NAME: {self.name}\n"
        returned_str += f"TYPE: {self.char_type}\n"
        returned_str += f"HP: {self.health}/{self.max_health}\n"
        returned_str += f"MP: {self.mp}/{self.max_mp}\n"
        returned_str += f"SPEED: {self.speed}\n"
        returned_str += f"FIELD:\n"

        party_members = []

        for y in range(FIELD_HEIGHT):
            for x in range(FIELD_WIDTH):
                if self.field[x][y]:
                    returned_str += "X "
                    party_members.append(self.field[x][y])
                else:
                    returned_str += ". "
            returned_str += "\n"
        returned_str += "\n"

        returned_str += "\nPARTY:\n"
        for character in party_members:
            if character.char_type != "Player":
                returned_str += f'{str(character)}\n'
            else:
                returned_str += 'PLAYER CHARACTER\n'
                
        return returned_str
