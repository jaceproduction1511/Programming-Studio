# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ./static/python/game_state.py                                         #
# --------------------------------------------------------------------------- #


from map_tile import Map_Tile
import random
import copy


class Game_State(object):
    """
    Keep tracks of game map and all that it contains
    """

    def __init__(self, player1_in, player2_in, mode_in, difficulty_in):
        """
        Initialize the game state

        Data Structure:
            -self.tiles: self.tiles on the map
            -self.turns: current turns
        """

        self.player1 = player1_in
        self.player2 = player2_in
        self.players = [self.player1, self.player2]
        self.difficulty = difficulty_in
        self.xmax = None
        self.ymax = None
        self.tiles = []
        self.mode = mode_in
        self.num_wumpuses = None

        if self.difficulty == "easy":
            self.players[0].life += 3
            self.players[1].life += 3
        elif self.difficulty == "medium":
            self.players[0].life += 2
            self.players[1].life += 2
        elif self.difficulty == "hard":
            self.players[0].life += 1
            self.players[1].life += 1

    def gen_map(self):
        wumpus_count = None

        #these variables store the percentage chances for things in map generation
        pit_gen_chance = None
        wumpus_gen_chance = None
        arrow_gen_chance = None
        life_potion_gen_chance = None
        ability_potion_gen_chance = None

        #set values based on difficulty level
        if self.difficulty == "easy":
            self.xmax = 13
            self.ymax = 9
            self.num_wumpuses = 1
            pit_gen_chance = 6
            wumpus_gen_chance = 3
            arrow_gen_chance = 15
            life_potion_gen_chance = 12
            ability_potion_gen_chance = 8

        elif self.difficulty == "medium":
            self.xmax = 13
            self.ymax = 9
            self.num_wumpuses = 3
            pit_gen_chance = 9
            wumpus_gen_chance = 4
            arrow_gen_chance = 13
            life_potion_gen_chance = 9
            ability_potion_gen_chance = 7

        elif self.difficulty == "hard":
            self.xmax = 13
            self.ymax = 9
            self.num_wumpuses = 3
            pit_gen_chance = 12
            wumpus_gen_chance = 4
            arrow_gen_chance = 11
            life_potion_gen_chance = 6
            ability_potion_gen_chance = 6

        wumpus_count = copy.deepcopy(self.num_wumpuses)
        
        #initialize & make map self.tiles
        for x in range(0, self.xmax):
            self.tiles.append([])
            for y in range(0, self.ymax):
                self.tiles[x].append(Map_Tile())

        #generate gold
        self.tiles[random.randint(1, self.xmax - 1)][random.randint(0, self.ymax - 1)].gold = True

        #randomly generate items and hazards in self.tiles
        for x in range(0, self.xmax):
            for y in range(0, self.ymax):
                #make sure we dont generate anythng where the door should be
                if (x == 0 and y == 0) == False:
                    #only generate pit if there is no gold in the tile
                    self.tiles[x][y].pit = (random.randint(0,100) < pit_gen_chance)\
                        and not self.tiles[x][y].gold
                        
                    #only generate wumpus if there is no gold in the tile, no pit, and the max number of wumpuses has not been exceeded
                    self.tiles[x][y].wumpus = (random.randint(0,100) < wumpus_gen_chance)\
                        and (wumpus_count != 0) and not self.tiles[x][y].gold\
                        and not self.tiles[x][y].pit
                        
                    self.tiles[x][y].arrow = (random.randint(0,100) < arrow_gen_chance)\
                        and not self.tiles[x][y].pit
                        
                    self.tiles[x][y].life_potion = (random.randint(0,100) < life_potion_gen_chance)\
                        and not self.tiles[x][y].pit
                        
                    self.tiles[x][y].ability_potion = (random.randint(0,100) < ability_potion_gen_chance)\
                        and not self.tiles[x][y].pit

                    #decrement things that have been placed and have a max number possible
                    if self.tiles[x][y].wumpus == True:
                        wumpus_count -= 1

        #forcibly ensure that all the required wumpuses are generated
        while wumpus_count > 0:
            new_x = random.randint(1, self.xmax - 1)
            new_y = random.randint(1, self.ymax - 1)
            
            if not self.tiles[new_x][new_y].gold and not self.tiles[new_x][new_y].wumpus\
                and not self.tiles[new_x][new_y].pit:
                    
                self.tiles[new_x][new_y].wumpus = True
                wumpus_count -= 1


        #set up perceptions in adjacent self.tiles from hazards
        for x in range(0, self.xmax):
            for y in range(0, self.ymax):
                if self.tiles[x][y].pit == True:
                    if self.is_valid_direction(x, y, "left") and not self.tiles[x - 1][y].pit:
                        self.tiles[x-1][y].breeze = True
                        
                    if self.is_valid_direction(x, y, "right") and not self.tiles[x + 1][y].pit:
                        self.tiles[x+1][y].breeze = True
                        
                    if self.is_valid_direction(x, y, "down") and not self.tiles[x][y + 1].pit:
                        self.tiles[x][y+1].breeze = True
                        
                    if self.is_valid_direction(x, y, "up") and not self.tiles[x][y - 1].pit:
                        self.tiles[x][y-1].breeze = True
        
        self.refresh_smells()

        #ensure that the exit door is the only thing in tile 0,0
        self.tiles[0][0].door = True
        self.tiles[0][0].wumpus = False
        self.tiles[0][0].pit = False

        #place players randomly
        for playernum in range(0, len(self.players)):
            new_x = random.randint(1, self.xmax - 1)
            new_y = random.randint(1, self.ymax - 1)
            #find valid coordinates for player placement
            
            while not self.tiles[new_x][new_y].is_empty() or self.tiles[new_x][new_y].player:
                new_x = random.randint(1, self.xmax - 1)
                new_y = random.randint(1, self.ymax - 1)

            #place player
            self.players[playernum].x = new_x
            self.players[playernum].y = new_y
            self.tiles[new_x][new_y].player = True

    def is_valid_pick_up(self, player):
        if self.tiles[player.x][player.y].gold\
            or self.tiles[player.x][player.y].life_potion\
            or self.tiles[player.x][player.y].ability_potion\
            or self.tiles[player.x][player.y].arrow:
            
            return True
        else:
            return False


    def is_valid_location(self, x, y):
        return x < self.xmax and x >= 0 and y < self.ymax and y >= 0


    def is_valid_direction(self, x, y, direction):
        if direction   == "up":
            return self.is_valid_location(x, y - 1)
        elif direction == "down":
            return self.is_valid_location(x, y + 1)
        elif direction == "left":
            return self.is_valid_location(x - 1, y)
        elif direction == "right":
            return self.is_valid_location(x + 1, y)


    def is_valid_move(self, player, direction):
        return self.is_valid_direction(player.x, player.y, direction)


    def get_percepts(self, player):
  
        other_player_flag = (self.player1.x == self.player2.x) and (self.player1.y == self.player2.y)

        #perception_str = output string
        perception_str  = "" + str(player.x) + "," + str(player.y) + ","
        perception_str += ("pit," if(self.tiles[player.x][player.y].pit) else "")
        perception_str += ("breeze," if(self.tiles[player.x][player.y].breeze) else "")
        perception_str += ("door," if(self.tiles[player.x][player.y].door) else "")
        perception_str += ("wumpus," if(self.tiles[player.x][player.y].wumpus) else "")
        perception_str += ("smell," if(self.tiles[player.x][player.y].smell) else "")
        perception_str += ("player," if(other_player_flag) else "")
        perception_str += ("arrow," if(self.tiles[player.x][player.y].arrow) else "")
        perception_str += ("life_potion," if(self.tiles[player.x][player.y].life_potion) else "")
        perception_str += ("ability_potion," if(self.tiles[player.x][player.y].ability_potion) else "")

        if player.player_class == "prospector":
            perception_str += ("glitter," if((self.is_prospector_by_gold(player))\
                or (self.tiles[player.x][player.y].gold)) else "")
        else:
            perception_str += ("glitter," if(self.tiles[player.x][player.y].gold) else "")

        perception_str += ("gold,"  if(self.tiles[player.x][player.y].gold) else "")
        perception_str += ("door,"   if(self.tiles[player.x][player.y].door) else "")
        perception_str += ("empty," if self.tiles[player.x][player.y].is_empty() else "")

        if (self.is_valid_move(player, "up") and self.tiles[player.x][player.y - 1].player)\
            or (self.is_valid_move(player, "down") and self.tiles[player.x][player.y + 1].player)\
            or (self.is_valid_move(player, "left") and self.tiles[player.x - 1][player.y].player)\
            or (self.is_valid_move(player, "right") and self.tiles[player.x + 1][player.y].player):

            perception_str += "footsteps,"

        return perception_str

    def scout(self, Scx, Scy):
        
        perception_str = "" + str(Scx) + "," + str(Scy) + ","
        perception_str += ("pit," if (self.tiles[Scx][Scy].pit) else "")
        perception_str += ("breeze," if (self.tiles[Scx][Scy].breeze) else "")
        perception_str += ("wumpus," if (self.tiles[Scx][Scy].wumpus) else "")
        perception_str += ("smell," if (self.tiles[Scx][Scy].smell) else "")
        perception_str += ("arrow," if (self.tiles[Scx][Scy].arrow) else "")
        perception_str += ("life_potion," if (self.tiles[Scx][Scy].life_potion) else "")
        perception_str += ("ability_potion," if (self.tiles[Scx][Scy].ability_potion) else "")
        perception_str += ("glitter," if (self.tiles[Scx][Scy].gold) else "")
        perception_str += ("gold," if (self.tiles[Scx][Scy].gold) else "")
        perception_str += ("empty," if (self.tiles[Scx][Scy].is_empty()) else "")

        return perception_str


    def refresh_smells(self):
        """
        go through the map and update where smells should be
        dont put smells on top of wumpuses
        """
        
        for x in range(0, self.xmax):
            for y in range(0, self.ymax):
                if self.tiles[x][y].wumpus == True:
                    if self.is_valid_direction(x, y, "left") and (self.tiles[x - 1][y].wumpus is False):
                        self.tiles[x-1][y].smell = True
                    if self.is_valid_direction(x, y, "right") and (self.tiles[x + 1][y].wumpus is False):
                        self.tiles[x+1][y].smell = True
                    if self.is_valid_direction(x, y, "down") and (self.tiles[x][y + 1].wumpus is False):
                        self.tiles[x][y+1].smell = True
                    if self.is_valid_direction(x, y, "up") and (self.tiles[x][y - 1].wumpus is False):
                        self.tiles[x][y-1].smell = True

    #(Add a wumpus to the map)
    def add_wumpus(self, x, y):
        if self.is_valid_location(x, y) and not self.tiles[x][y].wumpus and not self.tiles[x][y].pit\
                and not self.tiles[x][y].player:
            self.tiles[x][y].wumpus = True
            self.refresh_smells()
            self.num_wumpuses += 1
            return True
        return False

    #(remove the wumpus at (x,y))
    def remove_wumpus(self, x, y):
        if self.is_valid_location(x , y) and self.tiles[x][y].wumpus:
            #TO DO: remove smells around the old wumpus location
            #take into account the possibility of other wumpuses nearby
            
            self.tiles[x][y].wumpus = False
            if self.is_valid_direction(x, y, "up"):
                self.tiles[x][y - 1].smell = False
            if self.is_valid_direction(x, y, "down"):
                self.tiles[x][y + 1].smell = False
            if self.is_valid_direction(x, y, "left"):
                self.tiles[x - 1][y].smell = False
            if self.is_valid_direction(x, y, "right"):
                self.tiles[x + 1][y].smell = False

            self.refresh_smells()
            self.num_wumpuses -= 1
            return True
        return False

    #the wumpus might know where it is
    #the wumpus knows where it wants to be
    def move_wumpus(self, x1, y1, x2, y2):
        if self.remove_wumpus(x1, y1):
            if self.add_wumpus(x2, y2):
                print "Wumpus moved from (" + str(x1) + "," + str(y1) + ") to (" + str(x2) + "," + str(y2) + ")"
                return True
            else:
                #add the wumpus back if you cant place it in the new location after removal
                print "could not move wumpus from (" + str(x1) + "," + str(y1) + ") to (" + str(x2) + "," + str(y2) + ")"
                self.add_wumpus(x1, y1)
        return False

    def move_wumpus_direction(self, x, y, direction):
        if direction   == "up":
            self.move_wumpus(x, y, x, y - 1)
        elif direction == "down":
            self.move_wumpus(x, y, x, y + 1)
        elif direction == "left":
            self.move_wumpus(x, y, x - 1, y)
        elif direction == "right":
            self.move_wumpus(x, y, x + 1, y)
        else:
            print "unexpected direction game state move_wumpus: " + direction
            return False
        return True

    #Move the player in the requested direction
    def move_player(self, player, direction):
        old_x   = player.x
        old_y   = player.y
        new_x   = old_x
        new_y   = old_y
        message = ""

        if direction   == "up":
            new_y -= 1
        elif direction == "down":
            new_y += 1
        elif direction == "left":
            new_x -= 1
        elif direction == "right":
            new_x += 1

        #if the player will die, dont move them, and kill them
        if self.tiles[new_x][new_y].pit == True:
            message = self.kill(player, "pit")

        elif self.tiles[new_x][new_y].wumpus == True:
            message =  self.kill(player, "wumpus")

        #set new player internal coordinates
        player.x = new_x
        player.y = new_y

        self.tiles[player.x][player.y].player = True
        self.tiles[old_x][old_y].player = False


        return message


    #get the player to fire the arrow
    #return values for the user:
    #"cant fire the arrow, you are out."
    #"you fire the arrow (direction). No response."
    #return values for the parser:
    #"wumpus killed"
    #"player killed"
    def pick_up(self, player):
        if self.tiles[player.x][player.y].gold == True:
            player.gold = True
            player.web_socket.write_message("Notification:rgb(57, 176, 219):The gold has been picked up!")
            self.get_other_player(player).web_socket.write_message("Notification:rgb(57, 176, 219):The gold has been picked up!")
            self.tiles[player.x][player.y].gold = False
        if self.tiles[player.x][player.y].life_potion == True:
            player.life += 1
            self.tiles[player.x][player.y].life_potion = False
        if self.tiles[player.x][player.y].ability_potion == True:
            player.ability_uses += 1
            self.tiles[player.x][player.y].ability_potion = False
        if self.tiles[player.x][player.y].arrow == True:
            player.arrow += 1
            self.tiles[player.x][player.y].arrow = False


    def fire_arrow(self, player, direction):
        """
        negative y direction loop starting at player.y - 1
        check tiles in the direction the player fires
        when we encounter a killable object, kill it
        """

        if player.arrow == 0:
            return "rgb(57, 176, 219):Out of arrows!"

        player.arrow -= 1

        if direction == "up":
            y = player.y - 1
            while y >= 0:
                if self.tiles[player.x][y].wumpus == True:
                    self.remove_wumpus(player.x, y)
                    return "WumpusDead:" + str(player.x) + ':' + str(y)
                if self.tiles[player.x][y].player == True:
                    return "player killed"
                y -= 1

            self.tiles[player.x][0].arrow = True
            return "yellow:you fire the arrow " + str(direction) + " into the abyss."

        elif direction == "down":
            for y in range(player.y + 1, self.ymax):
                if self.tiles[player.x][y].wumpus == True:
                    self.remove_wumpus(player.x, y)
                    return "WumpusDead:" + str(player.x) + ':' + str(y)
                if self.tiles[player.x][y].player == True:
                    return "player killed"

            self.tiles[player.x][self.ymax - 1].arrow = True
            return "yellow:you fire the arrow " + str(direction) + " into the abyss."

        elif direction == "left":
            x = player.x - 1
            while x >= 0:
                if self.tiles[x][player.y].wumpus == True:
                    self.remove_wumpus(x, player.y)
                    return "WumpusDead:" + str(x) + ':' + str(player.y)
                if self.tiles[x][player.y].player == True:
                    return "player killed"
                x -= 1

            self.tiles[0][player.y].arrow = True
            return "yellow:you fire the arrow " + str(direction) + " into the abyss."

        elif direction == "right":
            for x in range(player.x + 1, self.xmax):
                if self.tiles[x][player.y].wumpus == True:
                    self.remove_wumpus(x, player.y)
                    return "WumpusDead:" + str(x) + ':' + str(player.y)
                if self.tiles[x][player.y].player == True:
                    return "player killed"

            self.tiles[self.xmax - 1][player.y].arrow = True
            return "yellow:you fire the arrow " + str(direction) + " into the abyss."
        else:
            return "bad input, invalid direction PLAYER SHOULDNT SEE THIS"


    def kill(self, player, cause_of_death):
        player.life -= 1

        #custom death messages for different causes of death

        if cause_of_death == "arrow":
            player.web_socket.write_message('Notification:red:An Arrow impales you in ' +
                'your left kneecap. You clutch your leg and embrace death')
            print "killed by arrow DEBUG game_state.py line 391"
        elif cause_of_death == "wumpus":
            player.web_socket.write_message("Notification:red:The Wumpus lunges and tears away at your flesh with it's teeth.")
        elif cause_of_death == "pit":
            player.web_socket.write_message("Notification:red:You fall down into the pit. Legend says that you're still falling to this day.")
            print "killed by pit DEBUG game_state.py line 396"
        elif cause_of_death == "duel":
            player.web_socket.write_message("Notification:Death by duel.")
        else:
            player.web_socket.write_message("Notification:Death by SNU SNU, PLAYER SHOULDNT SEE THIS EVER.")

        #drop gold in a random location

        if player.gold == True:
            player.gold = False
            tempx = random.randint(1,self.xmax - 1)
            tempy = random.randint(0,self.ymax - 1)
            #PYTHON, WHYYYY, i want a do-while loop :(
            while self.tiles[tempx][tempy].is_empty() == False or self.tiles[tempx][tempy].player == True:
                tempx = random.randint(1,self.xmax - 1)
                tempy = random.randint(0,self.ymax - 1)

            self.tiles[tempx][tempy].gold = True
            player.web_socket.write_message("Notification:yellow:The gold has been dropped in a random empty tile.")
            self.get_other_player(player).web_socket.write_message("Notification:yellow:The gold has been dropped in a random empty tile.")


        #when the player loses
        if player.life == 0:
            #GAME OVER
            print "Died:dead DEBUG line 410"
            player.web_socket.write_message("Died:Dead")
            self.get_other_player(player).web_socket.write_message("Victory")
            return "Died:Dead"
        else:
            print "Died:still alive DEBUG line 413"
            player.web_socket.write_message("Died:StillAlive")


    def check_victory(self, player):
        if ((self.tiles[player.x][player.y].door == True) and (player.gold == True)):
            return True
        else:
            return False

    """
    Player Class Specific Functions ********************************************
    """

    #returns true if the player is next to gold and is a prospector
    def is_prospector_by_gold(self, player):
        #CHECK ADJACENT SQUARES FOR GOLD

        if((self.is_valid_move(player, "left"))    and (self.tiles[player.x-1][player.y].gold)):
            return True
        elif((self.is_valid_move(player, "right")) and (self.tiles[player.x+1][player.y].gold)):
            return True
        elif((self.is_valid_move(player, "up"))    and (self.tiles[player.x][player.y-1].gold)):
            return True
        elif((self.is_valid_move(player, "down"))  and (self.tiles[player.x][player.y+1].gold)):
            return True
        else:
            return False

    def get_other_player(self, player_object):
        if self.players[0].name == player_object.name:
            return self.players[1]
        else:
            return self.players[0]


    """
    Random Events ***************************************************
    """

    #ask me if this goes bad - The Blonde
    #random events (including wumpus movement)
    def random_event_check(self):

        return_string = ""

        #percent chances for events to happen
        wumpus_move_chance          = None
        life_potion_spawn_chance    = None
        ability_potion_spawn_chance = None

        if self.difficulty   == "easy":
            wumpus_move_chance          = 0.0
            life_potion_spawn_chance    = 2.0
            ability_potion_spawn_chance = 1.0
        elif self.difficulty == "medium":
            wumpus_move_chance          = 25.0
            life_potion_spawn_chance    = 1.0
            ability_potion_spawn_chance = 0.5
        elif self.difficulty == "hard":
            wumpus_move_chance          = 66.7
            life_potion_spawn_chance    = 0.5
            ability_potion_spawn_chance = 0.25
        else:
            print "difficulty was unknown in gen_map: " + self.difficulty

        #RNGesus doing miracles right heyah

        #life potion spawning event
        if (random.random() * 100) < life_potion_spawn_chance:
            new_x = random.randint(1, self.xmax - 1)
            new_y = random.randint(1, self.ymax - 1)
            #find valid coordinates for placement
            while (self.tiles[new_x][new_y].is_empty() == False) or (self.tiles[new_x][new_y].player == True):
                new_x = random.randint(1, self.xmax - 1)
                new_y = random.randint(1, self.ymax - 1)
            self.tiles[new_x][new_y].life_potion = True
            print "life potion placed at: (" + str(new_x) + "," + str(new_y) + ")"
            return_string += "life_potion_added(" + str(new_x) + "," + str(new_y) + "):"

        #ability potion spawnng event
        if (random.random() * 100) < ability_potion_spawn_chance:
            new_x = random.randint(1, self.xmax - 1)
            new_y = random.randint(1, self.ymax - 1)
            #find valid coordinates for placement
            while (self.tiles[new_x][new_y].is_empty() == False) or (self.tiles[new_x][new_y].player == True):
                new_x = random.randint(1, self.xmax - 1)
                new_y = random.randint(1, self.ymax - 1)
            self.tiles[new_x][new_y].ability_potion = True
            print "ability potion placed at: (" + str(new_x) + "," + str(new_y) + ")"
            return_string += "ability_potion_added(" + str(new_x) + "," + str(new_y) + "):"

        #wumpues moving event
        for x in range(0, self.xmax):
            for y in range(0, self.ymax):
                if self.tiles[x][y].wumpus == True:
                    if (random.random() * 100) < wumpus_move_chance:
                        direction = None
                        direction_num = random.randint(1, 4)
                        if direction_num == 1: direction = "up"
                        if direction_num == 2: direction = "down"
                        if direction_num == 3: direction = "left"
                        if direction_num == 4: direction = "right"
                        result = self.move_wumpus_direction(x, y, direction)

                        if result:
                            new_x = x
                            new_y = y
                            if direction   == "up":    new_y -= 1
                            elif direction == "down":  new_y += 1
                            elif direction == "left":  new_x -= 1
                            elif direction == "right": new_x += 1
                            return_string += "wumpus_moved(" + str(x) + "," + str(y) + ")(" + str(new_x) + "," + str(new_y) + "):"

        return return_string