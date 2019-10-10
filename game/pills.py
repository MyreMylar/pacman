import pygame


class BasePill:
    def __init__(self):
        self.is_large_pill = False

    def update_sprite(self, all_sprites):
        pass


class LargePill(BasePill):
    def __init__(self, start_pos, all_pill_sprites):
        
        super().__init__()
        self.imageName = "images/large_pill.png"
        self.original_pill_image = pygame.image.load(self.imageName).convert_alpha()
        self.pill_image = self.original_pill_image.copy()
        self.pill_sprite = pygame.sprite.Sprite()      
                
        self.pill_sprite.rect = self.pill_image.get_rect()  
        self.pill_sprite.rect.center = start_pos

        self.position = [float(self.pill_sprite.rect.center[0]), float(self.pill_sprite.rect.center[1])]
        self.pill_sprite.image = self.pill_image
        all_pill_sprites.add(self.pill_sprite)

        self.rect = self.pill_sprite.rect
        self.should_die = False

        self.is_large_pill = True

    def update_sprite(self, all_sprites):
        if self.should_die:
            all_sprites.remove(self.pill_sprite)


class Pill(BasePill):
    def __init__(self, start_pos, all_pill_sprites):
        
        super().__init__()
        self.imageName = "images/pill.png"
        self.original_pill_image = pygame.image.load(self.imageName).convert_alpha()
        self.pill_image = self.original_pill_image.copy()
        self.pill_sprite = pygame.sprite.Sprite()      
                
        self.pill_sprite.rect = self.pill_image.get_rect()  
        self.pill_sprite.rect.center = start_pos

        self.position = [float(self.pill_sprite.rect.center[0]), float(self.pill_sprite.rect.center[1])]
        self.pill_sprite.image = self.pill_image
        all_pill_sprites.add(self.pill_sprite)

        self.is_large_pill = False
        self.rect = self.pill_sprite.rect
        self.should_die = False

    def update_sprite(self, all_sprites):
        if self.should_die:
            all_sprites.remove(self.pill_sprite)
