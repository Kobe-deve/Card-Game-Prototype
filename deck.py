# class for handling decks 
import copy
import random

from game_settings import MAX_HAND_SIZE

class Deck:
    def __init__(self,name="New Deck",deck_list=[]):
        self.name = name
        self.num_cards = len(deck_list)
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
