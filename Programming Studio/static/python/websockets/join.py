# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ../python/websockets/join.py                                          #
# --------------------------------------------------------------------------- #


# Program Imports
import tornado.websocket
import logging
import __builtin__
from threading import Timer


# Import logger function
print_logger = logging.getLogger('game_console_log')


# Global list of all active host objects.
active_join_screens = {}
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

    for connection in active_join_screens.keys():
        if active_join_screens[connection]['num_retries'] == 0:
            player_name = active_join_screens[connection]['name']
            global_server_state.remove_player(player_name)
            connections_to_remove.append(connection)
        else:
            active_join_screens[connection]['num_retries'] = active_join_screens[connection]['num_retries'] - 1
            try:
                connection.write_message("Ping")
                request_active_games(connection)
            except Exception:
                print_logger.debug("[DEBUG]: Ping to " + str(active_join_screens[connection])\
                    + " host websocket failed")

    for dead_connection in connections_to_remove:
        del active_join_screens[dead_connection]

    if len(active_join_screens) > 0:
        heartbeat_timer.cancel()
        heartbeat_timer = Timer(1, issue_heartbeat)
        heartbeat_timer.start()
    else:
        heartbeat_timer.cancel()


class JoinWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True

    def open(self, _):
        global heartbeat_timer

        if len(active_join_screens) == 0:
            heartbeat_timer = Timer(1, issue_heartbeat)
            heartbeat_timer.start()

        active_join_screens.update({self : {'name' : "", 'num_retries' : 5}})

    @tornado.web.asynchronous
    def on_message(self, message):

        print_logger.debug("[RECIEVED]: " + message)

        if message == "Pong":
            if active_join_screens[self]['num_retries'] < 6:
                active_join_screens[self]['num_retries'] = active_join_screens[self]['num_retries'] + 1

        elif "Name:" in message:
            active_join_screens[self]['name'] = message.replace("Name:", "").replace("%20", "")

        elif message == "RequestActiveGames":
            request_active_games(self)

        elif "CleanUp" in message:
            clean_up(self, message)

        elif "Join" in message:
            join_game(self, message)

        else:
            # Add more message handlers here as required
            pass

    def on_close(self):
        pass


def request_active_games(websocket_object):
    """
    The join screen is intended as a wait lobby to display all games
    that could house another player.  This method serves all games
    that currently exist in global_server_state that could possibly be
    joined.

    Input Arguments:
        - websocket_object: An instance of the players websocket

    Error Checking:
        - None
    """
    websocket_object.write_message("ClearList")
    for game in global_server_state.games:
        if (len(game.players) == 1) and game.ready_to_join:
            websocket_object.write_message("Game:" + game.game_name + ";Mode:" + game.mode\
                + ";Difficulty:" + game.difficulty)
            print_logger.warning("[SENT]: Game:" + game.game_name + ";Mode:"\
                + game.mode + ";Difficulty:" + game.difficulty)


def clean_up(websocket_object, message):
    """
    Removes the player from the database in the event that they press the back button.

    Input Arguments:
        - websocket_object: An instance of the players websocket
        - mesage: The full string message sent by the player

    Error Checking:
        - None
    """

    player_name = message.replace("CleanUp:", "").replace("%20", " ")
    global_server_state.remove_player(player_name)

    del active_join_screens[websocket_object]

    websocket_object.write_message("CleanUpSuccessful")
    print_logger.warning("[SENT]: CleanUpSuccessful")


def join_game(websocket_object, message):
    """
    Attaches the player to the requested game.

    Input Arguments:
        - websocket_object: An instance of the players websocket
        - mesage: The full string message sent by the player

    Error Checking:
        - None
    """

    message = message.replace("Join:", "").replace("%20", " ").split(":")
    player_name = message[0]
    game_name = message[1]

    if len(global_server_state.get_game(game_name).players) == 1:
        del active_join_screens[websocket_object]
        global_server_state.add_to_game(player_name, game_name)
        websocket_object.write_message("JoinSuccessful")
        print_logger.warning("[SENT]: JoinSuccessful")

    else:
        websocket_object.write_message("JoinFail")
        print_logger.warning("[SENT]: JoinFail")