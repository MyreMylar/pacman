import pygame
from pygame.locals import *

from game.ui_text_button import UTTextButton


class HighScoreScreen:

    def __init__(self, fonts, high_score_table):

        self.high_score_table = high_score_table
        self.fonts = fonts
        self.show_menu = False
        self.show_high_scores = True

        self.background_image = pygame.image.load("images/menu_background.png")

        self.back_to_menu_button = UTTextButton([325, 550, 150, 35], "Back to Menu", fonts, 1)

        self.is_running = True
        
    def run(self, screen, background, screen_data):
        is_main_menu_and_index = [0, 0]
        for event in pygame.event.get():
            self.back_to_menu_button.handle_input_event(event)
            
            if event.type == QUIT:
                self.is_running = False

        self.back_to_menu_button.update()
        
        if self.back_to_menu_button.was_pressed():
            self.show_high_scores = False
            self.show_menu = True

        screen.blit(background, (0, 0))  # draw the background
        
        title_text = self.fonts[0].render('High Scores', True, pygame.Color("#FFFF00"))
        title_text_rect = title_text.get_rect(centerx=screen_data.screen_size[0] / 2)
        title_text_rect.y = 40
        screen.blit(title_text, title_text_rect)

        for index, high_score in enumerate(self.high_score_table.high_scores):
            text = str(index+1) + ". " + high_score.name.upper() + " - {:,}".format(high_score.score)
            score_text_render = self.fonts[1].render(text,
                                                     True, pygame.Color("#FFFFFF"))
            screen.blit(score_text_render, score_text_render.get_rect(x=screen_data.screen_size[0] * 0.4,
                                                                      y=170 + (35 * index)))
            
        self.back_to_menu_button.draw(screen)
                
        if self.show_high_scores:
            is_main_menu_and_index[0] = 2
            self.show_menu = False
            self.show_high_scores = True
        elif self.show_menu:
            is_main_menu_and_index[0] = 0
            self.show_menu = False
            self.show_high_scores = True
        elif not self.is_running:
            is_main_menu_and_index[0] = 3

        return is_main_menu_and_index


class HighScoreEntry:

    def __init__(self, screen, screen_data, fonts, high_score_table):
        self.screen = screen
        self.screen_data = screen_data
        self.high_score_table = high_score_table

        # noinspection PyArgumentList
        self.text_colour1 = pygame.color.Color('#FAB243')
        # noinspection PyArgumentList
        self.text_colour2 = pygame.color.Color('#FFFFFF')
        self.fonts = fonts

        self.current_string = ""
    
        self.should_save_new_high_score = False

    def display(self, background):

        self.screen.blit(background, (0, 0))  # draw the background

        title_text = self.fonts[0].render('High Score!', True, self.text_colour1)
        title_text_rect = title_text.get_rect(centerx=self.screen_data.screen_size[0] / 2)
        title_text_rect.y = 100
        self.screen.blit(title_text, title_text_rect)

        select_char_text_render = self.fonts[1].render("Enter name: " + self.current_string.upper(),
                                                       True, self.text_colour2)
        self.screen.blit(select_char_text_render,
                         select_char_text_render.get_rect(x=self.screen_data.screen_size[0] * 0.38,
                                                          y=200))

        press_any_key_text_render = self.fonts[1].render("Press enter to confirm", True, self.text_colour2)
        self.screen.blit(press_any_key_text_render,
                         press_any_key_text_render.get_rect(centerx=self.screen_data.screen_size[0] / 2,
                                                            centery=(self.screen_data.screen_size[1] * 0.9)))

    def update(self, player_score):
        output_game_state = "text_entry"
        for event in pygame.event.get():
            if event.type == KEYDOWN: 
                if event.key == K_BACKSPACE:
                    self.current_string = self.current_string[0:-1]
                elif event.key == K_RETURN:
                    self.should_save_new_high_score = True
                    output_game_state = "title_screen"
                elif len(self.current_string) < 3:
                    if event.key == K_MINUS:
                        self.current_string += "_"
                    elif 97 <= event.key <= 122:
                        self.current_string += chr(event.key)

        if self.should_save_new_high_score:
            self.high_score_table.add_new_high_score(self.current_string, player_score)

        return output_game_state
