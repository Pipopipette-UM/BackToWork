import random

from agent import Agent, State
from pathfinding import Dijkstra
from pathfinding import TileUtils
from constants import MIN_HUNGRY_TIMER, MAX_HUNGRY_TIMER


class ChildAgent(Agent):

    def __init__(self, x, y, tmx_data, filename):
        Agent.__init__(self, x, y, tmx_data, filename)
        self.hungry_timer = random.randint(0, MIN_HUNGRY_TIMER)
        self.candyEat = 0

        self.grid = []
        self.path = []

    def update(self, environment, dt):
        if self.state == State.IDLE:
            self.hungry_timer -= dt
            if self.hungry_timer <= 0:
                self.state = State.HUNGRY
                self.hungry_timer = random.randint(MIN_HUNGRY_TIMER, MAX_HUNGRY_TIMER)
            self.player.animate()

        elif self.state == State.HUNGRY:
            if not self.path:
                (self.grid, self.path) = Dijkstra.find_path((self.player.x, self.player.y), (
                environment["toybox_pos"][0], environment["toybox_pos"][1]), self.player.path_layer)
            self.search_candy()

        elif self.state == State.RUNNING_BACK:
            if not self.path:
                (self.grid, self.path) = Dijkstra.find_path((self.player.x, self.player.y), (
                self.base_position[0], self.base_position[1]), self.player.path_layer)
            self.back_to_spawn()


    def teacher_caught_you(self):
        self.state = State.RUNNING_BACK
        self.path = []
        self.grid = []
        self.player.play_unique_animation_by_name("hurt")

    def play_with_toy(self):
        self.score += 1
        self.hungry_timer = random.randint(5, 20)
        self.state = State.RUNNING_BACK

    def search_candy(self):
        # Parfois le coffre est vide, donc on fait attendre le joueur.
        if len(self.path) == 0:
            self.player.action = "idle"
            self.player.direction = "up"
            self.player.animate()
            return

        next_pos = self.path[0]
        if TileUtils.position_to_tile(self.player.x, self.player.y) == next_pos:
            self.path.pop(0)

        next_pos = TileUtils.tile_to_position(next_pos[0], next_pos[1])
        self.move_to_position(next_pos[0], next_pos[1])

    def back_to_spawn(self):
        # Si le joueur est arrivé à sa position de base, on le met en mode IDLE (lecture).
        if len(self.path) == 0:
            self.player.direction = "down"
            self.player.action = "read"
            self.state = State.IDLE
            return

        # On récupère la prochaine position à atteindre et on la retire de la liste des positions à parcourir.
        next_pos = self.path[0]
        if TileUtils.position_to_tile(self.player.x, self.player.y) == next_pos:
            self.path.pop(0)

        next_pos = TileUtils.tile_to_position(next_pos[0], next_pos[1])
        self.move_to_position(next_pos[0], next_pos[1])