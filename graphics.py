
# display functions
from game_settings import FIELD_HEIGHT


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

# display information
TURN_ORDER_X = 50
TURN_ORDER_Y = 3

ENEMY_INFO_X = 0
ENEMY_INFO_Y = TURN_ORDER_Y 

PLAYER_INFO_X = ENEMY_INFO_X
PLAYER_INFO_Y = ENEMY_INFO_Y+10

PLAYER_INPUT_X = PLAYER_INFO_X
PLAYER_INPUT_Y = PLAYER_INFO_Y+FIELD_HEIGHT+20

NEXT_CARD_IN_DECK_X = TURN_ORDER_X+10
NEXT_CARD_IN_DECK_Y = PLAYER_INFO_Y+5
