import math


class NavNode:
    def __init__(self, position):
        self.position = position
        self.neighbours = []

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)

    def __str__(self):
        return "[" + str(self.position[0]) + ", " + str(self.position[1]) + "]"

    __repr__ = __str__


class PathFinderNode:
    def __init__(self, nav_node, parent_path_node, fixed_path_cost):
        self.nav_node = nav_node
        self.fixed_path_cost = fixed_path_cost
        self.parent_path_node = parent_path_node

    def __str__(self):
        return str(self.nav_node)

    __repr__ = __str__
        

class PathFinder:
    def __init__(self, start_nav_node, end_nav_node, max_path_search_size=500):
        self.start_path_node = PathFinderNode(start_nav_node, None, 0)
        self.end_nav_node = end_nav_node
        self.max_search_size = max_path_search_size
        self.final_path = []  # as regular nav_nodes we can just pop() off one after the other

        self.open_node_list = []
        self.closed_node_list = []  # nodes we have already evaluated by adding their neighbours to the open list
        self.current_path_node = self.start_path_node

        self.add_current_path_node_neighbours_to_open_list()

        self.search_size = 0
        self.current_fixed_path_cost = 0.0
        while self.current_path_node.nav_node != self.end_nav_node and self.search_size < self.max_search_size:
            lowest_path_cost = self.current_fixed_path_cost + 99999999.0
            lowest_path_cost_node = None
            for path_node in self.open_node_list:
                x_diff = path_node.nav_node.position[0] - self.end_nav_node.position[0]
                y_diff = path_node.nav_node.position[1] - self.end_nav_node.position[1]
                distance_to_end_node = math.sqrt(x_diff**2 + y_diff**2)

                path_cost = path_node.fixed_path_cost + distance_to_end_node

                if path_cost < lowest_path_cost:
                    lowest_path_cost = path_cost
                    lowest_path_cost_node = path_node
                
            self.current_path_node = lowest_path_cost_node
            self.add_current_path_node_neighbours_to_open_list()

            self.search_size += 1

        # unwind our successful path
        if self.search_size <= self.max_search_size:
            while self.current_path_node.parent_path_node is not None:
                self.final_path.append(self.current_path_node.nav_node)
                self.current_path_node = self.current_path_node.parent_path_node

    def add_current_path_node_neighbours_to_open_list(self):
        # add current Node neighbours to open list (if not in closed list?)
        for neighbour in self.current_path_node.nav_node.neighbours:
            if not self.is_nav_node_in_closed_list(neighbour):
                x_diff = self.current_path_node.nav_node.position[0] - neighbour.position[0]
                y_diff = self.current_path_node.nav_node.position[1] - neighbour.position[1]
                distance_to_neighbour = math.sqrt(x_diff**2 + y_diff**2)
                
                fixed_path_cost = self.current_path_node.fixed_path_cost + distance_to_neighbour
                self.open_node_list.append(PathFinderNode(neighbour, self.current_path_node, fixed_path_cost))
                
        self.closed_node_list.append(self.current_path_node)
        if self.current_path_node in self.open_node_list:
            self.open_node_list.remove(self.current_path_node)

    def is_nav_node_in_closed_list(self, nav_node):
        is_in_closed_list = False
        for path_node in self.closed_node_list:
            x_match = path_node.nav_node.position[0] == nav_node.position[0]
            y_match = path_node.nav_node.position[1] == nav_node.position[1]
            if x_match and y_match:
                is_in_closed_list = True
        return is_in_closed_list
