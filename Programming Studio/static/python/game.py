from game_state import Game_State

class Game(object):
    """
    Contains an instance of a game in process
    
    many of the functions here are handlers for the functions in game_state.py
    """

    def __init__(self, name, mode):
        """
        Initialize the game class

        Data Structures:
            -self.players: A list contains all active player of this instance 
            -self.difficulty: desired difficulty 
            -self.mode: desired game mode
            -self.game_state: the state of the game, defined in gamestate.player
            -self.map_size: the size of the map, defined by the numbers of x rows and y collumns
        """
        self.game_state      = None
        self.players         = []
        self.host            = None
        self.mode            = mode
        self.game_name       = name
        self.difficulty      = ""
        self.committed_moves = {}
        self.ready_to_join = False
        

    def fire_arrow(self, player_in, direction):
        """
        Player fires an arrow in a given direction
        
        Potential Return Values:
            - "cant fire the arrow, you are out."
            - "you fire the arrow (direction). No response."
            - "wumpus killed"
            - "player killed"
        """

        return self.game_state.fire_arrow(player_in, direction)

 
    def move_player(self, player, direction):
        self.game_state.move_player(player, direction)
    
    def move_wumpus(self, x, y, direction):
        self.game_state.move_wumpus_direction(x, y, direction)

    def is_valid_move(self, player, direction):
        """
        Given a player and thier desired move (left, right, up, down) a boolean value 
        will indicate if the player can move there.  A player can move to a location 
        if it is within the bounds of the game map.  
        """
        
        return self.game_state.is_valid_move(player, direction)
    
    
    def is_players_commited(self):
        """
        check to see if both players have committed thier moves
        this function name is, in fact, NOT grammatical
        """
    
        return (self.players[0].commit and self.players[1].commit)
    
    
    def is_valid_pick_up(self, player):
        """
        check to see if there is anything at the tile when player want to pick up something. 
        some other comment, I dont wanna feel left out.
        """
    
        return self.game_state.is_valid_pick_up(player)
        
    def pick_up(self, player):
        """
        picks up object in current tile and adds to player's inventory
        """
        self.game_state.pick_up(player)        
        
    def get_percepts(self, player):
        """
        gets all of the percepts for a given player
        return value is a serialized string, detailing data in the map tile the player is in
        NOTE, MAJOR NOTE: the player entry will be present if there is a DIFFERENT player in the same tile        
        """
    
        return self.game_state.get_percepts(player)
    
    # def get_killed(self, player, cause_of_death):
    #     return self.game_state.kill(player, cause_of_death)
    
    #return the other player object (the one that is not the one in the input argument)
    def get_other_player(self, player_object):
        if self.players[0].name == player_object.name:
            return self.players[1]
        else:
            return self.players[0]
        
    
    """
    Modification Functions *****************************************************
    """
    
    #Add a player to the game object    
    def add_player(self, player):
        self.players.append(player)
        
    #Remove a player by object from the game
    #for... you know... <i>reasons</i>
    def remove_player(self, player):
        self.players.remove(player)
    
    #start a game, this initalizes everything, and the game will not work if you dont.
    #protip. use it.
    #even more pro-tip: make sure you have 2 players and a difficulty initalized beforehand
    def start_game(self):
        if len(self.players) != 2:
            return
        
        if self.difficulty == "":
            self.difficulty = "easy"
        
        self.game_state = Game_State(self.players[0], self.players[1], self.mode, self.difficulty)
        self.game_state.gen_map()
        
    #kill the player
    #causes of death: "arrow", "wumpus", "pit", "duel"
    def kill(self, player, cause_of_death):
        return self.game_state.kill(player, cause_of_death)
        
    def Check_Victory(self, player):
        return self.game_state.check_victory(player)
        
    """
    Player Class Specific Functions ********************************************
    """
    
    #returns true if the player is next to gold and is a prospector
    # def is_prospector_by_gold(self, player):
    #     return self.game_state.is_prospector_by_gold(player)
    
    #returns precepts on scout tile
    def Scout(self, Scx, Scy):
        return self.game_state.scout(Scx, Scy)
        
    """
    Random Events ***************************************************
    """
    
    #ask me if this goes bad -Aaron
    #random events (including wumpus movement)
    def random_event_check(self):
        return self.game_state.random_event_check()
        