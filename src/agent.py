from enum import Enum

from character import Character

State = Enum('agentState', [("IDLE", 1), ("HUNGRY", 2), ("RUNNING_BACK", 3), ("HUNTING", 4)])

class Agent:

    def __init__(self, x, y, tmx_data, filename):
        self.character = Character(x,y,tmx_data, filename)
        self.base_position = (x,y)
        self.state = State.IDLE
        self.score = 0

    def update(self, environment, dt):
        pass

    def move_to_position(self, x, y):
        if self.character.x < x:
            self.character.move("right")
        elif self.character.x > x:
            self.character.move("left")
        elif self.character.y < y:
            self.character.move("down")
        elif self.character.y > y:
            self.character.move("up")