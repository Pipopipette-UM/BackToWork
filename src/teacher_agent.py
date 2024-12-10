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
                self.backToSpawn()
        else:
            self.searchChild()

    def child_caught(self):
        self.score += 1
        self.backToSpawn()
        self.player.play_unique_animation_by_name("catch")

    def backToSpawn(self):
        self.moveToPosition(self.base_position[0], self.base_position[1])

    def searchChild(self):
        child_x, child_y = self.target.player.x, self.target.player.y

        self.grid, self.path = Dijkstra.find_path((self.player.x, self.player.y), (child_x, child_y), self.player.path_layer)
        
        if len(self.path) <= 1:
            return
        
        next_pos = self.path[1]
        next_pos = TileUtils.tile_to_position(next_pos[0], next_pos[1])
        
        selfpos = TileUtils.position_to_tile(self.player.x, self.player.y)

        self.moveToPosition(next_pos[0], next_pos[1])