from agent import Agent, State
import random

class ChildAgent(Agent):

    def __init__(self, x, y, tmx_data, filename):
        Agent.__init__(self, x, y,tmx_data, filename)
        self.hungry_timer = random.randint(3, 10)
        self.candyEat = 0

    def update(self, environment, dt):
        if self.state == State.IDLE:
            self.hungry_timer -= dt
            if self.hungry_timer <= 0:
                print("i am hungry!")
                self.state = State.HUNGRY
                self.hungry_timer = random.randint(5, 20)

        elif self.state == State.HUNGRY:
            self.searchCandy(environment["candy_pos"])
            #if environment["candy_pos"][0] == self.x and environment["candy_pos"][1] == self.y:
            #    print("hmmm nice candy")
            #    self.candyEat+= 1
            #    self.state = State.RUNNING_BACK
            #else:
            #    print("Searching ")

        elif self.state == State.RUNNING_BACK:
            if self.x == self.base_position[0] and self.y == self.base_position[1]:
                print("i m sitting again")
                self.state  = State.IDLE
            else:
                self.backToSpawn()


    def searchCandy(self,candy_pos):
        candy_x, candy_y = candy_pos
        self.moveToPosition(candy_x, candy_y)

    def backToSpawn(self):
        self.moveToPosition(self.base_position[0], self.base_position[1], grid_size)

    def teacherCaughtYou(self):
        self.state = State.RUNNING_BACK

    def eat(self):
        print(" is eating.")
        self.state = State.IDLE
