import pygame
import os
import sys
import yaml

pygame.init()
pygame.display.set_caption('Склад 12')
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


# Функция для загрузки изображений
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


# Функция для загрузки уровней
def load_level(filename):
    fullname = "data/levels/" + filename

    with open(fullname, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# Изображения
tile_images = {
    'empty': load_image('grass.png'),
    'wall': load_image('wall.png'),
    'box': load_image('box.png'),
    "win": load_image('win.png'),
    "player": load_image('pika.png')
}

player_image = tile_images["player"]
tile_width = tile_height = 50


# Класс курсора для редактора
class Cursor(pygame.sprite.Sprite):
    # Инициализация
    def __init__(self, pos_x, pos_y):
        super().__init__(cursor_group, all_sprites)
        self.image = load_image('cursor.png', -1)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    # Движение
    def move(self, x, y):
        x, y = x * tile_width, y * tile_height
        self.rect.x = (self.rect.x + x) % width
        self.rect.y = (self.rect.y + y) % height


# Класс тайла
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        # Определение, занесение в нужную группу
        if tile_type == "wall":
            wall_group.add(self)
        elif tile_type == "win":
            win_group.add(self)

    # Смена типа тайла
    def change(self):
        types = list(tile_images)
        self.tile_type = types[(types.index(self.tile_type) + 1) % len(types)]
        self.image = tile_images[self.tile_type]


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.frames = dict()
        self.cut_sheet(load_image("pikachu.png"), 2, 4)
        self.cur_frame = 0
        self.last_step = (1, 0)
        self.image = self.frames[self.last_step][self.cur_frame]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    # Режем изображение спрайта
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        frames = list()
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

        self.frames = {(0, 1): (frames[0], frames[1]),
                       (0, -1): (frames[6], frames[7]),
                       (1, 0): (frames[4], frames[5]),
                       (-1, 0): (frames[2], frames[3])
                       }

    # Обновляем спрайт
    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames[(0, 1)])
        self.image = self.frames[self.last_step][self.cur_frame]

    # Двигаемся
    def move(self, x, y):
        self.last_step = x, y
        x, y = x * tile_width, y * tile_height
        x1, y1 = self.rect.move(x, y)[0] // tile_width, self.rect.move(x, y)[1] // tile_height
        # Если находим ящик на месте следующего положения, то пытаемся толкнуть
        for i in box_group:
            if x1 == i.x and y1 == i.y:
                i.move(x // tile_width, y // tile_height)
        last_rect = self.rect
        self.rect = self.rect.move(x, y)
        # Если будет столкновение с стеной и ящиком или выйдет за пределы экрана, то возвращаем предыдущее положение
        if any([pygame.sprite.spritecollideany(self, i) for i in (wall_group, box_group)]) or not (
                0 <= self.rect.x < width) or not (0 <= self.rect.y < height):
            self.rect = last_rect


# Класс ящика
class Box(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(box_group, all_sprites)
        self.image = tile_images["box"]
        self.x, self.y = pos_x, pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    # Движение
    def move(self, x, y):
        x_pos, y_pos = x, y
        x, y = x * tile_width, y * tile_height
        last_rect = self.rect
        self.rect = self.rect.move(x, y)
        # Если будет столкновение с стеной и ящиком или выйдет за пределы экрана, то возвращаем предыдущее положение
        if pygame.sprite.spritecollideany(self, wall_group) or \
                len(pygame.sprite.spritecollide(self, box_group, None)) > 1 or not (
                0 <= self.rect.x < width) or not (0 <= self.rect.y < height):
            self.rect = last_rect
        # Иначе обновляем координаты согласно клеточному полю
        else:
            self.x += x_pos
            self.y += y_pos


# Создаём уровень из списка
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


# Создаём список из редактора
def generate_level_from_editor(tile_group):
    dict_to_sym = {"wall": "#", "win": "!", "player": "@", "box": "$", "empty": "."}
    map_ = [["." for _ in range(width // tile_width)] for _ in range(height // tile_height)]
    for i in tile_group:
        x = i.rect.x // tile_width
        y = i.rect.y // tile_height
        symbol = dict_to_sym[i.tile_type]
        map_[y][x] = symbol
    return map_


# Редактор уровня
def editor(screen):
    cursor = Cursor(0, 0)

    # Заполняем экран тайлами
    for x in range(width // tile_width):
        for y in range(height // tile_height):
            Tile("empty", x, y)

    running = True
    clock = pygame.time.Clock()
    # Основной цикл
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                # Если нажата Escape, то завершаем функцию и возвращаем список
                if event.key == pygame.K_ESCAPE:
                    # Отрисовываем полупрозрачный прямоугольник
                    rectangle = pygame.surface.Surface((width // 6 + width // 2, height // 2 + height // 8))
                    rectangle.set_alpha(200)
                    rectangle.fill((255, 255, 255))
                    screen.blit(rectangle, (width // 6, height // 6))

                    # Определяем шрифты
                    font = pygame.font.Font(None, 110)
                    font2 = pygame.font.Font(None, 48)

                    # Рендерим тексты
                    save_text = font.render("Сохранить?", True, (0, 0, 128))
                    yes_text = font2.render(f"Если да, нажмите ENTER,", True, (0, 0, 0))
                    no_text = font2.render(f"Иначе любую клавишу", True, (0, 0, 0))

                    # Отрисовываем вопрос
                    place = save_text.get_rect(center=(width // 2, height // 2 - 90))
                    screen.blit(save_text, place)

                    # Отрисовываем пояснение
                    place = yes_text.get_rect(center=(width // 2, height // 2))
                    screen.blit(yes_text, place)
                    place = no_text.get_rect(center=(width // 2, height // 2 + 48))
                    screen.blit(no_text, place)

                    # Обновляем экран
                    pygame.display.flip()

                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                exit()
                            elif event.type == pygame.KEYDOWN:
                                # Если нажат Enter, то сохраняем
                                if event.key == pygame.K_RETURN:
                                    return generate_level_from_editor(tiles_group)
                                # Иначе нет
                                else:
                                    return None
                # Если пробел, то меняем тип тайла под курсором
                elif event.key == pygame.K_SPACE:
                    sprite = pygame.sprite.spritecollideany(cursor, tiles_group)
                    if sprite is not None:
                        sprite.change()
                # Движение курсора
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
        # Изображаем всё на экране
        tiles_group.draw(screen)
        cursor_group.draw(screen)
        pygame.display.flip()


# Функция запуска уровня
def runner(screen, level):
    global all_sprites, tiles_group, wall_group, box_group, win_group, player_group

    # Получаем уровень
    player, level_x, level_y = generate_level(level)
    if player is None:
        return None

    font = pygame.font.Font(None, 36)
    start_time = pygame.time.get_ticks()
    prev_buttons = list()

    running = True
    last_pressed = 0
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                # Если нанжата Escape, то чистим переменные и выходим
                if event.key == pygame.K_ESCAPE:
                    clear_vars()
                    return None
                # Если нажат пробел, сбрасываем уровень
                elif event.key == pygame.K_SPACE:
                    clear_vars()
                    start_time = pygame.time.get_ticks()
                    player, level_x, level_y = generate_level(level)

        # Движение
        buttons = pygame.key.get_pressed()
        if pygame.time.get_ticks() - last_pressed > 250 or prev_buttons != list(buttons):
            last_pressed = pygame.time.get_ticks()
            if buttons[pygame.K_UP]:
                player.move(0, -1)
            elif buttons[pygame.K_DOWN]:
                player.move(0, 1)
            if buttons[pygame.K_LEFT]:
                player.move(-1, 0)
            elif buttons[pygame.K_RIGHT]:
                player.move(1, 0)
            prev_buttons = list(buttons)

        # Отрисовываем тайлы
        tiles_group.draw(screen)
        player_group.update()
        player_group.draw(screen)
        box_group.draw(screen)

        # Рисуем секундомер
        timer_text = font.render(f"Время: {(pygame.time.get_ticks() - start_time) // 1000} сек.",
                                 True, (255, 255, 255), (0, 128, 0))
        screen.blit(timer_text, (10, 10))

        clock.tick(5)

        # Если все ящики на месте, то победа
        if len(pygame.sprite.groupcollide(box_group, win_group, None, None)) == len(win_group):
            # Отрисовываем полупрозрачный прямоугольник
            rectangle = pygame.surface.Surface((width // 6 + width // 2, height // 2 + height // 8))
            rectangle.set_alpha(200)
            rectangle.fill((255, 255, 255))
            screen.blit(rectangle, (width // 6, height // 6))

            time_ = (pygame.time.get_ticks() - start_time) // 1000

            # Определяем шрифты
            font = pygame.font.Font(None, 110)
            font2 = pygame.font.Font(None, 50)
            font3 = pygame.font.Font(None, 25)

            # Рендерим тексты
            win_text = font.render("Победа!", True, pygame.Color("orange"))
            time_text = font2.render(f"Время: {time_} секунд(ы)", True, (0, 0, 0))
            press_text = font3.render("Нажмите любую клавишу, чтобы выйти", True, (0, 0, 0))

            # Отрисовываем победу!
            place = win_text.get_rect(center=(width // 2, height // 2 - 90))
            screen.blit(win_text, place)

            # Отрисовываем время
            place = time_text.get_rect(center=(width // 2, height // 2))
            screen.blit(time_text, place)

            # Отрисовываем текст о выходе
            place = press_text.get_rect(center=(width // 2, height // 2 + 90))
            screen.blit(press_text, place)

            # Обновляем экран
            pygame.display.flip()

            # Звук победы
            sound = pygame.mixer.Sound("data/sounds/win.ogg")
            sound.play()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit()
                    # Если нажата кнопка, выходим
                    elif event.type == pygame.KEYDOWN:
                        return time_

        pygame.display.flip()


# Чистим все переменные
def clear_vars():
    global all_sprites, tiles_group, wall_group, box_group, win_group, player_group, cursor_group
    for i in (all_sprites, tiles_group, wall_group, box_group, win_group, player_group, cursor_group):
        i.empty()


# Сохраняем уровень в файл
def save_level(level, name):
    new = level.copy()
    for k, i in enumerate(level):
        new[k] = "".join(i)
    new = "\n".join(new)
    with open("data/levels/" + name, "w") as f:
        f.write(new)
        f.close()


# Меню
def menu(screen):
    # Загружаем рекроды
    scores = dict()
    try:
        with open("scores.yml", "r") as file:
            scores = yaml.load(file, yaml.Loader)
            file.close()
    except:
        # Если нет их, создаём новый файл
        open("scores.yml", "w")
    if scores is None:
        scores = dict()

    # Определяем шрифты
    font = pygame.font.Font(None, 110)
    font2 = pygame.font.Font(None, 50)
    font3 = pygame.font.Font(None, 25)

    # Рендерим статичные тексты
    text1 = font.render("СКЛАД 12", True, (0, 100, 50))
    choose_lvl_text = font2.render("Выберите уровень", True, (0, 0, 0))
    editor_text = font3.render("Нажмите E, чтобы открыть редактор", True, (0, 0, 0))

    background = load_image("background.png")
    running = True

    # Загружаем список уровней
    files = os.listdir("data/levels")
    files = sorted(files, key=lambda x: int(x[:-4]))
    now_file = files[0]

    # Фоновая музыка
    pygame.mixer.music.load('data/sounds/menu.mp3')
    pygame.mixer.music.play(-1, 0, 5)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # по нажатию на стрелки меняем выбранный уровень
                if event.key == pygame.K_RIGHT:
                    now_file = files[(files.index(now_file) + 1) % len(files)]
                elif event.key == pygame.K_LEFT:
                    now_file = files[(files.index(now_file) - 1) % len(files)]
                # По нажатию на пробел запускаем уровень
                elif event.key == pygame.K_SPACE:
                    clear_vars()
                    score = runner(screen, load_level(now_file))
                    # Сохраняем рекорд
                    if score is not None:
                        # Сравниваем
                        if now_file not in scores or score < scores[now_file]:
                            scores[now_file] = score
                        with open("scores.yml", "w") as file:
                            file.write(yaml.dump(scores))
                            file.close()
                # По нажатию на E запускаем редактор
                elif event.key == pygame.K_e:
                    clear_vars()
                    level = editor(screen)
                    # Если уровень не None, то ок
                    if level is not None:
                        # берём название
                        if int(files[-1][:-4]) >= 1000:
                            name = int(files[-1][:-4]) + 1
                            name = str(name) + ".txt"
                        else:
                            name = "1000.txt"
                        # Сохраняем
                        save_level(level, name)
                        # Обновляем список уровней
                        files = os.listdir("data/levels")
                        files = sorted(files, key=lambda x: int(x[:-4]))

        # Отрисовываем фон
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))

        # Отрисовываем полупрозрачный прямоугольник
        rectangle = pygame.surface.Surface((width // 6 + width // 2, height // 2 + height // 10))
        rectangle.set_alpha(200)
        rectangle.fill((255, 255, 255))
        screen.blit(rectangle, (width // 6, height // 10))

        # Отрисовываем название
        place = text1.get_rect(center=(width // 2, height // 4))
        screen.blit(text1, place)

        # Отрисовываем выбранный уровень
        text_now_level = font2.render(now_file[:-4], True, (0, 0, 0))
        place = text_now_level.get_rect(center=(width // 2, height // 2))
        screen.blit(text_now_level, place)

        # Отрисовываем статичный текст выбора уровня
        place = choose_lvl_text.get_rect(center=(width // 2, height // 2 - 45))
        screen.blit(choose_lvl_text, place)

        # Отрисовываем рекорд
        if now_file not in scores:
            record = "-"
        else:
            record = scores[now_file]
        record_text = font3.render(f"Рекорд: {record} секунд(ы)", True, (0, 0, 0))
        place = record_text.get_rect(center=(width // 2, height // 2 + 45))
        screen.blit(record_text, place)

        # Отрисовываем текст о редакторе
        place = editor_text.get_rect(center=(width // 2, height // 2 + 90))
        screen.blit(editor_text, place)

        pygame.display.flip()


if __name__ == "__main__":
    menu(screen)
