from agent import Agent, State

class TeacherAgent(Agent):

    def __init__(self,x,y,tmx_data, filename):
        super().__init__(x,y,tmx_data, filename)
        self.target = None

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
        self.moveToPosition(child_x, child_y)