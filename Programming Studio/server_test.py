#!/opt/anaconda/bin/python2.7

import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import sys
import logging
import copy
import __builtin__


sys.path.append('./static/python')
sys.path.append('./static/python/websockets')
from wumpus_world import Wumpus_World
from game import Game
from tornado.options import define, options, parse_command_line

from static_handlers import ProgramFileHandler, MainScreenHandler, HostScreenHandler, JoinScreenHandler,\
    HelpHandler, CharacterSelectionHandler, DifficultySelectionHandler, EasyGameHandler, MediumGameHandler,\
    HardGameHandler, GameOverHandler, VictoryHandler
from main_screen import MainWebSocketHandler
from host import HostWebSocketHandler
from join import JoinWebSocketHandler
from difficulty import DifficultyWebSocketHandler
from character import CharacterWebSocketHandler
from easy_game import EasyWebSocketHandler
from game_over import GameOverWebSocketHandler
from victory import VictoryWebSocketHandler


# Import Command Line Arguments
define("port", default=8888, help="run on the given port", type=int)


#Print logger goes to standard output and a file
if not os.path.exists("./gameplay_log"):
    os.makedirs("./gameplay_log")

print_logger = logging.getLogger('game_console_log')
print_logger.setLevel(logging.WARNING)
print_console_handler = logging.StreamHandler(sys.stdout)
print_file_handler = logging.FileHandler('./gameplay_log/game_output_log.txt')
print_logger.addHandler(print_console_handler)
print_logger.addHandler(print_file_handler)


# Global variables to keep track of game state
__builtin__.global_server_state = Wumpus_World()


# Main Game Handlers & Settings
settings = { }
handlers = [
    (r'/', MainScreenHandler),
    (r'/ws_main(.*)', MainWebSocketHandler),
    (r'/host', HostScreenHandler), 
    (r'/ws_host(.*)', HostWebSocketHandler),
    (r'/join', JoinScreenHandler),
    (r'/ws_join(.*)', JoinWebSocketHandler),
    (r'/help', HelpHandler),
    (r'/character_selection', CharacterSelectionHandler),
    (r'/difficulty_selection', DifficultySelectionHandler),
    (r'/ws_character', CharacterWebSocketHandler),
    (r'/ws_difficulty', DifficultyWebSocketHandler),
    (r'/easy_game', EasyGameHandler),
    (r'/medium_game', MediumGameHandler),
    (r'/hard_game', HardGameHandler),
    (r'/ws_easy(.*)', EasyWebSocketHandler),
    (r'/game_over', GameOverHandler),
    (r'/ws_cleanup(.*)',GameOverWebSocketHandler),
    (r'/victory', VictoryHandler),
    (r'/static/(.*)', ProgramFileHandler, {'path' : './static'})
    ]


app = tornado.web.Application(handlers, **settings)


if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()