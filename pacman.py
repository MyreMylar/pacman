import os
import pygame
import random
from pygame.locals import *

from game.main_menu import MainMenu
from game.high_score_screen import HighScoreEntry, HighScoreScreen
from game.high_scores import HighScoreTable
from game.player import PlayerStats, Player, Scheme, RespawnPlayer
from game.mazegen import create_maze
from game.ghost import Ghost
from game.pills import Pill, LargePill
from game.fruit import Fruit

# ---------------------------------------------------------------------
# HEY!
# ------
# Scroll down for the first of this week's challenges!
#
# ---------------------------------------------------------------------


class ScreenData:
    def __init__(self, screen_size):
        self.screen_size = screen_size


class Pacman:
    def __init__(self):

        # some colours
        self.BLACK = (0,   0,   0)
        self.RED = (255,   0,   0)
        self.BLUE = (75,   75,   200)

        # create empty pygame window with white background
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'  # center the window in the middle of the screen
        self.screen_data = ScreenData((800, 600))
        pygame.display.set_caption('A-Maze-ing Pac-Man 2.0')
        self.screen = pygame.display.set_mode(self.screen_data.screen_size)

        pygame.key.set_repeat()
        
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert(self.screen)
        self.background.fill((0, 0, 0))
        
        self.all_pill_sprites = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.fonts = []
        self.font = pygame.font.Font(None, 30)
        self.fonts.append(pygame.font.Font("fonts/PAC-FONT.TTF", 72))
        self.fonts.append(self.font)

        self.high_score_table = HighScoreTable()
        self.high_score_table.load()

        self.high_score_entry = HighScoreEntry(self.screen, self.screen_data, self.fonts, self.high_score_table)

        self.main_menu = MainMenu(self.fonts)
        self.high_score_screen = HighScoreScreen(self.fonts, self.high_score_table)
        self.is_main_menu = True
        self.is_high_score_screen = False
        self.is_play_game_screen = False

        self.should_enter_high_score = False

        self.score_board = []
        self.player_stats = PlayerStats((750, 50))
        self.score_board.append(self.player_stats)

        self.start_locations = []
        self.start_locations.append((390, 372))

        self.level_number = 0

        self.should_reset_game = False
        self.maze_base = []
        self.maze_ghost_gate = None
        self.maze_walls = []
        self.maze_junctions = []
        self.pill_zones = []
        self.pill_total = 0

        self.spawned_first_fruit_this_level = False
        self.spawned_second_fruit_this_level = False

        self.players = []
        self.pills = []
        self.fruits = []
        self.ghosts = []

        self.players_to_respawn = []
        self.ghosts_to_respawn = []

        self.wall_colour = None
        
        self.advance_to_next_level()

    # This function sets up a new level with a randomly generated maze and some ghostly enemies
    def advance_to_next_level(self):
        
        del self.maze_walls[:]
        del self.maze_junctions[:]
        del self.pill_zones[:]

        del self.players[:]
        del self.pills[:]
        del self.fruits[:]
        del self.ghosts_to_respawn[:]
        del self.ghosts[:]

        self.level_number += 1
        
        # generate a maze
        maze_walls_pill_zones_and_junctions = create_maze(30, 30)
        self.maze_walls = maze_walls_pill_zones_and_junctions[0]
        self.maze_junctions = maze_walls_pill_zones_and_junctions[1]
        self.pill_zones = maze_walls_pill_zones_and_junctions[2]
        self.maze_base = maze_walls_pill_zones_and_junctions[3]
        self.maze_ghost_gate = maze_walls_pill_zones_and_junctions[4]
        
        self.ghosts_to_respawn = []
        self.ghosts = []
        
        # ----------------------------------------------------------------------
        # Challenge 1
        # --------------------
        #
        # Add more ghosts in different colours! You do this by creating Ghost
        # objects with different starting parameters below.
        # - There are different coloured ghost images in the images/ folder
        # - remember to add the new ghosts to the self.ghosts list with append
        #
        # -------------------------------------------------------------
        # Challenge 2 is found in the game/player python file!
        # -----------------------------------------------------------------------
        
        ghost_1 = Ghost((400, 275), 'images/green_ghost.png', self.level_number)
        self.ghosts.append(ghost_1)

        self.wall_colour = pygame.Color(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        
        self.all_pill_sprites.empty()
        self.pills = []
        for zone in self.pill_zones:
            if zone.large_pill:
                pill = LargePill((zone.screen_x_pos, zone.screen_y_pos), self.all_pill_sprites)
            else:
                pill = Pill((zone.screen_x_pos, zone.screen_y_pos), self.all_pill_sprites)
            self.pills.append(pill)

        self.pill_total = len(self.pills)
        player_control_scheme = Scheme()

        self.players = []
        self.players.append(Player(random.choice(self.start_locations), player_control_scheme))

        self.fruits = []
        self.spawned_first_fruit_this_level = False
        self.spawned_second_fruit_this_level = False

    def run_game(self):
        clock = pygame.time.Clock()
        running = True  
        while running:
            frame_time = clock.tick(60)
            time_delta = frame_time/1000.0

            if self.is_main_menu:
                is_main_menu_and_index = self.main_menu.run(self.screen, self.background, self.fonts, self.screen_data)
                if is_main_menu_and_index[0] == 0:
                    self.is_main_menu = True
                    self.is_high_score_screen = False
                    self.is_play_game_screen = False
                elif is_main_menu_and_index[0] == 1:
                    self.is_play_game_screen = True
                    self.is_main_menu = False
                    self.is_high_score_screen = False
                    self.reset_game()
                elif is_main_menu_and_index[0] == 2:
                    self.is_high_score_screen = True
                    self.is_main_menu = False
                    self.is_play_game_screen = False
                elif is_main_menu_and_index[0] == 3:
                    running = False
            elif self.is_high_score_screen:
                is_main_menu_and_index = self.high_score_screen.run(self.screen, self.background,
                                                                    self.screen_data)
                if is_main_menu_and_index[0] == 0:
                    self.is_main_menu = True
                    self.is_high_score_screen = False
                    self.is_play_game_screen = False
                elif is_main_menu_and_index[0] == 1:
                    self.is_play_game_screen = True
                    self.is_main_menu = False
                    self.is_high_score_screen = False
                elif is_main_menu_and_index[0] == 2:
                    self.is_high_score_screen = True
                    self.is_main_menu = False
                    self.is_play_game_screen = False
                elif is_main_menu_and_index[0] == 3:
                    running = False
            elif self.should_enter_high_score:
                output_game_state = self.high_score_entry.update(self.player_stats.score)
                if output_game_state == "title_screen":
                    self.is_main_menu = True
                    self.should_enter_high_score = False
                self.high_score_entry.display(self.background)
            else:
                # create a bonus fruit after eating 150 pills
                if not self.spawned_first_fruit_this_level and (len(self.pills) == self.pill_total - 150):
                    self.spawned_first_fruit_this_level = True
                    self.fruits.append(Fruit(self.level_number, self.all_pill_sprites,
                                             random.choice(self.start_locations)))
                # create a 2nd bonus fruit after eating 300 pills
                if not self.spawned_second_fruit_this_level and (len(self.pills) == self.pill_total - 300):
                    self.spawned_second_fruit_this_level = True
                    self.fruits.append(Fruit(self.level_number, self.all_pill_sprites,
                                             random.choice(self.start_locations)))
                       
                # handle UI and inout events
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False    
                    for player in self.players:
                        player.process_event(event)

                # handle respawning players and ghosts after dying
                for respawning_player in self.players_to_respawn:
                    if respawning_player.time_to_spawn:
                        self.players.append(Player(random.choice(self.start_locations),
                                                   respawning_player.control_scheme))
                        respawning_player.has_respawned = True
                    else:
                        respawning_player.update(frame_time)
                self.players_to_respawn[:] = [r for r in self.players_to_respawn if not r.has_respawned]
                
                self.all_sprites.empty()
                for ghost in self.ghosts:
                    ghost.update_movement_and_collision(time_delta, self.maze_junctions,
                                                        self.maze_base, self.players)
                    self.all_sprites = ghost.update_sprite(self.all_sprites)
                    if ghost.is_in_base and ghost.is_dead:
                        ghost.respawn()
                    
                # update players and bullets
                for player in self.players:
                    player.update_movement_and_collision(time_delta, self.maze_walls, self.maze_ghost_gate,
                                                         self.pill_zones, self.ghosts, self.pills,
                                                         self.fruits, self.player_stats)
                    self.all_sprites = player.update_sprite(self.all_sprites)
                    if player.should_die and player.respawn_invincible:
                        player.should_die = False
                    elif player.should_die and self.player_stats.lives > 0 and not player.respawn_invincible:
                        self.player_stats.lives -= 1
                        self.players_to_respawn.append(RespawnPlayer(player))
                    elif player.should_die and self.player_stats.lives == 0 and not player.respawn_invincible:
                        if self.high_score_table.is_score_high(self.player_stats.score):
                            self.should_enter_high_score = True
                        else:
                            self.is_main_menu = True
                self.players[:] = [player for player in self.players if not player.should_die]

                for pill in self.pills:
                    pill.update_sprite(self.all_pill_sprites)
                self.pills[:] = [pill for pill in self.pills if not pill.should_die]

                self.fruits[:] = [fruit for fruit in self.fruits if not fruit.should_it_die(time_delta)]

                self.all_sprites.update()
                
                self.screen.blit(self.background, (0, 0))  # draw the background

                # draw maze
                for wall in self.maze_walls:
                    pygame.draw.line(self.screen, self.wall_colour, wall.start_pos, wall.end_pos, 4)

                pygame.draw.line(self.screen, self.RED, self.maze_ghost_gate.start_pos,
                                 self.maze_ghost_gate.end_pos, 4)
                self.all_pill_sprites.draw(self.screen)  # draw our pills
                self.all_sprites.draw(self.screen)  # draw all our moving sprites

                if len(self.pills) == 0:
                    self.advance_to_next_level()

                for score in self.score_board:
                    score_string = "Score:" 
                    score_text_render = self.font.render(score_string, True,
                                                         pygame.Color("#FFFFFF"))
                    score_text_render_rect = score_text_render.get_rect(centerx=score.screen_position[0],
                                                                        centery=score.screen_position[1])
                    score_text_render2 = self.font.render(str(score.score), True, pygame.Color("#FFFFFF"))
                    score_text_render_rect2 = score_text_render.get_rect(centerx=score.screen_position[0],
                                                                         centery=score.screen_position[1] + 32)
                    self.screen.blit(score_text_render, score_text_render_rect)
                    self.screen.blit(score_text_render2, score_text_render_rect2)

                    lives_string = "Lives:" 
                    lives_text_render = self.font.render(lives_string, True, pygame.Color("#FFFFFF"))
                    lives_text_render_rect = score_text_render.get_rect(centerx=score.screen_position[0],
                                                                        centery=score.screen_position[1] + 96)
                    lives_text_render2 = self.font.render(str(score.lives), True, pygame.Color("#FFFFFF"))
                    lives_text_render_rect2 = score_text_render.get_rect(centerx=score.screen_position[0],
                                                                         centery=score.screen_position[1] + 128)
                    self.screen.blit(lives_text_render, lives_text_render_rect)
                    self.screen.blit(lives_text_render2, lives_text_render_rect2)

                    level_string = "Level:" 
                    level_text_render = self.font.render(level_string, True, pygame.Color("#FFFFFF"))
                    level_text_render_rect = score_text_render.get_rect(centerx=score.screen_position[0],
                                                                        centery=score.screen_position[1] + 192)
                    level_text_render2 = self.font.render(str(self.level_number), True, pygame.Color("#FFFFFF"))
                    level_text_render_rect2 = score_text_render.get_rect(centerx=score.screen_position[0],
                                                                         centery=score.screen_position[1] + 224)
                    self.screen.blit(level_text_render, level_text_render_rect)
                    self.screen.blit(level_text_render2, level_text_render_rect2)

            pygame.display.flip()  # flip all our drawn stuff onto the screen

        pygame.quit()  # exited game loop so quit pygame

    def reset_game(self):
          
        self.should_reset_game = False
        self.score_board = []
        
        self.level_number = 0
        self.advance_to_next_level()

        self.player_stats = PlayerStats((750, 50))
        self.score_board.append(self.player_stats)

        self.high_score_entry = HighScoreEntry(self.screen, self.screen_data, self.fonts, self.high_score_table)

        
def main():
    game = Pacman()
    game.run_game()


if __name__ == '__main__':
    main()
