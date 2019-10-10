import math
import pygame
from pygame.locals import *

# ----------------------------------------------------------------------
# Scroll down for Challenge 2 in the 'update_movement_and_collision'
# function on line 121 - where we learn about collision.
# ----------------------------------------------------------------------


class Scheme:
    def __init__(self):
        self.up = K_UP
        self.down = K_DOWN
        self.left = K_LEFT
        self.right = K_RIGHT


class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, control_scheme, *groups):
        
        super().__init__(*groups)
        self.scheme = control_scheme
        self.image_name = "images/player.png"
        self.original_image = pygame.image.load(self.image_name).convert_alpha()
        self.sprite_sheet = self.original_image.copy()
        self.closed_left_pac = self.sprite_sheet.subsurface(pygame.Rect(2, 2, 32, 32))
        self.half_open_left_pac = self.sprite_sheet.subsurface(pygame.Rect(34, 2, 32, 32))
        self.full_open_left_pac = self.sprite_sheet.subsurface(pygame.Rect(66, 2, 32, 32))
        self.closed_right_pac = pygame.transform.flip(self.sprite_sheet.subsurface(pygame.Rect(2, 2, 32, 32)),
                                                      True, False)
        self.half_open_right_pac = pygame.transform.flip(self.sprite_sheet.subsurface(pygame.Rect(34, 2, 32, 32)),
                                                         True, False)
        self.full_open_right_pac = pygame.transform.flip(self.sprite_sheet.subsurface(pygame.Rect(66, 2, 32, 32)),
                                                         True, False)
        self.closed_up_pac = pygame.transform.rotate(self.sprite_sheet.subsurface(pygame.Rect(2, 2, 32, 32)), -90.0)
        self.half_open_up_pac = self.sprite_sheet.subsurface(pygame.Rect(98, 2, 32, 32))
        self.full_open_up_pac = self.sprite_sheet.subsurface(pygame.Rect(130, 2, 32, 32))
        self.closed_down_pac = pygame.transform.rotate(self.sprite_sheet.subsurface(pygame.Rect(2, 2, 32, 32)), 90.0)
        self.half_open_down_pac = pygame.transform.flip(self.sprite_sheet.subsurface(pygame.Rect(98, 2, 32, 32)),
                                                        False, True)
        self.full_open_down_pac = pygame.transform.flip(self.sprite_sheet.subsurface(pygame.Rect(130, 2, 32, 32)),
                                                        False, True)

        self.image = self.closed_left_pac
        self.rect = self.closed_left_pac.get_rect()
        self.rect.center = start_pos
        self.lives = 3

        self.should_move_up = False
        self.should_move_right = False
        self.should_move_down = False
        self.should_move_left = False

        self.last_vert_heading_vector = [0, 0]
        self.last_horiz_heading_vector = [0, 0]
        
        self.should_vert_drift_to_next_centre = False
        self.should_horiz_drift_to_next_centre = False

        self.normal_speed = 200.0
        self.eating_speed = 160.0
        self.speed = self.normal_speed

        self.should_die = False

        self.move_accumulator = 0.0
       
        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]

        self.eat_pill_slowdown_time = 0.6
        self.pill_eaten_countdown = 0.0

        self.respawn_invincible = True
        self.respawn_invincibility_time = 3.0

    def update_sprite(self, all_sprites):
        all_sprites.add(self)
        return all_sprites

    def process_event(self, event):
        if event.type == KEYDOWN:
            if event.key == self.scheme.left:
                self.should_move_left = True
                self.should_move_right = False
                self.should_move_up = False
                self.should_move_down = False
            elif event.key == self.scheme.right:
                self.should_move_right = True
                self.should_move_left = False
                self.should_move_up = False
                self.should_move_down = False
            elif event.key == self.scheme.up:
                self.should_move_up = True
                self.should_move_right = False
                self.should_move_left = False
                self.should_move_down = False
            elif event.key == self.scheme.down:
                self.should_move_down = True
                self.should_move_right = False
                self.should_move_left = False
                self.should_move_up = False

        elif event.type == KEYUP:
            if event.key == self.scheme.left:
                self.should_move_left = False
                self.should_horiz_drift_to_next_centre = True
            elif event.key == self.scheme.right:
                self.should_move_right = False
                self.should_horiz_drift_to_next_centre = True
            elif event.key == self.scheme.up:
                self.should_move_up = False
                self.should_vert_drift_to_next_centre = True
            elif event.key == self.scheme.down:
                self.should_move_down = False
                self.should_vert_drift_to_next_centre = True

    def update_movement_and_collision(self, time_delta, maze_walls, maze_ghost_gate,
                                      pill_zones, ghosts, pills, fruits, player_stats):

        # -----------------------------------------------------------------------
        # CHALLENGE 2
        # -------------
        # Your task is to add another collision for loop that kills the player when he
        # hits a ghost.
        #
        # A collision loop is just a way of checking if a bunch of
        # objects of the same type are touching something. We step through each
        # ghost, fruit or pill and check if it is colliding with the player and,
        # if it is, do something appropriate.
        #
        # Tips:
        # ------
        # - Look at the two 'for' loops below for the yellow pills and the bonus fruits.
        #   Your code will need to be similar.
        #
        # - The objects are all held in python lists. A list can be created like this in Python;
        #   myList = [thingZeroInList, thingOneInList, thingTwoInList]
        #
        # - A for loop is the most commonly used loop in python and you will often see
        #   it used like this ( e.g. for member in list ) to step through every member
        #   of a list of things.
        #
        # - Set 'self.should_die' equal to True to kill the player.
        # ------------------------------------------------------------------------

        # -----------------------------------------------------------------------
        # Bonus Challenge
        # -----------------------------------------------------------------------
        # To strike back at the ghosts in true pacman
        # style you will need to test if the ghost.is_vulnerable
        # variable is True during a collision.
        #
        # If it is, you should kill the ghost instead of Pacman.
        #
        # Don't forget to give yourself 500 points onto your score if you manage
        # to kill a vulnerable ghost
        # -----------------------------------------------------------------------
        for fruit in fruits:
            if self.test_collision(fruit):
                fruit.should_die = True
                player_stats.score += fruit.score
                
        for pill in pills:
            if self.test_collision(pill):
                pill.should_die = True
                self.pill_eaten_countdown = self.eat_pill_slowdown_time
                if pill.is_large_pill:
                    player_stats.score += 50
                    for ghost in ghosts:
                        ghost.start_vulnerability()
                else:
                    player_stats.score += 10

        if self.pill_eaten_countdown > 0.0:
            self.pill_eaten_countdown -= time_delta
            self.speed = self.eating_speed
        else:
            self.speed = self.normal_speed

        if self.should_move_up or self.should_move_down or self.should_move_left\
                or self.should_move_right or self.should_horiz_drift_to_next_centre\
                or self.should_vert_drift_to_next_centre:
            
            last_move_horiz = False
            previous_pos = [self.position[0], self.position[1]]
            temp_rect = self.rect.copy()
            
            if self.should_move_up and not self.should_horiz_drift_to_next_centre:
                self.should_vert_drift_to_next_centre = False
                if self.move_accumulator > 0.0:
                    self.move_accumulator = 0.0
                else:
                    self.move_accumulator -= self.speed * time_delta
                self.last_vert_heading_vector = [0.0, -1.0]
                self.position[0] += (self.last_vert_heading_vector[0] * self.speed * time_delta)
                self.position[1] += (self.last_vert_heading_vector[1] * self.speed * time_delta)
                temp_rect.center = (int(self.position[0]), int(self.position[1]))

            if self.should_move_down and not self.should_horiz_drift_to_next_centre:
                self.should_vert_drift_to_next_centre = False
                if self.move_accumulator < 0.0:
                    self.move_accumulator = 0.0
                else:
                    self.move_accumulator += self.speed * time_delta
                self.last_vert_heading_vector = [0.0, 1.0]
                self.position[0] += (self.last_vert_heading_vector[0] * self.speed * time_delta)
                self.position[1] += (self.last_vert_heading_vector[1] * self.speed * time_delta)
                temp_rect.center = (int(self.position[0]), int(self.position[1]))

            if self.should_move_left and not self.should_vert_drift_to_next_centre:
                last_move_horiz = True
                self.should_horiz_drift_to_next_centre = False
                if self.move_accumulator > 0.0:
                    self.move_accumulator = 0.0
                else:
                    self.move_accumulator -= self.speed * time_delta
                self.last_horiz_heading_vector = [-1.0, 0.0]
                self.position[0] += (self.last_horiz_heading_vector[0] * self.speed * time_delta)
                self.position[1] += (self.last_horiz_heading_vector[1] * self.speed * time_delta)
                temp_rect.center = (int(self.position[0]), int(self.position[1]))

            if self.should_move_right and not self.should_vert_drift_to_next_centre:
                last_move_horiz = True
                self.should_horiz_drift_to_next_centre = False
                if self.move_accumulator < 0.0:
                    self.move_accumulator = 0.0
                else:
                    self.move_accumulator += self.speed * time_delta
                self.last_horiz_heading_vector = [1.0, 0.0]
                self.position[0] += (self.last_horiz_heading_vector[0] * self.speed * time_delta)
                self.position[1] += (self.last_horiz_heading_vector[1] * self.speed * time_delta)
                temp_rect.center = (int(self.position[0]), int(self.position[1]))

            if self.should_horiz_drift_to_next_centre:
                last_move_horiz = True
                if self.x_pos_in_col_centre_tolerance_range(pill_zones, time_delta):
                    self.should_horiz_drift_to_next_centre = False  # stop drifting
                    temp_rect.center = (int(self.position[0]), int(self.position[1]))
                else:
                    self.move_accumulator += self.last_horiz_heading_vector[0] * self.speed * time_delta
                    self.position[0] += (self.last_horiz_heading_vector[0] * self.speed * time_delta)
                    self.position[1] += (self.last_horiz_heading_vector[1] * self.speed * time_delta)
                    temp_rect.center = (int(self.position[0]), int(self.position[1]))

            if self.should_vert_drift_to_next_centre:
                if self.y_pos_in_row_centre_tolerance_range(pill_zones, time_delta):
                    self.should_vert_drift_to_next_centre = False
                    temp_rect.center = (int(self.position[0]), int(self.position[1]))
                else:
                    self.move_accumulator += self.last_vert_heading_vector[1] * self.speed * time_delta
                    self.position[0] += (self.last_vert_heading_vector[0] * self.speed * time_delta)
                    self.position[1] += (self.last_vert_heading_vector[1] * self.speed * time_delta)
                    temp_rect.center = (int(self.position[0]), int(self.position[1]))

            collided_horiz = False
            horiz_wall_line = [[0, 0], [0, 0]]
            collided_vert = False
            vert_wall_line = [[0, 0], [0, 0]]
            
            for wall in maze_walls:
                if self.test_wall_collision(temp_rect, wall):
                    wall.collided = True
                    self.should_vert_drift_to_next_centre = False
                    self.should_horiz_drift_to_next_centre = False
                    if wall.is_horiz_wall:
                        collided_horiz = True
                        
                        horiz_wall_line[0] = wall.start_pos
                        horiz_wall_line[1] = wall.end_pos
                    else:
                        collided_vert = True
                        
                        vert_wall_line[0] = wall.start_pos
                        vert_wall_line[1] = wall.end_pos

            if self.test_wall_collision(temp_rect, maze_ghost_gate):
                maze_ghost_gate.collided = True
                self.should_vert_drift_to_next_centre = False
                self.should_horiz_drift_to_next_centre = False
                collided_horiz = True
                
                horiz_wall_line[0] = maze_ghost_gate.start_pos
                horiz_wall_line[1] = maze_ghost_gate.end_pos

            if collided_vert:
                # is our centre of mass getting closer to the wall or further away?
                new_dist = self.distance_from_line(self.position, vert_wall_line)
                old_dist = self.distance_from_line(previous_pos, vert_wall_line)
                if new_dist < old_dist:
                    # closer to wall so stop dead
                    self.position[0] = previous_pos[0]
                    self.position[1] = previous_pos[1]
            if collided_horiz:
                new_dist = self.distance_from_line(self.position, horiz_wall_line)
                old_dist = self.distance_from_line(previous_pos, horiz_wall_line)
                if new_dist < old_dist:
                    self.position[1] = previous_pos[1]
                    self.position[0] = previous_pos[0]

            if last_move_horiz:
                if self.move_accumulator > 32.0:
                    self.image = self.closed_right_pac
                    self.move_accumulator = 0.0
                elif self.move_accumulator > 24.0:
                    self.image = self.half_open_right_pac
                elif self.move_accumulator > 16.0:
                    self.image = self.full_open_right_pac
                elif self.move_accumulator > 8.0:
                    self.image = self.half_open_right_pac

                if self.move_accumulator < -32.0:
                    self.image = self.closed_left_pac
                    self.move_accumulator = 0.0
                elif self.move_accumulator < -24.0:
                    self.image = self.half_open_left_pac
                elif self.move_accumulator < -16.0:
                    self.image = self.full_open_left_pac
                elif self.move_accumulator < -8.0:
                    self.image = self.half_open_left_pac
            else:
                if self.move_accumulator > 32.0:
                    self.image = self.closed_down_pac
                    self.move_accumulator = 0.0
                elif self.move_accumulator > 24.0:
                    self.image = self.half_open_down_pac
                elif self.move_accumulator > 16.0:
                    self.image = self.full_open_down_pac
                elif self.move_accumulator > 8.0:
                    self.image = self.half_open_down_pac

                if self.move_accumulator < -32.0:
                    self.image = self.closed_up_pac
                    self.move_accumulator = 0.0
                elif self.move_accumulator < -24.0:
                    self.image = self.half_open_up_pac
                elif self.move_accumulator < -16.0:
                    self.image = self.full_open_up_pac
                elif self.move_accumulator < -8.0:
                    self.image = self.half_open_up_pac

            self.rect.center = (int(self.position[0]), int(self.position[1]))

        if self.respawn_invincible:
            self.respawn_invincibility_time -= time_delta
            if self.respawn_invincibility_time <= 0.0:
                self.respawn_invincible = False

    def x_pos_in_col_centre_tolerance_range(self, pill_zones, time_delta):
        in_tolerance_range = False
        distance_from_centre = abs(self.get_nearest_maze_centre(pill_zones)[0] - self.position[0])
        max_move_per_frame = self.speed * time_delta
        if distance_from_centre < max_move_per_frame:
            self.position[0] = self.get_nearest_maze_centre(pill_zones)[0]
            in_tolerance_range = True
        return in_tolerance_range

    def y_pos_in_row_centre_tolerance_range(self, pill_zones, time_delta):
        in_tolerance_range = False
        distance_from_centre = abs(self.get_nearest_maze_centre(pill_zones)[1] - self.position[1])
        max_move_per_frame = self.speed * time_delta
        if distance_from_centre < max_move_per_frame:
            in_tolerance_range = True
            self.position[1] = self.get_nearest_maze_centre(pill_zones)[1]
        return in_tolerance_range

    def get_nearest_maze_centre(self, pill_zones):
        closest_zone = [0.0, 0.0]
        shortest_dist = 999999999.0
        for zone in pill_zones:
            x_diff = self.position[0] - zone.screen_x_pos
            y_diff = self.position[1] - zone.screen_y_pos
            dist = math.sqrt(x_diff * x_diff + y_diff * y_diff)
            if dist < shortest_dist:
                shortest_dist = dist
                closest_zone = [zone.screen_x_pos, zone.screen_y_pos]
        return closest_zone

    def test_wall_collision(self, temp_rect, wall):
        collided = False
        if self.get_hit_box(temp_rect).colliderect(wall.rect):
            collided = True
        return collided

    def test_collision(self, pill):
        collided = False
        if self.get_hit_box(self.rect).colliderect(pill.rect):
            collided = True

        return collided

    @staticmethod
    def get_hit_box(rect):
        smaller_rect = rect.copy()
        original_center = rect.center
        smaller_rect.width = 28
        smaller_rect.height = 28
        smaller_rect.center = original_center
        return smaller_rect
    
    @staticmethod
    def distance_from_line(point, line):

        x1 = line[0][0]
        y1 = line[0][1]
        x2 = line[1][0]
        y2 = line[1][1]
        x3 = point[0]
        y3 = point[1]

        px = x2-x1
        py = y2-y1

        something = px*px + py*py

        u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        # Note: If the actual distance does not matter,
        # if you only want to compare what this function
        # returns to other results of this function, you
        # can just return the squared distance instead
        # (i.e. remove the sqrt) to gain a little performance

        dist = math.sqrt(dx*dx + dy*dy)

        return dist


class RespawnPlayer:
    def __init__(self, player):
        self.control_scheme = player.scheme
        
        self.respawn_timer = 3.0
        self.time_to_spawn = False
        self.has_respawned = False

    def update(self, frame_time_ms):
        self.respawn_timer -= (frame_time_ms / 1000.0)
        if self.respawn_timer < 0.0:
            self.time_to_spawn = True


class PlayerStats:
    def __init__(self, screen_position):
        self.screen_position = screen_position
        self.score = 0
        self.lives = 3
