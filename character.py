# class for characters in battle

from game_settings import MAX_HEALTH, MAX_MP


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
    
    def __str__(self):
        returned_str = ""
        returned_str += f"NAME: {self.name}\n"
        returned_str += f"TYPE: {self.char_type}\n"
        returned_str += f"HP: {self.health}/{self.max_health}\n"
        returned_str += f"MP: {self.mp}/{self.max_mp}\n"
        returned_str += f"SPEED: {self.speed}\n"
        return returned_str
