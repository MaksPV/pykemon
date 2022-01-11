import pygame
import os
import sys

from funcs import load_image, load_level

tile_images = {
    'empty': load_image('grass.png'),
    'wall': load_image('wall.png'),
    'box': load_image('box.png'),
    "win": load_image('win.png'),
    "player": load_image('mario.png')
}

tile_width = tile_height = 50

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
cursor_group = pygame.sprite.Group()

class Cursor(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(cursor_group, all_sprites)
        self.image = load_image('cursor.png', -1)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def move(self, x, y):
        x, y = x * tile_width, y * tile_height
        self.rect.x = (self.rect.x + x) % width
        self.rect.y = (self.rect.y + y) % height


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.tile_type = tile_type
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def change(self):
        types = list(tile_images)
        self.tile_type = types[(types.index(self.tile_type) + 1) % len(types)]
        self.image = tile_images[self.tile_type]

def editor(screen):
    cursor = Cursor(0, 0)

    for x in range(width // tile_width):
        for y in range(height // tile_height):
            Tile("empty", x, y)

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sprite = pygame.sprite.spritecollideany(cursor, tiles_group)
                    if sprite != None:
                        sprite.change()
                if event.key == pygame.K_UP:
                    cursor.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    cursor.move(0, 1)
                if event.key == pygame.K_LEFT:
                    cursor.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    cursor.move(1, 0)
        clock.tick(25)
        screen.fill((0, 0, 0))
        tiles_group.draw(screen)
        cursor_group.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('mario')
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)

    editor(screen)