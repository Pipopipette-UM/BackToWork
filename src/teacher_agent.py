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
        if self.target is None or self.target.state != State.HUNGRY:
            for i in range(len(environment["child"])):
                if environment["child"][i].state == State.HUNGRY:
                    self.target = environment["child"][i]

            if self.target is None or self.target.state != State.HUNGRY:
                if (self.path == []):
                    (self.grid, self.path) = Dijkstra.find_path((self.player.x, self.player.y), (
                    self.base_position[0], self.base_position[1]), self.player.path_layer)
                self.backToSpawn()
        else:
            self.searchChild()

        tile_x,tile_y = TileUtils.position_to_tile(self.player.x, self.player.y)
        base_tile_x, base_tile_y = TileUtils.position_to_tile(self.base_position[0], self.base_position[1])

        if tile_x == base_tile_x and tile_y == base_tile_y:
            self.player.move("idle")
        self.player.animate()

    def child_caught(self):
        self.score += 1
        self.path = []
        self.grid = []
        self.player.play_unique_animation_by_name("catch")
        self.target = None

    def backToSpawn(self):
        if len(self.path) == 0:
            return
        next_pos = self.path[0]

        if TileUtils.position_to_tile(self.player.x, self.player.y) == next_pos:
            self.path.pop(0)

        next_pos = TileUtils.tile_to_position(next_pos[0], next_pos[1])

        self.moveToPosition(next_pos[0], next_pos[1])

    def searchChild(self):
        child_x, child_y = self.target.player.x, self.target.player.y

        self.grid, self.path = Dijkstra.find_path((self.player.x, self.player.y), (child_x, child_y), self.player.path_layer)
        
        if len(self.path) <= 1:
            return
        
        next_pos = self.path[1]
        next_pos = TileUtils.tile_to_position(next_pos[0], next_pos[1])
        
        selfpos = TileUtils.position_to_tile(self.player.x, self.player.y)

        self.moveToPosition(next_pos[0], next_pos[1])