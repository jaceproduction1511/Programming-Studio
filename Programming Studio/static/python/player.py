# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ./static/python/player.py                                             #
# --------------------------------------------------------------------------- #


class Player(object):
    """monitor player status"""
    def __init__(self, name_in):
        self.name = name_in
        self.player_class = ''
        self.ability_uses = 0
        self.arrow = 1
        self.gold = False
        self.life = 0
        self.x = 0
        self.y = 0
        self.commit = False
        self.web_socket = None

    def set_class(self, player_class):
        self.player_class = player_class
        if self.player_class == "scout":
            self.ability_uses = 5
        elif self.player_class == "hunter":
            self.arrow += 1
        elif self.player_class == "survivor":
            self.life += 1
        elif self.player_class == "prospector":
            pass

    def set_difficulty_constraints(self, difficulty):
        if difficulty == "easy":
            self.life += 0
        elif difficulty == "medium":
            self.life -= 1
        elif difficulty == "hard":
            self.life -= 2

    def set_ability_uses(self, number):
        if self.player_class == "scout":
            self.ability_uses = number