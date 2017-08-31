# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ../python/websockets/host.py                                          #
# --------------------------------------------------------------------------- #


# Program Imports
import tornado.websocket
import logging
import __builtin__
from threading import Timer


# Import logger function
print_logger = logging.getLogger('game_console_log')


# Global list of all active host objects.
active_host_screens = {}
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

    for connection in active_host_screens.keys():
        if active_host_screens[connection]['num_retries'] == 0:
            player_name = active_host_screens[connection]['name']
            global_server_state.remove_player(player_name)
            connections_to_remove.append(connection)
        else:
            active_host_screens[connection]['num_retries'] = active_host_screens[connection]['num_retries'] - 1
            try:
                connection.write_message("Ping")
            except Exception:
                print_logger.debug("[DEBUG]: Ping to " + str(active_host_screens[connection]) + " host websocket failed")

    for dead_connection in connections_to_remove:
        del active_host_screens[dead_connection]

    if len(active_host_screens) > 0:
        heartbeat_timer = Timer(1, issue_heartbeat)
        heartbeat_timer.start()
    else:
        heartbeat_timer.cancel()



class HostWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True

    def open(self, _):
        global heartbeat_timer

        if len(active_host_screens) == 0:
            heartbeat_timer = Timer(1, issue_heartbeat)
            heartbeat_timer.start()

        active_host_screens.update({self : {'name' : "", 'num_retries' : 5}})


    @tornado.web.asynchronous
    def on_message(self, message):

        print_logger.debug("[RECIEVED]: " + message)

        if message == "Pong":
            if active_host_screens[self]['num_retries'] < 6:
                active_host_screens[self]['num_retries'] = active_host_screens[self]['num_retries'] + 1

        elif "PlayerName:" in message:
            name = message.replace("Name:", "").replace("%20", "")
            active_host_screens[self]['name'] = name

        elif message == "ValidateGameName:":
            self.write_message("ValidationFailure")
            print_logger.warning("[SENT]: ValidationFailure")

        elif "ValidateGameName:" in message:
            parsed_game_name = message.replace("ValidateGameName:", "").replace("%20", " ")
            self.write_message("Validation" + global_server_state.validate_game_name(parsed_game_name))
            print_logger.warning("[SENT]: Validation" + global_server_state.validate_game_name(parsed_game_name))

        elif "CleanUp" in message:
            player_name = message.replace("CleanUp:", "").replace("%20", " ")
            global_server_state.remove_player(player_name)
            del active_host_screens[self]
            self.write_message("CleanUpSuccessful")
            print_logger.warning("[SENT]: CleanUpSuccessful")

        elif "SetupGame" in message:
            message = message.replace("SetupGame:", "").replace("%20", " ").split(":")
            game_name = message[0]
            game_mode = message[1]
            player_name = message[2]
            global_server_state.add_game(game_name, game_mode)
            global_server_state.add_to_game(player_name, game_name)
            game_object = global_server_state.get_game(game_name)
            game_object.host = global_server_state.get_player(player_name)
            del active_host_screens[self]

            self.write_message("SetupSuccessful")
            print_logger.warning("[SENT]: SetupSuccessful")

        else:
            self.write_message("Programmer Oops")
            print_logger.warning("[SENT]: Programmer oops")

    def on_close(self):
        pass