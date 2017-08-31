# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ../python/websockets/victory.py                                       #
# --------------------------------------------------------------------------- #


# Program Imports
import tornado.websocket
import logging
import __builtin__
from threading import Timer


# Import logger function
print_logger = logging.getLogger('game_console_log')


# Global list of all active host objects.
active_victory_screens = {}
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

    for connection in active_victory_screens.keys():
        if active_victory_screens[connection]['num_retries'] == 0:
            player_name = active_victory_screens[connection]['name']
            player_object = global_server_state.get_player(player_name)

            print "Clean Up Victory"

            try:
                game_object = None
                for game in global_server_state.games:
                    if player_object in game.players:
                        game_object = game
                
                global_server_state.remove_game(game_object)
            except Exception:
                print_logger.debug("[DEBUG]: Unexpected behavior while attempting to remove player/game")

            try:
                other_player_object = None
                for player in game_object.players:
                    if player.name != player_name:
                        other_player_object = player
            except Exception:
                print_logger.debug("[DEBUG]: Unexpected behavior while attempting to remove player/game")

            try:
                other_player_object.web_socket.write_message("Victory")
            except Exception:
                print_logger.debug("[DEBUG]: Unexpected behavior while attempting to remove player/game")

            try:
                global_server_state.remove_player(player_name)
            except Exception:
                print_logger.debug("[DEBUG]: Unexpected behavior while attempting to remove player/game")

            try:
                global_server_state.remove_player(other_player)
                global_server_state.remove_game(game_object)

            except Exception:
                print_logger.debug("[DEBUG]: Unexpected behavior while attempting to remove player/game")

            connections_to_remove.append(connection)

        else:
            active_victory_screens[connection]['num_retries'] = active_victory_screens[connection]['num_retries'] - 1
            try:
                connection.write_message("Ping")
            except Exception:
                print_logger.debug("[DEBUG]: Ping to %s host websocket failed" % str(active_victory_screens[connection]))

    for dead_connection in connections_to_remove:
        del active_victory_screens[dead_connection]

    if len(active_victory_screens) > 0:
        heartbeat_timer.cancel()
        heartbeat_timer = Timer(1, issue_heartbeat)
        heartbeat_timer.start()
    else:
        heartbeat_timer.cancel()


class VictoryWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True

    def open(self, _):
        global heartbeat_timer
        global active_victory_screens

        if len(active_victory_screens) == 0:
            heartbeat_timer = Timer(1, issue_heartbeat)
            heartbeat_timer.start()

        active_victory_screens.update({self : {'name' : "", 'num_retries' : 5}})

    @tornado.web.asynchronous
    def on_message(self, message):
        global active_victory_screens

        print_logger.debug("[RECIEVED]: " + message)

        if message == "Pong":
            if active_victory_screens[self]['num_retries'] < 6:
                active_victory_screens[self]['num_retries'] = active_victory_screens[self]['num_retries'] + 1

        elif "Name:" in message:
            active_victory_screens[self]['name'] = message.replace("Name:", "").replace("%20", "")
            try:
                player_name = active_victory_screens[self]['name']
                
                game_object = None
                for game in global_server_state.games:
                    for player in game.players:
                        if player.name == player_name:
                            game_object = game
                    
                global_server_state.games.remove(game_object)
            except Exception:
                pass

    def on_close(self):
        pass