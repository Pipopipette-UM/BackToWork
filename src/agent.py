from enum import Enum

from tensorflow.python.ops.numpy_ops.np_random import random

from player import Player

State = Enum('agentState', [("IDLE", 1), ("HUNGRY", 2), ("RUNNING_BACK", 3), ("LOOKING", 4)])

class Agent:

    def __init__(self, x, y, tmx_data, filename):
        self.player = Player(x,y,tmx_data, filename)
        self.base_position = (x,y)
        self.state = State.IDLE

    def update(self, environment, dt):
        pass

    def moveToPosition(self, x, y):
        dx, dy = 0, 0
        # TODO algo pathfinding
        if self.player.x < x:
            self.player.move("right")
        elif self.player.x > x:
            self.player.move("left")
        elif self.player.y < y:
            self.player.move("down")
        elif self.player.y > y:
            self.player.move("up")