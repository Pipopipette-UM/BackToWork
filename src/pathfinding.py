import numpy as np

import constants


class TileUtils:
    @staticmethod
    def position_to_tile(x, y):
        return x // constants.TILE_SIZE, y // constants.TILE_SIZE
    
    @staticmethod
    def tile_to_position(x, y):
        return x * constants.TILE_SIZE, y * constants.TILE_SIZE
    
    @staticmethod
    def distance(start, end):
        x1, y1 = start
        x2, y2 = end
        return abs(x1 - x2) + abs(y1 - y2)
    
    @staticmethod
    def valid_node(node, size_of_grid):
        if node[0] < 0 or node[0] >= size_of_grid:
            return False
        if node[1] < 0 or node[1] >= size_of_grid:
            return False
        return True

    @staticmethod
    def up(node):
        return node[0] - 1,node[1]

    @staticmethod
    def down(node):
        return node[0] + 1,node[1]

    @staticmethod
    def left(node):
        return node[0], node[1] - 1

    @staticmethod
    def right(node):
        return node[0], node[1] + 1
    
    @staticmethod
    def get_neighbours(grid, x, y):
        neighbours = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if 0 <= x + i < len(grid) and 0 <= y + j < len(grid[0]):
                    neighbours.append((x + i, y + j))
        return neighbours
    
    
    
    @staticmethod
    def find_next_pos(start, grid):
        x, y = start
        current_tile = Dijkstra.position_to_tile(x, y)
        neighbours = Dijkstra.get_neighbours(grid, current_tile[0], current_tile[1])
        neighbours = [(x, y) for x, y in neighbours if grid[y][x][0] != -1]
        neighbours.sort(key=lambda pos: grid[pos[1]][pos[0]][0])
        return Dijkstra.tile_to_position(*neighbours[0])


#https://lunalux.io/dijkstras-algorithm-for-grids-in-python/
class Dijkstra:

    @staticmethod
    def notused(start, end, path_layer):
        #print(type(grid))
        
        data = path_layer.iter_data()
        
        # {dist to end, is_a_wall}
        
        grid = [26 * [0] for i in range(27)]
        
        end_tile = Dijkstra.position_to_tile(*end)
        start_tile = Dijkstra.position_to_tile(*start)

        for (x,y,gid) in data:
            
            p_dist = Dijkstra.distance((x, y), start_tile)
            e_dist = Dijkstra.distance((x, y), end_tile)
            
            w1 = 0.2
            w2 = 0.8
            weight = w1 * p_dist + w2 * e_dist
            
            grid[x][y] = [int(weight), 1] if gid > 0 else [-1, 0]
        

        return grid

    def backtrack(initial_node, desired_node, distances):
        # idea start at the last node then choose the least number of steps to go back
        # last node
        path = [desired_node]

        size_of_grid = distances.shape[0]

        while True:
            # check up down left right - choose the direction that has the least distance
            potential_distances = []
            potential_nodes = []

            directions = [TileUtils.up,TileUtils.down,TileUtils.left,TileUtils.right]

            for direction in directions:
                node = direction(path[-1])
                if TileUtils.valid_node(node, size_of_grid):
                    potential_nodes.append(node)
                    potential_distances.append(distances[node[0],node[1]])

            least_distance_index = np.argmin(potential_distances)
            path.append(potential_nodes[least_distance_index])

            if path[-1][0] == initial_node[0] and path[-1][1] == initial_node[1]:
                break

        return list(reversed(path))

    def dijkstra(initial_node, desired_node, obstacles):
        """Dijkstras algorithm for finding the shortest path between two nodes in a graph.

        Args:
            initial_node (list): [row,col] coordinates of the initial node
            desired_node (list): [row,col] coordinates of the desired node
            obstacles (array 2d): 2d numpy array that contains any obstacles as 1s and free space as 0s

        Returns:
            list[list]: list of list of nodes that form the shortest path
        """
        # initialize cost heuristic map
        obstacles = obstacles.copy()
        # obstacles should have very high cost, so we avoid them.
        obstacles *= 1000
        # normal tiles should have 1 cost (1 so we can backtrack)
        obstacles += np.ones(obstacles.shape)
        
        #print(obstacles)
        # source and destination are free
        obstacles[initial_node[0],initial_node[1]] = 0
        obstacles[desired_node[0],desired_node[1]] = 0


        # initialize maps for distances and visited nodes
        size_of_floor = obstacles.shape[0]

        # we only want to visit nodes once
        visited = np.zeros([size_of_floor,size_of_floor],bool)

        # initiate matrix to keep track of distance to source node
        # initial distance to nodes is infinity so we always get a lower actual distance
        distances = np.ones([size_of_floor,size_of_floor]) * np.inf
        # initial node has a distance of 0 to itself
        distances[initial_node[0],initial_node[1]] = 0

        # start algorithm
        current_node = [initial_node[0], initial_node[1]]
        while True:
            directions = [TileUtils.up, TileUtils.down, TileUtils.left, TileUtils.right]
            for direction in directions:
                potential_node = direction(current_node)
                if TileUtils.valid_node(potential_node, size_of_floor): # boundary checking
                    if not visited[potential_node[0],potential_node[1]]: # check if we have visited this node before
                        # update distance to node
                        distance = distances[current_node[0], current_node[1]] + obstacles[potential_node[0],potential_node[1]]

                        # update distance if it is the shortest discovered
                        if distance < distances[potential_node[0],potential_node[1]]:
                            distances[potential_node[0],potential_node[1]] = distance


            # mark current node as visited
            visited[current_node[0]  ,current_node[1]] = True

            # select next node
            # by choosing the the shortest path so far
            t=distances.copy()
            # we don't want to visit nodes that have already been visited
            t[np.where(visited)]=np.inf
            # choose the shortest path
            node_index = np.argmin(t)

            # convert index to row,col.
            node_row = node_index//size_of_floor
            node_col = node_index%size_of_floor
            # update current node.
            current_node = (node_row, node_col)

            # stop if we have reached the desired node
            if current_node[0] == desired_node[0] and current_node[1]==desired_node[1]:
                break

        # backtrack to construct path
        return Dijkstra.backtrack(initial_node,desired_node,distances)
        
        
    
    def find_path(start, end, path_layer):
        #print("starting Dijkstra pathfinding")
        #print(f"Start position: {start}, End position: {end}")

        
        start_tile = TileUtils.position_to_tile(*start)
        end_tile = TileUtils.position_to_tile(*end)
        #print(f"Start tile: {start_tile}, End tile: {end_tile}")

        obstacles = [27 * [0] for i in range(26)]
        
        data = path_layer.iter_data()
        for (x, y, gid) in data:
            obstacles[x][y] = 0.0 if gid > 0 else 1.0

        display_grid = [row[:] for row in obstacles]

        if start_tile == end_tile:
            return (display_grid,[])

        if obstacles[start_tile[0]][start_tile[1]] == 1 or obstacles[end_tile[0]][end_tile[1]] == 1:
            print("TRYING TO PATH TO OR FROM A WALL")
            return (display_grid, [])
            
        path = Dijkstra.dijkstra(start_tile, end_tile, np.array(obstacles))

        for position in path:
            x, y = position
            display_grid[x][y] = -1
        
        return (display_grid,path)
        

    
    


#https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

class AStar:
    

    @staticmethod
    def astar(maze, start, end):
        """Returns a list of tuples as a path from the given start to the given end in the given maze"""

        # Create start and end node
        start_node = Node(None, start)
        start_node.g = start_node.h = start_node.f = 0
        end_node = Node(None, end)
        end_node.g = end_node.h = end_node.f = 0

        # Initialize both open and closed list
        open_list = []
        closed_list = []

        # Add the start node
        open_list.append(start_node)

        loop_count = 0

        # Loop until you find the end
        while len(open_list) > 0:
            loop_count += 1
            if loop_count > 5000:
                print('AStar infinite loop')
                return []

            # Get the current node
            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            # Pop current off open list, add to closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            # Found the goal
            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1] # Return reversed path

            # Generate children
            children = []
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

                # Get node position
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

                # Make sure within range
                if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                    continue

                # Make sure walkable terrain
                if maze[node_position[0]][node_position[1]] != 0:
                    continue

                # Create new node
                new_node = Node(current_node, node_position)

                # Append
                children.append(new_node)

            # Loop through children
            for child in children:

                # Child is on the closed list
                for closed_child in closed_list:
                    if child == closed_child:
                        continue

                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
                child.f = child.g + child.h

                # Child is already in the open list
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue

                # Add the child to the open list
                open_list.append(child)


    @staticmethod
    def find_path(start, end, path_layer):
        #print("starting A Star pathfinding")
        #print(f"Start position: {start}, End position: {end}")

        start_tile = TileUtils.position_to_tile(*start)
        end_tile = TileUtils.position_to_tile(*end)
        #print(f"Start tile: {start_tile}, End tile: {end_tile}")

        obstacles = [27 * [0] for i in range(26)]

        

        data = path_layer.iter_data()
        for (x, y, gid) in data:
            obstacles[x][y] = 0 if gid > 0 else 1

        if start_tile == end_tile:
            return (obstacles, [])


        display_grid = [row[:] for row in obstacles]
        display_grid[start_tile[0]][start_tile[1]] = 'S'
        display_grid[end_tile[0]][end_tile[1]] = 'E'

        print("Grid with start (S) and end (E) tiles highlighted:")
        for row in zip(*display_grid):
            print(' '.join(f"{round(cell):d}" if isinstance(cell, (int, float)) else f"{cell}" for cell in row))




        if obstacles[start_tile[0]][start_tile[1]] == 1 or obstacles[end_tile[0]][end_tile[1]] == 1:
            print("TRYING TO PATH TO OR FROM A WALL")
            return (obstacles, [])

        print("Computing path using A*...")
        path = AStar.astar(obstacles, start_tile, end_tile)
        print(f"Computed path: {path}")

        return (obstacles, path)




