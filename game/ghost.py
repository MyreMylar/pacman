import math
import random
import pygame

from game.path_finder import PathFinder


class Ghost(pygame.sprite.Sprite):
    def __init__(self, start_pos, ghost_image_name, level_num, *groups):

        super().__init__(*groups)
        self.startLoc = start_pos
        self.levelNum = level_num
        self.image_name = ghost_image_name
        self.original_ghost_image = pygame.image.load(ghost_image_name).convert_alpha()
        self.vulnerable_ghost_image = pygame.image.load("images/vulnerable_ghost.png").convert_alpha()
        self.ghost_eyes_image = pygame.image.load("images/ghost_eyes.png").convert_alpha()
        self.ghost_image = self.original_ghost_image.copy()

        self.image = self.ghost_image
        self.rect = self.ghost_image.get_rect()
        self.rect.topleft = start_pos

        self.ghost_speed = 100.0 + min(50, (10.0 * level_num - 1))
        self.ghost_position = [float(self.rect.center[0]), float(self.rect.center[1])]

        self.should_die = False
        self.is_dead = False
        self.current_path = []
        self.move_target = self.ghost_position

        self.is_start = True
        self.is_vulnerable = False
        self.vulnerability_timer = 0.0

        self.is_dead = False
        self.is_in_base = False

        self.ai_value = 0

        # The type of AI behaviour is determined by the image name
        # The red ghost is more likely to home in on the player.

        if self.image_name == "images/green_ghost.png":
            self.ai_value = 1
        elif self.image_name == "images/purple_ghost.png":
            self.ai_value = 4
        elif self.image_name == "images/blue_ghost.png":
            self.ai_value = 6
        elif self.image_name == "images/red_ghost.png":
            self.ai_value = 8

        self.score = 500
            
    def update_sprite(self, all_sprites):
        all_sprites.add(self)
        return all_sprites

    def start_vulnerability(self):
        if not self.is_dead or self.should_die:
            self.is_vulnerable = True
            self.image = self.vulnerable_ghost_image
            self.vulnerability_timer += max(20.0 - self.levelNum, 0.0)

    def check_in_base(self, maze_base, time_delta):
        in_base = False
        for square in maze_base:
            if self.approx_equal(self.ghost_position, square, time_delta):
                in_base = True
        return in_base

    @staticmethod
    def neighbour_sorter(s):
        return s[0]

    @staticmethod
    def find_closest_junction_to_base(maze_base, maze_junctions):
        shortest_distance = 9999999999.0
        closest_junction = None
        for junction in maze_junctions:
            # distance from gate
            x_diff = junction.nav_node.position[0] - maze_base[0][0]
            y_diff = junction.nav_node.position[1] - maze_base[0][1]
            dist_sq = x_diff ** 2 + y_diff ** 2

            if dist_sq < shortest_distance:
                shortest_distance = dist_sq
                closest_junction = junction

        return closest_junction

    def update_movement_and_collision(self, time_delta, maze_junctions, maze_base, players):
        time_delta = min(1.0, time_delta)
        if self.should_die:
            self.image = self.ghost_eyes_image
            self.is_dead = True
            self.should_die = False
            self.current_path = []

        if self.is_dead:
            if self.check_in_base(maze_base, time_delta):
                self.is_in_base = True
                self.current_path = []
            else:
                self.is_in_base = False
            # if we are dead the eyes travel back to base

            if self.approx_equal(self.ghost_position, self.move_target, time_delta):
                if len(self.current_path) > 0:
                    self.move_target = self.current_path.pop().position
                else:
                    ghost_junction = self.find_closest_junction(maze_junctions)
                    base_junction = self.find_closest_junction_to_base(maze_base, maze_junctions)
                    path_finder = PathFinder(ghost_junction.nav_node, base_junction.nav_node, len(maze_junctions))
                    self.current_path = path_finder.final_path

        else:
            if self.is_vulnerable:
                self.vulnerability_timer -= time_delta
                if self.vulnerability_timer <= 0.0:
                    self.is_vulnerable = False
                    self.image = self.ghost_image

            # figure out if it's time to change our direction of travel
            if self.is_start or self.approx_equal(self.ghost_position, self.move_target, time_delta):
                self.is_start = False
                neighbours = self.find_closest_junction(maze_junctions).nav_node.neighbours
                new_target_junction = None
                if not self.is_vulnerable:
                    decision_value = random.randint(0, 9)
                    if len(players) > 0 and decision_value <= self.ai_value:
                        ghost_junction = self.find_closest_junction(maze_junctions)
                        player_junction = self.find_closest_junction_to_player(players, maze_junctions)
                        path_finder = PathFinder(ghost_junction.nav_node, player_junction.nav_node, len(maze_junctions))
                        self.current_path = path_finder.final_path
                        if len(self.current_path) > 0:
                            self.move_target = self.current_path.pop().position
                    else:
                        new_target_junction = random.choice(neighbours)
                        self.move_target = (new_target_junction.position[0], new_target_junction.position[1])
                else:
                    decision_value = random.randint(0, 9)
                    if decision_value <= self.ai_value:
                        new_target_junction = self.find_furthest_junction_to_player(players, neighbours,
                                                                                    new_target_junction)
                        if new_target_junction is not None:
                            self.move_target = (new_target_junction.position[0], new_target_junction.position[1])
                        else:
                            new_target_junction = random.choice(neighbours)
                            self.move_target = (new_target_junction.position[0], new_target_junction.position[1])
                    else:
                        new_target_junction = random.choice(neighbours)
                        self.move_target = (new_target_junction.position[0], new_target_junction.position[1])

        x_diff = self.move_target[0] - self.ghost_position[0]
        y_diff = self.move_target[1] - self.ghost_position[1]
        distance = math.sqrt((x_diff * x_diff) + (y_diff * y_diff))

        x_direction = x_diff / distance
        y_direction = y_diff / distance

        self.ghost_position[0] += self.ghost_speed * x_direction * time_delta
        self.ghost_position[1] += self.ghost_speed * y_direction * time_delta

        self.rect.center = (int(self.ghost_position[0]), int(self.ghost_position[1]))

    def respawn(self):
        self.should_die = False
        self.is_dead = False
        self.move_target = self.ghost_position
        self.is_start = True
        self.is_vulnerable = False
        self.vulnerability_timer = 0.0
        self.is_dead = False
        self.image = self.ghost_image
        self.is_in_base = False

    def find_closest_junction(self, maze_junctions):
        shortest_distance = 5000000000
        found_junction = None
        for junction in maze_junctions:
            x_dist = junction.nav_node.position[0] - self.ghost_position[0]
            y_dist = junction.nav_node.position[1] - self.ghost_position[1]
            distance = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))

            if distance < shortest_distance:
                shortest_distance = distance
                found_junction = junction
        return found_junction

    def approx_equal(self, point_a, point_b, time_delta):
        x_dist = point_a[0] - point_b[0]
        y_dist = point_a[1] - point_b[1]
        distance = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
        if distance < self.ghost_speed * time_delta:
            return True
        else:
            return False

    @staticmethod
    def find_closest_junction_to_player(players, maze_junctions):
        player_junction = None
        shortest_sq_dist_to_player = 9999999.0
        for junction in maze_junctions:
            for player in players:
                x_diff = junction.nav_node.position[0] - player.position[0]
                y_diff = junction.nav_node.position[1] - player.position[1]
                dist_sq = x_diff * x_diff + y_diff * y_diff
                if dist_sq < shortest_sq_dist_to_player:
                    shortest_sq_dist_to_player = dist_sq
                    player_junction = junction
        return player_junction

    @staticmethod
    def find_furthest_junction_to_player(players, neighbours, new_target_junction):
        furthest_sq_dist_to_player = 0.0
        for junction in neighbours:
            for player in players:
                x_diff = junction.position[0] - player.position[0]
                y_diff = junction.position[1] - player.position[1]
                dist_sq = x_diff * x_diff + y_diff * y_diff
                if dist_sq > furthest_sq_dist_to_player:
                    furthest_sq_dist_to_player = dist_sq
                    new_target_junction = junction
        return new_target_junction
