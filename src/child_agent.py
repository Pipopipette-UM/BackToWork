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
        self.beliefs = {
            "hungry": False,
            "at_base": True,
            "toybox_pos": None
        }


    def brf(self, environment,dt):
        """
        Belief Revision Function: met à jour les croyances en fonction de l'environnement.
        """
        # On met à jour les croyances de l'agent en fonction de l'environnement
        self.beliefs["toybox_pos"] = environment["toybox_pos"]
        tile_x, tile_y = TileUtils.position_to_tile(self.character.x, self.character.y)
        base_tile_x, base_tile_y = TileUtils.position_to_tile(self.base_position[0], self.base_position[1])
        self.beliefs["at_base"] = tile_x == base_tile_x and tile_y == base_tile_y

        if self.beliefs["at_base"]:
            self.hungry_timer -= dt
            if self.hungry_timer <= 0:
                self.beliefs["hungry"] = True

    def deliberate(self):
        """
        Décide de l'action à effectuer en fonction des croyances.
        """
        if self.beliefs["hungry"]:
            self.state = State.HUNGRY
        elif self.beliefs["at_base"]:
            self.state = State.IDLE
        else:
            self.state = State.RUNNING_BACK

    def plan(self):
        """
        Planifie l'action à effectuer en fonction de l'état actuel.
        """
        if self.state == State.HUNGRY:
            if not self.path:
                (self.grid, self.path) = Dijkstra.find_path((self.character.x, self.character.y), self.beliefs["toybox_pos"],
                                                            self.character.path_layer)
        elif self.state == State.IDLE:
            self.path = []
            self.grid = []
        elif self.state == State.RUNNING_BACK:
            if not self.path:
                (self.grid, self.path) = Dijkstra.find_path((self.character.x, self.character.y), self.base_position,
                                                            self.character.path_layer)

    def execute(self):
        """
        Exécute le plan actuel.
        """
        if self.state == State.HUNGRY:
            self.search_candy()
        elif self.state == State.IDLE:
            self.back_to_spawn()
        elif self.state == State.RUNNING_BACK:
            self.back_to_spawn()

    def update(self, environment, dt):
        self.brf(environment, dt)
        self.deliberate()
        self.plan()
        self.execute()
        self.character.animate()

    def teacher_caught_you(self):
        self.state = State.RUNNING_BACK
        self.beliefs["hungry"] = False
        self.hungry_timer = random.randint(MIN_HUNGRY_TIMER, MAX_HUNGRY_TIMER)
        self.path = []
        self.grid = []
        self.character.play_unique_animation_by_name("hurt")

    def play_with_toy(self):
        self.score += 1
        self.beliefs["hungry"] = False
        self.hungry_timer = random.randint(MIN_HUNGRY_TIMER, MAX_HUNGRY_TIMER)
        self.state = State.RUNNING_BACK

    def search_candy(self):
        # Parfois le coffre est vide, donc on fait attendre le joueur.
        if len(self.path) == 0:
            self.character.action = "idle"
            self.character.direction = "up"
            self.character.animate()
            return

        next_pos = self.path[0]
        if TileUtils.position_to_tile(self.character.x, self.character.y) == next_pos:
            self.path.pop(0)

        next_pos = TileUtils.tile_to_position(next_pos[0], next_pos[1])
        self.move_to_position(next_pos[0], next_pos[1])

    def back_to_spawn(self):
        # Si le joueur est arrivé à sa position de base, on le met en mode IDLE (lecture).
        if len(self.path) == 0:
            self.character.direction = "down"
            self.character.action = "read"
            self.state = State.IDLE
            return

        # On récupère la prochaine position à atteindre et on la retire de la liste des positions à parcourir.
        next_pos = self.path[0]
        if TileUtils.position_to_tile(self.character.x, self.character.y) == next_pos:
            self.path.pop(0)

        next_pos = TileUtils.tile_to_position(next_pos[0], next_pos[1])
        self.move_to_position(next_pos[0], next_pos[1])