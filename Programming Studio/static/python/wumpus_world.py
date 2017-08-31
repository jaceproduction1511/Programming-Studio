# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ./static/python/wumpus_workd  .py                                     #
# --------------------------------------------------------------------------- #


from game import Game
from player import Player

class Wumpus_World(object):
    """
    Contains all instances of games that are in progress
    """

    def __init__(self):
        """
        Initialize the wumpusworld class
        Data Structures:
            - self.players: A list containing all active players
            - self.games: A list containing all active games

        Input Arguments:
            - None

        Error Checking:
            - None required
        """

        self.players = []
        self.games = []

    def validate_name(self, name):
        """
        Player's name must be unique.
        Check to ensure that name doesn't already existed.

        Input Arguments:
            - string name: A string corresponding to the name to check

        Error Checking:
            - name must be a string
        """
        for player in self.players:
            if player.name == name:
                return "Failure"

        return "Success"

    def add_player(self, name):
        """
        Add a player into the program by name

        Input Arguments:
            - string name: String name of the person to add

        Error Checking:
            - name must be a string
            - name must be non-NULL
        """
        new_player = Player(name)
        self.players.append(new_player)

    def get_player(self, player_name):
        """
        Given a player name, returns the matching player object

        Input Arguments:
            - player_name: The string name corresponding to the requested
              player object

        Error Checking:
            - name must be a string
        """

        player_object = None
        for player in self.players:
            if player.name == player_name:
                player_object = player

        return player_object

    def get_game(self, game_name):
        """
        Given a game name, returns the matching game object

        Input Arguments:
            - game name: The string name corresponding to the requested
              player object

        Error Checking:
            - name must be a string
        """

        game_object = None
        for game in self.games:
            if game.game_name == game_name:
                game_object = game

        return game_object

    def add_to_game(self, player_name, game_name):
        """
        Adds a player to a game

        Input Arguments:
            - player_name: The name of the player to add
            - game_name: The name of the game to add the player to

        Error Checking:
            - None
        """

        player_object = None
        for player in self.players:
            if player.name == player_name:
                player_object = player

        game_object = None
        for game in self.games:
            if game.game_name == game_name:
                game_object = game

        game_object.players.append(player_object)

    def remove_player(self, name):
        """
        Remove a player from program by name

        Input Arguments:
            - string name: name of the person to remove

        Error Checking:
            - name must be a string
            - name must be non-NULL
        """
        name = name.replace("%20", " ")
        object_to_remove = None
        for player in self.players:
            if player.name == name:
                object_to_remove = player

        if object_to_remove in self.players:
            self.players.remove(object_to_remove)
        else:
            return "PlayerDoesntExist"

    def validate_game_name(self, game_name):
        """
        Player's name must be unique.
        Check to ensure that name doesn't already existed.

        Input Arguments:
            - string name: A string corresponding to the name to check

        Error Checking:
            - name must be a string
        """

        for game in self.games:
            if game.game_name == game_name:
                return "Failure"

        return "Success"

    def add_game(self, game_name, mode):
        """
        Add an instance of a game to the server

        Input Arguments:
            - string host player: name of the player that host the game
            - bool difficulty: desired difficulty
            - bool game mode: desired game mode

        Error Checking:
            - All input arguments must be strings
            - All input arguments must be non-NULL
        """
        new_game = Game(game_name, mode)
        self.games.append(new_game)

    def remove_game(self, game_object):
        """
        Remove an instance of a game from the server

        Input Arguments:
            -string host_player: name of the player that host the game

        Error Checking:
            -All input arguments must be stirng
            -All inpu arguments must be non-NULL
        """

        if game_object in self.games:
            self.games.remove(game_object)