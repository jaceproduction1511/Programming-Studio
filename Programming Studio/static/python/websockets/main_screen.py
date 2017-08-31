# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ../python/websockets/main_screen.py                                   #
# --------------------------------------------------------------------------- #


# Program Imports
import tornado.websocket
import logging
import __builtin__


# Import logger function
print_logger = logging.getLogger('game_console_log')


class MainWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True

    def open(self, _):
        pass

    @tornado.web.asynchronous
    def on_message(self, message):
        """
        This function validate the name user input and test if it already existed.
        """

        print_logger.warning("[RECEIVED]: " + message)

        if "ValidateName" in message:
            validate_name(self, message)

    def on_close(self):
        pass


def validate_name(websocket_object, message):
    """
    Validates the client's requested name against those which already exist in the
    program database.
    """

    if message == "ValidateName:":
        websocket_object.write_message("Failure")
        print_logger.warning("[SENT]: Failure")

    elif "ValidateName:" in message:
        parsed_name = message.replace("ValidateName:", "").replace("%20", " ")
        result = global_server_state.validate_name(parsed_name)
        websocket_object.write_message(result)
        print_logger.warning("[SENT]: " + result)
        if result == "Success":
            global_server_state.add_player(parsed_name)