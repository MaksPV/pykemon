import pygame

from funcs import load_level, load_image

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        if tile_type == "wall":
            wall_group.add(self)
        elif tile_type == "win":
            win_group.add(self)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move(self, x, y):
        x, y = x * tile_width, y * tile_height
        x1, y1 = self.rect.move(x, y)[0] // tile_width, self.rect.move(x, y)[1] // tile_height,
        for i in box_group:
            if x1 == i.x and y1 == i.y:
                i.move(x // tile_width, y // tile_height)
        last_rect = self.rect
        self.rect = self.rect.move(x, y)
        if any([pygame.sprite.spritecollideany(self, i) for i in (wall_group, box_group)]):
            self.rect = last_rect


class Box(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(box_group, all_sprites)
        self.image = tile_images["box"]
        self.x, self.y = pos_x, pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def move(self, x, y):
        x_pos, y_pos = x, y
        x, y = x * tile_width, y * tile_height
        last_rect = self.rect
        self.rect = self.rect.move(x, y)
        if pygame.sprite.spritecollideany(self, wall_group) or \
                len(pygame.sprite.spritecollide(self, box_group, None)) > 1:
            self.rect = last_rect
        else:
            self.x += x_pos
            self.y += y_pos


def win():
    pass

def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                Tile('win', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '$':
                Tile('empty', x, y)
                Box(x, y)
            else:
                Tile('empty', x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def runner(screen, level):
    tile_images = {
        'wall': load_image('wall.png'),
        'empty': load_image('grass.png'),
        'box': load_image('box.png'),
        "win": load_image('win.png')
    }
    player_image = load_image('mario.png')

    tile_width = tile_height = 50

    # основной персонаж
    player = None

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    wall_group = pygame.sprite.Group()
    box_group = pygame.sprite.Group()
    win_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()

    player, level_x, level_y = generate_level(load_level(level))

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if len(pygame.sprite.groupcollide(box_group, win_group, None, None)) == len(win_group):
            win()
        buttons = pygame.key.get_pressed()
        if buttons[pygame.K_SPACE]:
            all_sprites = pygame.sprite.Group()
            tiles_group = pygame.sprite.Group()
            wall_group = pygame.sprite.Group()
            box_group = pygame.sprite.Group()
            win_group = pygame.sprite.Group()
            player_group = pygame.sprite.Group()
            player, level_x, level_y = generate_level(load_level("1.txt"))
        if buttons[pygame.K_UP]:
            player.move(0, -1)
        elif buttons[pygame.K_DOWN]:
            player.move(0, 1)
        if buttons[pygame.K_LEFT]:
            player.move(-1, 0)
        elif buttons[pygame.K_RIGHT]:
            player.move(1, 0)
        clock.tick(5)
        tiles_group.draw(screen)
        player_group.draw(screen)
        box_group.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('mario')
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)

    runner(screen, "1.txt")