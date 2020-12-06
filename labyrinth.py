import pygame

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 480, 480
FPS = 15
TILE_SIZE = 32
ENEMY_EVENT_TYPE = pygame.USEREVENT + 1


class Enemy:
    def __init__(self, pos):
        self.x, self.y = pos
        self.delay = 100
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)

    def get_pos(self):
        return self.x, self.y

    def set_pos(self, pos):
        self.x, self.y = pos

    def render(self, screen):
        center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, (255, 0, 255), center, TILE_SIZE // 2)


class Hero:
    def __init__(self, pos):
        self.x, self.y = pos

    def get_pos(self):
        return self.x, self.y

    def set_pos(self, pos):
        self.x, self.y = pos

    def render(self, screen):
        center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, (255, 255, 255), center, TILE_SIZE // 2)


class Labyrinth:
    def __init__(self, filename, free_tiles, finish_tile):
        self.map = []
        with open(f'{filename}') as f:
            for line in f:
                self.map.append(list(map(int, line.split())))
            self.height = len(self.map)
            self.width = len(self.map[0])
            self.tile_size = TILE_SIZE
            self.free_tiles = free_tiles
            self.finish_tile = finish_tile

    def render(self, screen):
        colors = {0: (0, 0, 0), 1: (120, 120, 120), 2: (50, 50, 50)}
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                screen.fill(colors[self.get_tile_id((x, y))], rect)

    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    def is_free(self, pos):
        return self.get_tile_id(pos) in self.free_tiles

    def find_step(self, start, target):
        INF = 1000
        x, y = start
        distanse = [[INF] * self.width for _ in range(self.height)]
        distanse[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        quene = [(x, y)]
        while quene:
            x, y = quene.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width and 0 <= next_y < self.height and self.is_free((next_x, next_y)) and \
                        distanse[next_y][next_x] == INF:
                    distanse[next_y][next_x] = distanse[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    quene.append((next_x, next_y))

        x, y = target
        if distanse[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y


class Game:
    def __init__(self, lab, hero, enemy):
        self.labyrinth = lab
        self.hero = hero
        self.enemy = enemy

    def render(self, screen):
        self.labyrinth.render(screen)
        self.hero.render(screen)
        self.enemy.render(screen)

    def update_hero(self):
        next_x, next_y = self.hero.get_pos()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.labyrinth.is_free((next_x, next_y)):
            self.hero.set_pos((next_x, next_y))

    def move_enemy(self):
        next_pos = self.labyrinth.find_step(self.enemy.get_pos(), self.hero.get_pos())
        self.enemy.set_pos(next_pos)

    def check_win(self):
        return self.labyrinth.get_tile_id(self.hero.get_pos()) == self.labyrinth.finish_tile

    def check_lose(self):
        return self.hero.get_pos() == self.enemy.get_pos()


def show_mes(screen, mes):
    font = pygame.font.Font(None, 40)
    text = font.render(mes, 1, (255, 255, 255))
    text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
    text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (200, 0, 230), (text_x - 10, text_y - 10, text_w + 20, text_h + 20), 0)
    screen.blit(text, (text_x, text_y))


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    labyrinth = Labyrinth('simple_map.txt', [0, 2], 2)
    hero = Hero((7, 7))
    enemy = Enemy((7, 1))
    game = Game(labyrinth, hero, enemy)

    clock = pygame.time.Clock()
    running = True
    over = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == ENEMY_EVENT_TYPE and not over:
                game.move_enemy()
        if not over:
            game.update_hero()
        screen.fill((0, 0, 0))
        game.render(screen)
        if game.check_win():
            over = True
            show_mes(screen, "YOU WON!")
        if game.check_lose():
            over = True
            show_mes(screen, "YOU LOSE!")
        pygame.display.flip()
        clock.tick(FPS)
    pygame.display.quit()


if __name__ == '__main__':
    main()
