# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ./static/python/map_tile.py                                           #
# --------------------------------------------------------------------------- #


class Map_Tile(object):
    def __init__(self):
        self.pit = False
        self.breeze = False
        self.door = False

        self.wumpus = False
        self.smell = False

        self.player = False
        self.footsteps = False
        self.life_potion = False
        self.ability_potion = False
        self.arrow = False
        self.gold = False

    def is_hazard(self):
        return (self.wumpus is True) or (self.pit is True)

    def is_empty(self):
        if self.pit or self.breeze or self.door or self.wumpus or self.smell\
            or self.life_potion or self.ability_potion or self.arrow or self.gold:

            return False

        else:
            return True