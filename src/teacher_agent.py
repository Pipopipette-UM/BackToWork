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
        self.beliefs = {
            "at_base": True,
            "children": []
        }

    def brf(self, environment, dt):
        # On met à jour les croyances de l'agent en fonction de l'environnement
        tile_x, tile_y = TileUtils.position_to_tile(self.player.x, self.player.y)
        base_tile_x, base_tile_y = TileUtils.position_to_tile(self.base_position[0], self.base_position[1])
        self.beliefs["at_base"] = tile_x == base_tile_x and tile_y == base_tile_y
        self.beliefs["children"] = environment["children"]

    def deliberate(self):
        if self.beliefs["at_base"]:
            self.state = State.IDLE
        else:
            self.state = State.RUNNING_BACK

        for child in self.beliefs["children"]:
            if child.state == State.HUNGRY:
                self.target = child
                self.state = State.HUNTING # Si un enfant a faim, on passe en mode chasse

    def plan(self):
        if self.state == State.HUNTING:
            self.path = []
            (self.grid, self.path) = Dijkstra.find_path((self.player.x, self.player.y), (self.target.player.x, self.target.player.y), self.player.path_layer)
        elif self.state == State.RUNNING_BACK:
            if self.path == []:
                (self.grid, self.path) = Dijkstra.find_path((self.player.x, self.player.y), (self.base_position[0], self.base_position[1]), self.player.path_layer)

    def execute(self):
        if self.state == State.IDLE:
            self.back_to_spawn()
            # Temporary fix
            self.grid = []
            self.path = []
        if self.state == State.HUNTING:
            self.search_child()
        elif self.state == State.RUNNING_BACK:
            self.back_to_spawn()

    def update(self, environment,dt):
        self.brf(environment,dt)
        self.deliberate()
        self.plan()
        self.execute()
        self.player.animate()

    def child_caught(self):
        self.score += 1
        self.path = []
        self.grid = []
        self.player.play_unique_animation_by_name("catch")
        self.target = None
        self.state = State.RUNNING_BACK

    def back_to_spawn(self):
        if len(self.path) == 0:
            self.player.action = "read"
            self.player.direction = "down"
            return

        # Probleme lors du retour du prof a voir
        # Aussi pourquoi quelques fois c'est self.path[0] et d'autres c'est self.path[1]
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