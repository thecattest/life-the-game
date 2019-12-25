import pygame
import os
import time
import json
import glob


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 20
        self.create_screen()
        self.started = 0
        self.speed = 200
        self.clock = pygame.time.Clock()
        self.last_tick = self.speed
        self.step = 0
        self.directory = 'populations'
        self.name = time.strftime('%d.%m.%Y', time.localtime())
        if os.path.exists(self.directory):
            self.name += '_' + str(len(glob.glob(os.path.join(self.directory, self.name + '*.json'))))

    def create_screen(self):
        global screen
        width = self.width * self.cell_size + self.left * 2
        height = self.height * self.cell_size + self.top * 3 + 40
        width = width if width > 420 else 420
        screen = pygame.display.set_mode((width, height))

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.create_screen()

    def save_progress(self):
        if not self.step:
            return
        path = self.get_path(self.name)
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        settings = [self.width, self.height, self.board, self.left, self.top, self.cell_size]
        with open(path, 'w') as file:
            json.dump(settings, file)

    def load_progress(self, fname):
        path = self.get_path(fname)
        if not os.path.exists(path):
            return
        self.name = fname
        with open(path) as file:
            settings = json.load(file)
            self.width, self.height, self.board, left, top, cell_size = settings
            self.set_view(left, top, cell_size)

    def get_path(self, name):
        path = os.path.join(self.directory, name + '.json')
        return path

    def render(self):
        self.last_tick += self.clock.tick()
        if self.last_tick < self.speed and self.started:
            return
        else:
            self.last_tick = 0
        if self.started:
            self.next_move()
        screen.fill((0, 0, 0))
        for i in range(self.height):
            for j in range(self.width):
                # координаты клетки
                x = j * self.cell_size + self.left
                y = i * self.cell_size + self.top
                # если 1, то белая вся клетка, если 0 - то только рамка
                alive = self.board[i][j]
                if alive:
                    pygame.draw.rect(screen, (255, 255, 255), (x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(screen, (255, 255, 255), (x, y, self.cell_size, self.cell_size), 1)
        pygame.display.flip()

    def next_move(self, number=0):
        new_field = [[0] * self.width for _ in range(self.height)]
        for i in range(self.height):
            for j in range(self.width):
                neighbours = self.get_neighbours(j, i)
                if self.board[i][j]:
                    if 2 <= neighbours <= 3:
                        new_field[i][j] = 1
                else:
                    if neighbours == 3:
                        new_field[i][j] = 1
        self.board = new_field
        self.step += 1
        if number > 1:
            self.next_move(number - 1)

    def get_neighbours(self, x, y):
        count = 0
        y_start = y - 1
        y_end = y + 2

        x_start = x - 1
        x_end = x + 2

        for i in range(y_start, y_end):
            for j in range(x_start, x_end):
                i %= self.height
                j %= self.width
                count += self.board[i][j]
        count -= self.board[y][x]
        return count

    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        # - border
        x -= self.left
        y -= self.top
        # если клик не по полю
        if not 0 <= x <= self.width * self.cell_size or not 0 <= y <= self.height * self.cell_size:
            return None
        # indexes
        i = y // self.cell_size
        j = x // self.cell_size
        return j, i

    def on_click(self, cell_coords):
        if cell_coords is None or self.started:
            return
        x, y = cell_coords
        self.board[y][x] = 1 - self.board[y][x]

    def get_click(self, event):
        if event.button == 1:
            cell = self.get_cell(event.pos)
            self.on_click(cell)
        elif event.button == 3:
            # включить или остановить
            self.started = 1 - self.started
        elif event.button == 4:
            self.speed += 100
        elif event.button == 5:
            self.speed -= 100
        else:
            # не моя проблема...
            pass


pygame.init()

life = Board(20, 20)
life.set_view(10, 10, 15)
# life.load_progress('25.12.2019_1')

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            life.save_progress()
        if event.type == pygame.MOUSEBUTTONDOWN:
            life.get_click(event)
        elif event.type == 2:
            life.started = 1 - life.started
    life.render()
