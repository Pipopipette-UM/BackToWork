from agent import Agent, State
from pathfinding import TileUtils
from pathfinding import AStar
from pathfinding import Dijkstra

class TeacherAgent(Agent):

    def __init__(self,x,y,tmx_data, filename):
        super().__init__(x,y,tmx_data, filename)
        self.target = None
        self.grid = []
        self.path = []

    def update(self, environment,dt):
        # Si le professeur n'a pas de cible ou que la cible n'est plus affamée, on en cherche une nouvelle.
        if self.target is None or self.target.state != State.HUNGRY:
            for child in environment["children"]:
                if child.state == State.HUNGRY:
                    self.target = child

            # Si aucune cible n'a été trouvée, on retourne à la position de départ.
            if self.target is None or self.target.state != State.HUNGRY:
                if self.path == []:
                    (self.grid, self.path) = Dijkstra.find_path((self.player.x, self.player.y), (
                    self.base_position[0], self.base_position[1]), self.player.path_layer)
                self.back_to_spawn()
        else:
            self.search_child()

        tile_x,tile_y = TileUtils.position_to_tile(self.player.x, self.player.y)
        base_tile_x, base_tile_y = TileUtils.position_to_tile(self.base_position[0], self.base_position[1])

        if tile_x == base_tile_x and tile_y == base_tile_y:
            self.player.move("idle")
        environment["teacher"] = (self.player.x, self.player.y)

    def child_caught(self):
        self.score += 1
        self.path = []
        self.grid = []
        self.player.play_unique_animation_by_name("catch")
        self.target = None

    def back_to_spawn(self):
        if len(self.path) == 0:
            self.player.action = "idle"
            self.player.direction = "down"
            return
        next_pos = self.path[0]

        if TileUtils.position_to_tile(self.player.x, self.player.y) == next_pos:
            self.path.pop(0)

        next_pos = TileUtils.tile_to_position(next_pos[0], next_pos[1])

        self.move_to_position(next_pos[0], next_pos[1])

    def search_child(self):
        child_x, child_y = self.target.player.x, self.target.player.y
        self.grid, self.path = Dijkstra.find_path((self.player.x, self.player.y), (child_x, child_y), self.player.path_layer)

        if len(self.path) <= 1:
            return

        # On récupère la prochaine tuile à atteindre et on la transforme en position.
        next_pos = self.path[1]
        next_pos = TileUtils.tile_to_position(next_pos[0], next_pos[1])

        # On déplace le professeur vers la prochaine position.
        self.move_to_position(next_pos[0], next_pos[1])