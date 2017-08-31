# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ./static/python/websockets/character.py                               #
# --------------------------------------------------------------------------- #


# Program Imports
import tornado.websocket
import logging
import __builtin__
from threading import Timer

# Import logger function
print_logger = logging.getLogger('game_console_log')

# Global list of all active host objects.
active_character_screens = {}
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

    for connection in active_character_screens.keys():
        if active_character_screens[connection]['num_retries'] == 0:
            player_name = active_character_screens[connection]['name']

            game_object = None
            for game in global_server_state.games:
                for player in game.players:
                    if player_name == player.name:
                        game_object = game

            global_server_state.remove_player(player_name)
            global_server_state.remove_game(game_object)
            connections_to_remove.append(connection)
        else:
            active_character_screens[connection]['num_retries'] = active_character_screens[connection]['num_retries'] - 1
            try:
                connection.write_message("Ping")
            except Exception:
                print_logger.debug("[DEBUG]: Ping to " + str(active_character_screens[connection]) + " host websocket failed")

    for dead_connection in connections_to_remove:
        del active_character_screens[dead_connection]

    if len(active_character_screens) > 0:
        heartbeat_timer = Timer(1, issue_heartbeat)
        heartbeat_timer.start()
    else:
        heartbeat_timer.cancel()


class CharacterWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True

    def open(self):
        global heartbeat_timer

        if len(active_character_screens) == 0:
            heartbeat_timer = Timer(1, issue_heartbeat)
            heartbeat_timer.start()

        active_character_screens.update({self : {'name' : "", 'num_retries' : 5}})

    @tornado.web.asynchronous
    def on_message(self, message):

        print_logger.warning("[RECIEVED]: " + message)

        if message == "Pong":
            if active_character_screens[self]['num_retries'] < 6:
                active_character_screens[self]['num_retries'] = active_character_screens[self]['num_retries'] + 1

        elif "PlayerName" in message:
            active_character_screens[self]['name'] = message.replace("PlayerName:", "").replace("%20", " ")

        if "SetCharacter:" in message:
            message = message.replace("%20", " ").replace("SetCharacter:", "").split(":")
            player_name = message[0]
            chosen_character = message[1]
            player_object = global_server_state.get_player(player_name)
            player_object.set_class(chosen_character)
            if self in active_character_screens.keys():
                del active_character_screens[self]
            self.write_message("CharacterSet")
            print_logger.warning("[SENT]: CharacterSet")

        elif "Return:" in message:
            player_name = message.replace("%20", " ").replace("Return:", "")
            player_object = global_server_state.get_player(player_name)

            game_object = None
            for game in global_server_state.games:
                if player_object in game.players:
                    game_object = game

            player_object.player_class = ''
            if player_object == game_object.host:
                if self in active_character_screens.keys():
                    del active_character_screens[self]

                self.write_message("ReturnHost")
                print_logger.warning("[SENT]: ReturnHost")
            else:
                if self in active_character_screens.keys():
                    del active_character_screens[self]

                self.write_message("ReturnJoin")
                print_logger.warning("[SENT]: ReturnJoin")
                game_object.remove_player(player_object)

    def on_close(self):
        pass