import pygame


class Fruit:
    def __init__(self, level_num, all_pill_sprites, start_location):

        self.all_pill_sprites = all_pill_sprites
        self.fruit_tile_table = self.load_tile_table("images/fruits.png", 16, 16, 1, 16, 1)
        self.fruit_to_pick = 0
        if level_num > 16:
            self.fruit_to_pick = 15
        else:
            self.fruit_to_pick = level_num - 1
        self.fruit_image = self.fruit_tile_table[0][self.fruit_to_pick]
        self.fruit_sprite = pygame.sprite.Sprite()      
                
        self.fruit_sprite.rect = self.fruit_image.get_rect()  
        self.fruit_sprite.rect.center = start_location

        self.position = [float(self.fruit_sprite.rect.center[0]), float(self.fruit_sprite.rect.center[1])]
        self.fruit_sprite.image = self.fruit_image
        self.all_pill_sprites.add(self.fruit_sprite)

        self.rect = self.fruit_sprite.rect
        self.should_die = False

        self.score = ((level_num + level_num) * 100) - 100

        self.fruit_life_time = 10.0

    def should_it_die(self, dt):
        self.fruit_life_time -= dt
        if self.fruit_life_time <= 0.0:
            self.should_die = True
        if self.should_die:
            self.all_pill_sprites.remove(self.fruit_sprite)
        return self.should_die

    @staticmethod
    def load_tile_table(filename, width, height, tile_spacing, num_x_tiles, num_y_tiles):
        image = pygame.image.load(filename).convert_alpha()
        tile_table = []
        for tile_y in range(0, num_y_tiles):
            line = []
            tile_table.append(line)
            for tile_x in range(0, num_x_tiles):
                rect = (tile_x * width + tile_spacing + tile_spacing * tile_x,
                        tile_y * height + tile_spacing + tile_spacing * tile_y, width, height)
                line.append(image.subsurface(rect))
        return tile_table
