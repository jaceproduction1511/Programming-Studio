# --------------------------------------------------------------------------- #
# Lair Crushers 2: The Wumpus Strikes Back                                    #
# Developers:                                                                 #
#     - Aaron Ayrault                                                         #
#     - Andrew Kirfman                                                        #
#     - Cheng Chen                                                            #
#     - Cuong Do                                                              #
#                                                                             #
# File: ./static/python/static_handlers.py                                    #
# --------------------------------------------------------------------------- #


# Program Imports
import tornado.web
import os


# General File Handler
class ProgramFileHandler(tornado.web.StaticFileHandler):
    def initialize(self, path):
        self.dirname, self.filename = os.path.split(path)
        super(ProgramFileHandler, self).initialize(self.dirname)

    def get(self, path=None, include_body=True):
        program_file = str(self.dirname) + '/' + str(self.filename) + '/' + str(path)
        super(ProgramFileHandler, self).get(program_file, include_body)


# Get Request Handlers
class MainScreenHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/main_screen.html")


class HostScreenHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/host.html")


class JoinScreenHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/join.html")


class HelpHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/help.html")


class CharacterSelectionHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/character_selection.html")


class DifficultySelectionHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/difficulty_selection.html")


class EasyGameHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/easy_game.html")


class MediumGameHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/medium_game.html")


class HardGameHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/hard_game.html")


class GameOverHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/game_over.html")


class VictoryHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("../html/victory.html")