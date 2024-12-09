from agent import Agent, State
import random
from pathfinding import Dijkstra
from pathfinding import AStar
from pathfinding import TileUtils

class ChildAgent(Agent):

    def __init__(self, x, y, tmx_data, filename):
        Agent.__init__(self, x, y,tmx_data, filename)
        self.hungry_timer = random.randint(1, 1)
        self.candyEat = 0

        self.grid = []
        self.path = []

    def update(self, environment, dt):
        if self.state == State.IDLE:
            self.hungry_timer -= dt
            if self.hungry_timer <= 0:
                print("i am hungry!")
                self.state = State.HUNGRY
                self.hungry_timer = random.randint(5, 20)

        elif self.state == State.HUNGRY:
            
            if(self.path == []):
                (self.grid,self.path) = Dijkstra.find_path((self.player.x, self.player.y), (environment["toybox_pos"][0], environment["toybox_pos"][1]), self.player.path_layer)
            self.searchCandy(environment["toybox_pos"])

        elif self.state == State.RUNNING_BACK:
            if self.player.x == self.base_position[0] and self.player.y == self.base_position[1]:
                print("i m sitting again")
                self.state  = State.IDLE
            else:
                self.backToSpawn()
                self.player.animate()

            if self.player.x == self.base_position[0] and self.player.y == self.base_position[1]:
                self.player.animate()

    def teacher_caught_you(self):
        self.state = State.RUNNING_BACK

    def play_with_toy(self, toybox):
        self.score += 1
        self.hungry_timer = random.randint(5, 20)
        self.state = State.RUNNING_BACK
        print("playing with toy")


    def searchCandy(self,candy_pos):
        candy_x, candy_y = candy_pos

        if len(self.path) == 0:
            return
        
        next_pos = self.path[0]
        # l'algo ne prend pas en compte les obstacles !!! ????
        if TileUtils.position_to_tile(self.player.x, self.player.y) == next_pos:
            #print("next_pos ", next_pos)
            self.path.pop(0)
        
        #print("next_pos ", next_pos)
        #print("current pos ", PathFinding.position_to_tile(self.player.x, self.player.y))   
        
        next_pos = TileUtils.tile_to_position(next_pos[0], next_pos[1])

        self.moveToPosition(next_pos[0], next_pos[1])

    def backToSpawn(self):
        self.moveToPosition(self.base_position[0], self.base_position[1])

    def teacherCaughtYou(self):
        self.state = State.RUNNING_BACK

    def eat(self):
        print(" is eating.")
        self.state = State.IDLE
