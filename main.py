import pygame
import os
import sys

pygame.init()
pygame.display.set_caption('mario')
size = width, height = 800, 600
screen = pygame.display.set_mode(size)

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
win_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
cursor_group = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    fullname = "data/levels/" + filename

    with open(fullname, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'empty': load_image('grass.png'),
    'wall': load_image('wall.png'),
    'box': load_image('box.png'),
    "win": load_image('win.png'),
    "player": load_image('mario.png')
}

player_image = tile_images["player"]
tile_width = tile_height = 50


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
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        if tile_type == "wall":
            wall_group.add(self)
        elif tile_type == "win":
            win_group.add(self)

    def change(self):
        types = list(tile_images)
        self.tile_type = types[(types.index(self.tile_type) + 1) % len(types)]
        self.image = tile_images[self.tile_type]


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
                exit()
            elif event.type == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sprite = pygame.sprite.spritecollideany(cursor, tiles_group)
                    if sprite is not None:
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


def runner(screen, level):
    global all_sprites, tiles_group, wall_group, box_group, win_group, player_group

    player, level_x, level_y = generate_level(load_level(level))

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    all_sprites = pygame.sprite.Group()
                    tiles_group = pygame.sprite.Group()
                    wall_group = pygame.sprite.Group()
                    box_group = pygame.sprite.Group()
                    win_group = pygame.sprite.Group()
                    player_group = pygame.sprite.Group()
                    player, level_x, level_y = generate_level(load_level(level))
                if event.key == pygame.K_UP:
                    player.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    player.move(0, 1)
                if event.key == pygame.K_LEFT:
                    player.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    player.move(1, 0)


        if len(pygame.sprite.groupcollide(box_group, win_group, None, None)) == len(win_group):
            break

        clock.tick(5)
        tiles_group.draw(screen)
        player_group.draw(screen)
        box_group.draw(screen)
        pygame.display.flip()


editor(screen)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
