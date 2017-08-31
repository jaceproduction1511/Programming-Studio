

# Program Imports
import tornado.websocket
import logging
import copy
import __builtin__
from threading import Timer


# Import logger function
print_logger = logging.getLogger('game_console_log')


# Global list of all active host objects.
active_easy_game_screens = {}
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

    for connection in active_easy_game_screens.keys():
        if active_easy_game_screens[connection]['num_retries'] == 0:
            player_name = active_easy_game_screens[connection]['name']
            player_object = global_server_state.get_player(player_name)

            try:
                game_object = None
                for game in global_server_state.games:
                    if player_object in game.players:
                        game_object = game
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
            active_easy_game_screens[connection]['num_retries'] = active_easy_game_screens[connection]['num_retries'] - 1
            try:
                connection.write_message("Ping")
            except Exception:
                print_logger.debug("[DEBUG]: Ping to %s host websocket failed" % str(active_easy_game_screens[connection]))

    for dead_connection in connections_to_remove:
        del active_easy_game_screens[dead_connection]

    if len(active_easy_game_screens) > 0:
        heartbeat_timer.cancel()
        heartbeat_timer = Timer(1, issue_heartbeat)
        heartbeat_timer.start()
    else:
        heartbeat_timer.cancel()



class EasyWebSocketHandler(tornado.websocket.WebSocketHandler):
    def broadcast(self, game_in, message_in):
        for player in game_in.players:
            player.web_socket.write_message("Notification:" + str(message_in))
            print_logger.warning("[SENT]: to " + player.name +": Notification:" + str(message_in))

    def check_origin(self, origin):
        return True

    def open(self, what):
        global heartbeat_timer

        if len(active_easy_game_screens) == 0:
            heartbeat_timer = Timer(1, issue_heartbeat)
            heartbeat_timer.start()

        active_easy_game_screens.update({self : {'name' : "", 'num_retries' : 5}})

    @tornado.web.asynchronous
    def on_message(self, message):
        print_logger.debug("[RECIEVED]: " + message)

        if message == "Pong":
            active_easy_game_screens[self]['num_retries'] = active_easy_game_screens[self]['num_retries'] + 1

        elif "NewMessage:" in message:
            new_message(self, message);

        elif "GameStart:" in message:
            game_start(self, message)

        elif "GetOtherPlayer:" in message:
            coop(self,message)

        elif "Validate:" in message:
            validate_move(self, message)

        elif "GetGameMode:" in message:
            print "Mode1"
            get_game_mode(self, message)

        elif "PickUp:" in message:
            pickup_objects(self, message)

        elif "GetPerceptions:" in message:
            get_perceptions(self, message)

        elif "GetArrowsCount:" in message:
            get_count(self, 'arrows', message)

        elif "GetLivesCount:" in message:
            get_count(self, 'lives', message)

        elif "GetAbilityCount:" in message:
            get_count(self, 'ability', message)

        elif "FireArrow:" in message:
            fire_arrow(self, message)

        elif "CheckVictory" in message:
            check_victory(self, message)

        elif "PlayerName:" in message:
            active_easy_game_screens[self]['name'] = message.replace("PlayerName:", "").replace("%20", " ")

        elif "Scouting:" in message:
            Scouting(self, message)

        else:
            # Add more message handlers here as required
            pass

    def on_close(self):
        pass

def get_game_mode(self, message):
    print "Mode2"
    message = message.replace("GetGameMode:", "")
    player_object = global_server_state.get_player(message)
    print "Mode3"
    game_object = None
    for game in global_server_state.games:
        if player_object in game.players:
            game_object = game
    print "Mode4 " + str(game_object.mode)
    player_object.web_socket.write_message("GameMode:" + game_object.mode)


def coop(websocket_object, message):
    message = message.replace("GetOtherPlayer:", "").replace("%20", " ")
    player_object = global_server_state.get_player(message)
    game_object = None
    for game in global_server_state.games:
        if player_object in game.players:
            game_object = game
    other_player_object = game_object.get_other_player(player_object)
    player_object.web_socket.write_message("OtherPlayer:" + str(other_player_object.name)\
        + ':' + str(other_player_object.x) + ':' + str(other_player_object.y))

def new_message(websocket_object, message):
    """
    Facilitates message passing between two clients.

    Input Arguments:
        - websocket_object: An instance of the players websocket
        - message: The full string message sent by the player

    Error Checking:
        - None
    """

    message = message.replace("NewMessage:", "").replace("%20", " ").split(':')
    player_name = message[0]
    message_to_send = message[1]


    player_dict = {}
    for game in global_server_state.games:
        for player in game.players:
            if player_name == player.name:
                player_dict = {x.name : x for x in copy.copy(game.players) }


    del player_dict[player_name]

    other_player = global_server_state.get_player(player_dict[player_dict.keys()[0]].name)

    other_player.web_socket.write_message("Message:" + player_name + ':' + message_to_send)




def game_start(websocket_object, message):
    """
    Function to respond to the "GameStart" message from the client.
    The game doesn't officially start until two players join the game.
    Consequently, the server (this function) doesn't send the starting
    message to the client until both clients connect to play the same
    game.

    Input Arguments:
        - websocket_object: An instance of the players websocket
        - message: The full string message sent by the player

    Error Checking:
        - None
    """

    player_name = message.replace("GameStart:", "").replace("%20", "")
    player_object = global_server_state.get_player(player_name)
    game_object = None

    player_object.web_socket = websocket_object;
    for game in global_server_state.games:
        if player_object in game.players:
            game_object = game

    if player_object not in game_object.players:
        game_object.append(player_object)

    if len(game_object.players) > 1:
        game_object.start_game()

        # Broadcast join messages to players
        temp_player_list = list(game_object.players)
        for player in game_object.players:
            temp_player_list.remove(player)
            for other_player in temp_player_list:
                player.web_socket.write_message("Joined:" + other_player.name)
                print_logger.warning("[SENT]: to " + player.name + ": Joined:" + other_player.name)
            temp_player_list = list(game_object.players)
            

        for player in game_object.players:
            start_loc = str(player.x) + "," + str(player.y)
            start_loc_2 = str(game_object.get_other_player(player_object).x) + "," + str(game_object.get_other_player(player_object).y)

            #Class
            Class = player.player_class
            player.web_socket.write_message("Class:" + Class)
            print_logger.warning("[SENT]: to " + player.name +": Class:" + Class)

            # InitialLocation:<x-coordinate>,<y-coordinate>
            player.web_socket.write_message("InitialLocation:"+start_loc)
            print_logger.warning("[SENT]: to " + player.name + ": InitialLocation:" + start_loc)

            #game_object.get_other_player(player_object).web_socket.write_message("CoopInitialLocation:"+start_loc)
            # Perceptions
            Perceptions = game_object.get_percepts(player)
            player.web_socket.write_message("Percepts:" + Perceptions)
            print_logger.warning("[SENT]: to " + player.name +": Percepts:" + Perceptions)
        
        player_object.web_socket.write_message("GameMode:" + game_object.mode)
        game_object.get_other_player(player_object).web_socket.write_message("GameMode:" + game_object.mode)
        
        player_object.web_socket.write_message("ForceShowOtherPlayer:" + game_object.get_other_player(player_object).name)
        game_object.get_other_player(player_object).web_socket.write_message("ForceShowOtherPlayer:" + player_object.name)

    else:
        game_object.ready_to_join = True


def validate_move(websocket_object, message):
    """
    Determines whether a players chosen move is valid (Makes sure that they
    won't run into a wall or anything).  Also synchronizes committed move choices
    and doesn't actually apply moves until the turn is over.

    Input Arguments:
        - websocket_object: An instance of the players websocket
        - message: The full string message sent by the player

    Error Checking:
        - None
    """

    message = message.replace("Validate:", "").replace("%20", " ").split(":")
    player_name = message[0]
    direction = message[1]
    player_object = global_server_state.get_player(player_name)
    game_object = None

    for game in global_server_state.games:
        if player_object in game.players:
            game_object = game

    if game_object.is_valid_move(player_object, direction):
        websocket_object.write_message("Valid")
        print_logger.info("[SENT]: Valid")

        game_object.committed_moves[str(player_name)] = str(direction)
        if len(game_object.committed_moves) == len(game_object.players):
            for player in game_object.players:

                result = game_object.move_player(player, game_object.committed_moves[str(player.name)])
                player.web_socket.write_message("ApplyMove")
                print_logger.info("[SENT]: to " + player.name +": ApplyMove")

                if result != "" and result is not None:
                    player.web_socket.write_message("Died:" + str(result))

            game_object.committed_moves = {}

            #ask me if this goes bad - The Blonde
            #random events (including wumpus movement)
            #will return a string in the following format:
            #"life_potion_added(newx,newy):ability_potion_added(newx,newy):wumpus_moved(oldx,oldy)(newx,newy):wumpus_moved(oldx,oldy)(newx,newy):"
            event_result = game_object.random_event_check()

    else:
        websocket_object.write_message("InvalidMove")
        print_logger.warning("[SENT]: InvalidMove")


def pickup_objects(websocket_object, message):
    """
    Called when the user clicks on the "Pick Up" button in the browser window.
    Will pick up any objects that are in the same square that the user resides.
    If no objects occupy that square, then this function effectively does nothing.

    Input Arguments:
        - websocket_object: An instance of the players websocket
        - message: The full string message sent by the player

    Error Checking:
        - None
    """

    player_name = message.replace("%20", " ").replace("PickUp:", "")
    player_object = global_server_state.get_player(player_name)
    game_object = None

    for game in global_server_state.games:
        if player_object in game.players:
            game_object = game

    player2_object = game_object.get_other_player(player_object)
    result = game_object.is_valid_pick_up(player_object)



    if result is True:
        result = game_object.get_percepts(player_object)
        picked_up = game_object.pick_up(player_object)



        websocket_object.write_message("PickedUp:" + player_object.name)
        print_logger.warning("[SENT]: PickedUp:" + player_object.name)

        player_object.web_socket.write_message("RemoveElements:" + result)
        player2_object.web_socket.write_message("RemoveElements:" + result)
        print_logger.warning("[SENT]: RemoveElements:" + result)

    else:

        websocket_object.write_message("InvalidPickUp")
        print_logger.warning("[SENT]: InvalidPickUp")


def get_perceptions(websocket_object, message):
    """
    Given a user and a position, returns the percepts that the user is
    experiencing.

    Input Arguments:
        - websocket_object: An instance of the players websocket
        - message: The full string message sent by the player

    Error Checking:
        - None
    """

    print "Flag1: " + str(message)
    player_name = message.replace("%20", " ").replace("GetPerceptions:", "")
    print "Flag2: " + str()
    player_object = global_server_state.get_player(player_name)
    game_object = None

    for game in global_server_state.games:
        if player_object in game.players:
            game_object = game

    result = game_object.get_percepts(player_object)

    websocket_object.write_message("SetPerceptions:" + result)
    print_logger.warning("[SENT]: SetPerceptions:" + result)

def get_count(websocket_object, thing, message):
    """
    The client may request to be updated on the current
    count of modifiable resources (lives, arrows, etc...).  This
    function facilitates this by fetching current counts and
    returning them to the client.

    Input Arguments:
        - websocket_object: An instance of the players websocket
        - thing: The item to get the count of.  Currently only
          'arrows' and 'lives' are supported.
        - message: The full string message sent by the player

    Error Checking:
        - None
    """

    if thing == "arrows":
        player_name = message.replace("%20", " ").replace("GetArrowsCount:", "")
        player_object = global_server_state.get_player(player_name)

        websocket_object.write_message("ArrowsCount:" + str(player_object.arrow))
        print_logger.warning("[SENT]: " + str(player_object.arrow))
    elif thing == "lives":
        player_name = message.replace("%20", " ").replace("GetLivesCount:", "")
        player_object = global_server_state.get_player(player_name)

        websocket_object.write_message("LivesCount:" + str(player_object.life))
        print_logger.warning("[SENT]: " + str(player_object.life))
    elif thing == "ability":
        player_name = message.replace("%20", " ").replace("GetAbilityCount:", "")
        player_object = global_server_state.get_player(player_name)

        websocket_object.write_message("AbilityCount:" + str(player_object.ability_uses))
        print_logger.warning("[SENT]: " + str(player_object.ability_uses))
    else:
        # Add more count messages as needed
        pass


def fire_arrow(websocket_object, message):
    """
    A given player fires an arrow by clicking on one of the arrows in the browser.
    This function determines the result of that arrow and returns it to the user.

    Input Arguments:
        - websocket_object: An instance of the players websocket
        - message: The full string message sent by the player

    Error Checking:
        - None
    """

    split_strings = message.replace("%20", " ").replace("FireArrow:", "").split(":")
    player_object = global_server_state.get_player(split_strings[0])
    game_object = None

    for game in global_server_state.games:
        if player_object in game.players:
            game_object = game

    player2_object = game_object.get_other_player(player_object)
    result = game_object.fire_arrow(player_object, split_strings[1])

    #result will literally be the message to return to the output box
    if result == "player killed":
        kill_message = game_object.kill(player2_object, "arrow")
        player_object.web_socket.write_message('Notification:red:You hear the scream of your dying opponent.')
        print_logger.warning("[SENT]: You hear the scream of your dying opponent.")
    elif "WumpusDead:" in result:
        websocket_object.broadcast(game_object, "red:You hear the Blood Curdling scream of a dying Wumpus.")
        print_logger.warning("[SENT]: You hear the Blood Curdling scream of a dying Wumpus.")
        player_object.web_socket.write_message(result)
        player2_object.web_socket.write_message(result)
    else:
        websocket_object.write_message("Notification:" + str(result))
        print_logger.warning("[SENT]: " + str(result))


def check_victory(websocket_object, message):
    """
    Check to see if a player has won the game.

    Input Arguments:
        - websocket_object: An instance of the players websocket
        - message: The full string message sent by the player

    Error Checking:
        - None
    """

    player_name = message.replace("%20", " ").replace("CheckVictory:", "")
    player_object = global_server_state.get_player(player_name)

    game_object = None

    for game in global_server_state.games:
        if player_object in game.players:
            game_object = game

    player2_object = game_object.get_other_player(player_object)
    if game_object.Check_Victory(player_object):
        player_object.web_socket.write_message("Victory")
        if game_object.mode == "collaborative":
            player2_object.web_socket.write_message("Victory")
        elif game_object.mode == "pvp":
            player2_object.web_socket.write_message("Died:Dead")
    
    if websocket_object in active_easy_game_screens.keys():
        del active_easy_game_screens[websocket_object]

def Scouting(self, message):
    message = message.replace("%20", " ").replace("Scouting:", "").split(',')
    player = global_server_state.get_player(message[0]);
    Scx = int(message[1])
    Scy = int(message[2])
    game_object = None

    for game in global_server_state.games:
        if player in game.players:
            game_object = game
    if(player.ability_uses > 0):
        Perceptions = game_object.Scout(Scx, Scy)
        player.web_socket.write_message("SetPerceptions:" + Perceptions)
        if (game_object.mode == "collaborative"):
            player2 = game_object.get_other_player(player)
            player2.web_socket.write_message("SetPerceptions:" + Perceptions)
        print_logger.warning("[SENT]: to " + player.name +": SetPerceptions:" + Perceptions)
        player.ability_uses = player.ability_uses-1
        player.web_socket.write_message("AbilityCount:" + str(player.ability_uses))
    else:
        player.web_socket.write_message('Notification:yellow:You are out of ability uses.')