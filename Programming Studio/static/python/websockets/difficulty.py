# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ../python/websockets/difficulty.py                                    #
# --------------------------------------------------------------------------- #


# Program Imports
import tornado.websocket
import logging
import __builtin__
from threading import Timer


# Import logger function
print_logger = logging.getLogger('game_console_log')

# Global list of all active host objects.
active_difficulty_screens = {}
heartbeat_timer = None


def issue_heartbeat():
    """
    There is a high probability that either users will close out of their browser
    window or that something could go wrong with the client's network connection.
    In order to prevent this, regularly ping all open connections to ensure data
    consistency.

    Input Arguments:
        - None

    Error Checking:
        - None
    """

    global heartbeat_timer
    connections_to_remove = []

    for connection in active_difficulty_screens.keys():
        if active_difficulty_screens[connection]['num_retries'] == 0:
            player_name = active_difficulty_screens[connection]['name']

            game_object = None
            for game in global_server_state.games:
                for player in game.players:
                    if player_name == player.name:
                        game_object = game

            global_server_state.remove_player(player_name)
            global_server_state.remove_game(game_object)
            connections_to_remove.append(connection)
        else:
            active_difficulty_screens[connection]['num_retries'] = active_difficulty_screens[connection]['num_retries'] - 1
            try:
                connection.write_message("Ping")
            except Exception:
                print_logger.debug("[DEBUG]: Ping to " + str(active_difficulty_screens[connection]) + " host websocket failed")

    for dead_connection in connections_to_remove:
        del active_difficulty_screens[dead_connection]

    if len(active_difficulty_screens) > 0:
        heartbeat_timer = Timer(1, issue_heartbeat)
        heartbeat_timer.start()
    else:
        heartbeat_timer.cancel()


class DifficultyWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True

    def open(self):
        global heartbeat_timer

        if len(active_difficulty_screens) == 0:
            heartbeat_timer = Timer(1, issue_heartbeat)
            heartbeat_timer.start()

        active_difficulty_screens.update({self : {'name' : "", 'num_retries' : 5}})

    @tornado.web.asynchronous
    def on_message(self, message):

        print_logger.warning("[RECIEVED]: " + message)

        if message == "Pong":
            if active_difficulty_screens[self]['num_retries'] < 6:
                active_difficulty_screens[self]['num_retries'] = active_difficulty_screens[self]['num_retries'] + 1

        elif "PlayerName" in message:
            active_difficulty_screens[self]['name'] = message.replace("PlayerName:", "").replace("%20", " ")

        elif "CleanUp" in message:
            player_name = message.replace("CleanUp:", "").replace("%20", " ")
            player_object = global_server_state.get_player(player_name)

            if self in active_difficulty_screens.keys():
                del active_difficulty_screens[self]

            game_object = None
            for game in global_server_state.games:
                if player_object in game.players:
                    game_object = game

            global_server_state.remove_game(game_object)
            self.write_message("CleanUpSuccessful")
            print_logger.warning("[SENT]: CleanUpSuccessful")

        elif "Difficulty:" in message:
            message = message.replace("Difficulty:", "").replace("%20", " ").split(":")
            player_object = global_server_state.get_player(message[0])

            game_object = None
            for game in global_server_state.games:
                if player_object in game.players:
                    game_object = game

            game_object.difficulty = message[1]

            del active_difficulty_screens[self]
            self.write_message("DifficultySet")
            print_logger.warning("[SENT]: DifficultySet")

        else:
            self.write_message("Programmer Oops")
            print_logger.warning("[SENT]: Programmer oops")

    def on_close(self):
        pass