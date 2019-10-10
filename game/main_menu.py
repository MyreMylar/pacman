import pygame
from pygame.locals import *

from game.ui_text_button import UTTextButton


class MainMenu:

    def __init__(self, fonts):
        self.show_menu = True
        self.show_high_scores = False
        self.start_game = False

        self.background_image = pygame.image.load("images/menu_background.png")

        self.play_game_button = UTTextButton([325, 490, 150, 35], "Play Game", fonts, 1)
        self.high_scores_button = UTTextButton([325, 545, 150, 35], "High Scores", fonts, 1)

        self.is_running = True
        
    def run(self, screen, background, fonts, screen_data):
        is_main_menu_and_index = [0, 0]
        for event in pygame.event.get():
            self.play_game_button.handle_input_event(event)
            self.high_scores_button.handle_input_event(event)
            
            if event.type == QUIT:
                self.is_running = False

        self.play_game_button.update()
        self.high_scores_button.update()
        
        if self.play_game_button.was_pressed():
            self.start_game = True
            self.show_menu = False

        if self.high_scores_button.was_pressed():
            self.show_high_scores = True
            self.show_menu = False

        screen.blit(background, (0, 0))  # clear the background to black
        screen.blit(self.background_image, (0, 0))  # draw the background
        
        main_menu_title_string = "Pac-Man"
        main_menu_title_text_render = fonts[0].render(main_menu_title_string, True, pygame.Color("#FFFF00"))
        screen.blit(main_menu_title_text_render,
                    main_menu_title_text_render.get_rect(centerx=screen_data.screen_size[0] * 0.5,
                                                         centery=screen_data.screen_size[1] * 0.10))

        self.play_game_button.draw(screen)
        self.high_scores_button.draw(screen)
                
        if self.show_high_scores:
            is_main_menu_and_index[0] = 2
            self.show_menu = True
            self.show_high_scores = False
            self.start_game = False
        elif self.start_game:
            is_main_menu_and_index[0] = 1
            self.show_menu = True
            self.show_high_scores = False
            self.start_game = False
        elif not self.is_running:
            is_main_menu_and_index[0] = 3
        else:
            is_main_menu_and_index[0] = 0

        return is_main_menu_and_index
