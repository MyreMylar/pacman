import random

# import numpy
# from numpy.random import random_integers as rand
import pygame

from game.path_finder import NavNode


class PillZone:
    def __init__(self, x_pos, y_pos, large_pill):
        self.grid_x_pos = x_pos
        self.grid_y_pos = y_pos

        self.screen_x_pos = 120 + (self.grid_x_pos * 18)
        self.screen_y_pos = 30 + (self.grid_y_pos * 18)
        self.large_pill = large_pill


class JunctionPoint:
    def __init__(self, x_pos, y_pos):
        self.grid_x_pos = x_pos
        self.grid_y_pos = y_pos

        screen_x_pos = 120 + (self.grid_x_pos * 18)
        screen_y_pos = 30 + (self.grid_y_pos * 18)

        self.nav_node = NavNode([screen_x_pos, screen_y_pos])


class MazeGhostGate:
    def __init__(self, start_index, end_index):
        self.start_index = start_index
        self.end_index = end_index
        self.is_horiz_wall = True
        self.start_pos = (120 + (start_index[1] * 18), 30 + (start_index[0] * 18))
        self.end_pos = (120 + (end_index[1] * 18), 30 + (end_index[0] * 18))
        self.collided = False

        if self.start_pos[0] < self.end_pos[0]:
            left = self.start_pos[0]
            width = self.end_pos[0] - self.start_pos[0]
        else:
            left = self.end_pos[0]
            width = self.start_pos[0] - self.end_pos[0]
            if width == 0:
                width = 4

        if self.start_pos[1] < self.end_pos[1]:
            top = self.start_pos[1]
            height = self.end_pos[1] - self.start_pos[1]
        else:
            top = self.start_pos[1]
            height = self.start_pos[1] - self.end_pos[1]
            if height == 0:
                height = 4
        self.rect = pygame.Rect((left, top), (width, height))


class MazeWall:
    def __init__(self, start_index, end_index):
        self.is_vert_wall = False
        self.is_horiz_wall = False

        if start_index[0] < end_index[0]:
            first_id = start_index[0]
            second_id = end_index[0]
            self.is_vert_wall = True
        else:
            first_id = end_index[0]
            second_id = start_index[0]

        if start_index[1] < end_index[1]:
            third_id = start_index[1]
            fourth_id = end_index[1]
            self.is_horiz_wall = True
        else:
            third_id = end_index[1]
            fourth_id = start_index[1]

        self.id = str(first_id) + str(second_id) + str(third_id) + str(fourth_id)
        self.start_index = start_index
        self.end_index = end_index

        self.start_pos = (120 + (start_index[1] * 18), 30 + (start_index[0] * 18))
        self.end_pos = (120 + (end_index[1] * 18), 30 + (end_index[0] * 18))
        self.collided = False

        if self.start_pos[0] < self.end_pos[0]:
            left = self.start_pos[0]
            width = self.end_pos[0] - self.start_pos[0]
        else:
            left = self.end_pos[0]
            width = self.start_pos[0] - self.end_pos[0]
            if width == 0:
                width = 4

        if self.start_pos[1] < self.end_pos[1]:
            top = self.start_pos[1]
            height = self.end_pos[1] - self.start_pos[1]
        else:
            top = self.start_pos[1]
            height = self.start_pos[1] - self.end_pos[1]
            if height == 0:
                height = 4
        self.rect = pygame.Rect((left, top), (width, height))


def add_new_wall_if_unique(possible_new_wall, maze_walls):
    wall_already_exists = False
    for wall in maze_walls:
        if wall.id == possible_new_wall.id:
            wall_already_exists = True
    if not wall_already_exists:
        maze_walls.append(possible_new_wall)

    return maze_walls


def create_maze(width=11, height=16, complexity=.75, density=.75):
    # Only odd shapes
    shape = ((width // 2) * 2 + 1, (height // 2) * 2 + 1)
    # Adjust complexity and density relative to maze size
    complexity = int(complexity * (5 * (shape[0] + shape[1])))
    density = int(density * ((shape[0] // 2) * (shape[1] // 2)))
    # Build actual maze
    maze_shape = []  # numpy.zeros(shape, dtype=bool)
    for x in range(0, shape[0]):
        column = []
        for y in range(0, shape[1]):
            column.append(0)
        maze_shape.append(column)
    # Fill borders
    for x in range(0, shape[0]):
        maze_shape[x][0] = 1
        maze_shape[x][-1] = 1
    for y in range(0, shape[1]):
        maze_shape[0][y] = 1
        maze_shape[-1][y] = 1

    # Make aisles
    for i in range(density):
        x, y = int(random.randint(0, shape[0] // 2) * 2), int(random.randint(0, shape[1] // 2) * 2)
        maze_shape[x][y] = 1
        for j in range(complexity):
            neighbours = []
            if x > 1:
                neighbours.append((x - 2, y))
            if x < shape[0] - 2:
                neighbours.append((x + 2, y))
            if y > 1:
                neighbours.append((x, y - 2))
            if y < shape[1] - 2:
                neighbours.append((x, y + 2))
            if len(neighbours):
                x_, y_ = neighbours[int(random.randint(0, len(neighbours) - 1))]
                if maze_shape[x_][y_] == 0:
                    maze_shape[x_][y_] = 1
                    maze_shape[x_ + (x - x_) // 2][y_ + (y - y_) // 2] = 1
                    x, y = x_, y_

    # clears dead ends
    for x in range(1, shape[0] - 1):
        for y in range(1, shape[1] - 1):
            if maze_shape[x][y] == 0:
                wall_neighbours = []
                exits = 0
                if maze_shape[x][y + 1] == 0:
                    exits += 1
                elif (y + 1) != shape[0] - 1:
                    wall_neighbours.append((y + 1, x))
                if maze_shape[x + 1][y] == 0:
                    exits += 1
                elif (x + 1) != shape[1] - 1:
                    wall_neighbours.append((y, x + 1))
                if maze_shape[x - 1][y] == 0:
                    exits += 1
                elif (x - 1) != 0:
                    wall_neighbours.append((y, x - 1))
                if maze_shape[x][y - 1] == 0:
                    exits += 1
                elif (y - 1) != 0:
                    wall_neighbours.append((y - 1, x))

                if exits <= 1:
                    y_, x_ = wall_neighbours[int(random.randint(0, len(wall_neighbours) - 1))]
                    maze_shape[x_][y_] = 0

    # change centre of maze to always be ghost cube

    centre_x = int((shape[0] - 1) / 2)
    centre_y = int((shape[1] + 1) / 2)

    # 5 by 3 gap in centre
    maze_shape[centre_x][centre_y] = 0
    maze_shape[centre_x][centre_y + 1] = 0
    maze_shape[centre_x][centre_y - 1] = 0
    maze_shape[centre_x - 1][centre_y] = 0
    maze_shape[centre_x + 1][centre_y] = 0
    maze_shape[centre_x - 1][centre_y + 1] = 0
    maze_shape[centre_x + 1][centre_y + 1] = 0
    maze_shape[centre_x - 1][centre_y - 1] = 0
    maze_shape[centre_x + 1][centre_y - 1] = 0
    maze_shape[centre_x - 2][centre_y] = 0
    maze_shape[centre_x + 2][centre_y] = 0
    maze_shape[centre_x - 2][centre_y + 1] = 0
    maze_shape[centre_x + 2][centre_y + 1] = 0
    maze_shape[centre_x - 2][centre_y - 1] = 0
    maze_shape[centre_x + 2][centre_y - 1] = 0
    # surrounding walls
    maze_shape[centre_x][centre_y + 2] = 1
    maze_shape[centre_x + 1][centre_y + 2] = 1
    maze_shape[centre_x - 1][centre_y + 2] = 1
    maze_shape[centre_x + 2][centre_y + 2] = 1
    maze_shape[centre_x - 2][centre_y + 2] = 1
    maze_shape[centre_x + 3][centre_y + 2] = 1
    maze_shape[centre_x - 3][centre_y + 2] = 1
    maze_shape[centre_x][centre_y - 2] = 0  # doorway
    maze_shape[centre_x + 1][centre_y - 2] = 1
    maze_shape[centre_x - 1][centre_y - 2] = 1
    maze_shape[centre_x + 2][centre_y - 2] = 1
    maze_shape[centre_x - 2][centre_y - 2] = 1
    maze_shape[centre_x + 3][centre_y - 2] = 1
    maze_shape[centre_x - 3][centre_y - 2] = 1
    maze_shape[centre_x + 3][centre_y] = 1
    maze_shape[centre_x + 3][centre_y - 1] = 1
    maze_shape[centre_x + 3][centre_y + 1] = 1
    maze_shape[centre_x - 3][centre_y] = 1
    maze_shape[centre_x - 3][centre_y - 1] = 1
    maze_shape[centre_x - 3][centre_y + 1] = 1

    # corridor around ghost cube
    maze_shape[centre_x][centre_y + 3] = 0
    maze_shape[centre_x + 1][centre_y + 3] = 0
    maze_shape[centre_x - 1][centre_y + 3] = 0
    maze_shape[centre_x + 2][centre_y + 3] = 0
    maze_shape[centre_x - 2][centre_y + 3] = 0
    maze_shape[centre_x + 3][centre_y + 3] = 0
    maze_shape[centre_x - 3][centre_y + 3] = 0
    maze_shape[centre_x + 4][centre_y + 3] = 0
    maze_shape[centre_x - 4][centre_y + 3] = 0
    maze_shape[centre_x][centre_y - 3] = 0
    maze_shape[centre_x + 1][centre_y - 3] = 0
    maze_shape[centre_x - 1][centre_y - 3] = 0
    maze_shape[centre_x + 2][centre_y - 3] = 0
    maze_shape[centre_x - 2][centre_y - 3] = 0
    maze_shape[centre_x + 3][centre_y - 3] = 0
    maze_shape[centre_x - 3][centre_y - 3] = 0
    maze_shape[centre_x + 4][centre_y - 3] = 0
    maze_shape[centre_x - 4][centre_y - 3] = 0
    maze_shape[centre_x + 4][centre_y] = 0
    maze_shape[centre_x + 4][centre_y - 1] = 0
    maze_shape[centre_x + 4][centre_y + 1] = 0
    maze_shape[centre_x + 4][centre_y - 2] = 0
    maze_shape[centre_x + 4][centre_y + 2] = 0
    maze_shape[centre_x - 4][centre_y] = 0
    maze_shape[centre_x - 4][centre_y - 1] = 0
    maze_shape[centre_x - 4][centre_y + 1] = 0
    maze_shape[centre_x - 4][centre_y - 2] = 0
    maze_shape[centre_x - 4][centre_y + 2] = 0

    maze_base = []
    maze_walls = []
    junction_points = []
    pill_zones = []
    maze_base.append([120 + (centre_x * 18), 30 + (centre_y * 18)])  # add the base entrance first
    maze_ghost_gate = MazeGhostGate((centre_y - 2, centre_x - 1), (centre_y - 2, centre_x + 1))
    for x in range(0, shape[0]):
        for y in range(0, shape[1]):
            if maze_shape[x][y] == 1:
                # check for neighbours with a wall, if a wall is on it's own we just won't draw it
                if y + 1 < shape[0]:
                    if maze_shape[x][y + 1] == 1:
                        maze_walls = add_new_wall_if_unique(MazeWall((y, x), (y + 1, x)), maze_walls)
                if y - 1 > 0:
                    if maze_shape[x][y - 1] == 1:
                        maze_walls = add_new_wall_if_unique(MazeWall((y, x), (y - 1, x)), maze_walls)
                if x + 1 < shape[1]:
                    if maze_shape[x + 1][y] == 1:
                        maze_walls = add_new_wall_if_unique(MazeWall((y, x), (y, x + 1)), maze_walls)
                if x - 1 > 0:
                    if maze_shape[x - 1][y] == 1:
                        maze_walls = add_new_wall_if_unique(MazeWall((y, x), (y, x - 1)), maze_walls)
            elif maze_shape[x][y] == 0:
                if (maze_shape[x][y + 1] == 1) and (maze_shape[x][y - 1] == 1) and (maze_shape[x - 1][y] == 0) and (
                        maze_shape[x + 1][y] == 0):
                    pass  # in horizontal corridor
                elif (maze_shape[x][y + 1] == 0) and (maze_shape[x][y - 1] == 0) and (maze_shape[x - 1][y] == 1) and (
                        maze_shape[x + 1][y] == 1):
                    pass  # vertical corridor
                else:  # must be a point at which we can or need to change direction
                    junction_points.append(JunctionPoint(x, y))

                if centre_y - 2 < y < centre_y + 2 and centre_x - 3 < x < centre_x + 3:
                    maze_base.append([x, y])  # in ghost cube so don't place any pills
                elif x == centre_x and y == centre_y - 2:
                    pass  # in ghost cube doorway = no pills
                else:
                    if x == 1 and y == 1:
                        pill_zones.append(PillZone(x, y, True))
                    elif x == 29 and y == 1:
                        pill_zones.append(PillZone(x, y, True))
                    elif x == 1 and y == 29:
                        pill_zones.append(PillZone(x, y, True))
                    elif x == 29 and y == 29:
                        pill_zones.append(PillZone(x, y, True))
                    else:
                        pill_zones.append(PillZone(x, y, False))

    for point in junction_points:
        # locate neighbours in the four possible directions if they exist
        x_explore = point.grid_x_pos + 1
        found_wall_or_neighbour = False
        while x_explore < shape[1] and not found_wall_or_neighbour:  # direction 1
            if maze_shape[x_explore][point.grid_y_pos] == 0:
                for neighbour_point in junction_points:
                    if neighbour_point.grid_y_pos == point.grid_y_pos and neighbour_point.grid_x_pos == x_explore:
                        point.nav_node.neighbours.append(neighbour_point.nav_node)
                        found_wall_or_neighbour = True
                        break
                x_explore += 1
            elif maze_shape[x_explore][point.grid_y_pos] == 1:
                found_wall_or_neighbour = True
                if x_explore - 1 != point.grid_x_pos:
                    for neighbour_point in junction_points:
                        if neighbour_point.grid_x_pos == x_explore - 1 and\
                                neighbour_point.grid_y_pos == point.grid_y_pos:
                            point.nav_node.neighbours.append(neighbour_point.nav_node)
                            break

        x_explore = point.grid_x_pos - 1
        found_wall_or_neighbour = False
        while x_explore > 0 and not found_wall_or_neighbour:  # direction 2
            if maze_shape[x_explore][point.grid_y_pos] == 0:
                for neighbour_point in junction_points:
                    if neighbour_point.grid_y_pos == point.grid_y_pos and neighbour_point.grid_x_pos == x_explore:
                        point.nav_node.neighbours.append(neighbour_point.nav_node)
                        found_wall_or_neighbour = True
                        break
                x_explore -= 1
            elif maze_shape[x_explore][point.grid_y_pos] == 1:
                found_wall_or_neighbour = True
                if x_explore + 1 != point.grid_x_pos:
                    for neighbour_point in junction_points:
                        if neighbour_point.grid_x_pos == x_explore + 1 and\
                                neighbour_point.grid_y_pos == point.grid_y_pos:
                            point.nav_node.neighbours.append(neighbour_point.nav_node)
                            break

        y_explore = point.grid_y_pos + 1
        found_wall_or_neighbour = False
        while y_explore < shape[0] and not found_wall_or_neighbour:  # direction 3
            if maze_shape[point.grid_x_pos][y_explore] == 0:
                for neighbour_point in junction_points:
                    if neighbour_point.grid_y_pos == y_explore and neighbour_point.grid_x_pos == point.grid_x_pos:
                        point.nav_node.neighbours.append(neighbour_point.nav_node)
                        found_wall_or_neighbour = True
                        break
                y_explore += 1
            elif maze_shape[point.grid_x_pos][y_explore] == 1:
                found_wall_or_neighbour = True
                if y_explore - 1 != point.grid_y_pos:
                    for neighbour_point in junction_points:
                        if neighbour_point.grid_y_pos == y_explore - 1 and\
                                neighbour_point.grid_x_pos == point.grid_x_pos:
                            point.nav_node.neighbours.append(neighbour_point.nav_node)
                            break

        y_explore = point.grid_y_pos - 1
        found_wall_or_neighbour = False
        while y_explore > 0 and not found_wall_or_neighbour:  # direction 4
            if maze_shape[point.grid_x_pos][y_explore] == 0:
                for neighbour_point in junction_points:
                    if neighbour_point.grid_y_pos == y_explore and\
                            neighbour_point.grid_x_pos == point.grid_x_pos:
                        point.nav_node.neighbours.append(neighbour_point.nav_node)
                        found_wall_or_neighbour = True
                        break

                y_explore -= 1
            elif maze_shape[point.grid_x_pos][y_explore] == 1:
                found_wall_or_neighbour = True
                if y_explore + 1 != point.grid_y_pos:
                    for neighbour_point in junction_points:
                        if neighbour_point.grid_y_pos == y_explore + 1 and\
                                neighbour_point.grid_x_pos == point.grid_x_pos:
                            point.nav_node.neighbours.append(neighbour_point.nav_node)
                            break

    return maze_walls, junction_points, pill_zones, maze_base, maze_ghost_gate
