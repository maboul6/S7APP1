from Instructions import *


class Controller:
    def __init__(self, app=None):
        self.app = app

    def get_instruction(self, keys=None, events=None):
        return Action.DOWN
