import pygame, sys
import random
import time
from functools import partial

pygame.init() 
FPS = 60
FramePerSec = pygame.time.Clock()

# Predefined some colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Screen information
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Game")

SCORE = 0
LEVEL = 1
SNAKE_INITIAL_LENGTH = 75
appState = dict(
    speed=1,
    RUN=True,
    window_size=SNAKE_INITIAL_LENGTH
)

font_small = pygame.font.SysFont("Verdana", 20)
font = pygame.font.SysFont("Verdana", 60)

snakeHeadImage = pygame.image.load("snakeout.png")
fruitImage = pygame.image.load("appleout.png")


# Try to use State pattern
class SnakeHead(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__() 
        self.image = snakeHeadImage
        self.rect = self.image.get_rect(center=(x, y))
        self.current_state = 'DOWN'
        self.tail = self

    def change_direction(self):
        temp_state = self.current_state
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_UP]:
            if self.current_state != "DOWN":
                self.image = pygame.transform.rotate(snakeHeadImage, 180)
                self.current_state = 'UP'
        if pressed_keys[pygame.K_DOWN]:
            if self.current_state != 'UP':
                self.image = pygame.transform.rotate(snakeHeadImage, 0)
                self.current_state = 'DOWN'

        if pressed_keys[pygame.K_LEFT]:
            if self.current_state != 'RIGHT':
                self.image = pygame.transform.rotate(snakeHeadImage, -90)
                self.current_state = 'LEFT'

        if pressed_keys[pygame.K_RIGHT]:
            if self.current_state != 'LEFT':
                self.image = pygame.transform.rotate(snakeHeadImage, 90)
                self.current_state = 'RIGHT'

        # if temp_state != self.current_state:
        self.leave_point()

    def leave_point(self):
        cur_center = self.rect.center
        movement = get_movement(self.current_state)
        # new_coords = (cur_center[0] - (get_sign(movement[0]) * self.rect.width // 2),
        #               cur_center[1] - (get_sign(movement[1]) * self.rect.height // 2))
        # point = CollisionPoint(new_coords[0], new_coords[1], self.current_state)
        point = CollisionPoint(cur_center[0], cur_center[1], self.current_state)

        collision_points.add(point)
        bodyWindow.append(point)

    def move(self):

        self.rect.move_ip(get_movement(self.current_state))
        # self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        # self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))
        if self.rect.x > SCREEN_WIDTH or self.rect.x < 0 or \
           self.rect.y > SCREEN_WIDTH or self.rect.y < 0:
            game_over_handler()


class Fruit(pygame.sprite.Sprite):
    def __init__(self, lifetime=5, weight=1):
        super().__init__() 
        self.image = fruitImage
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40,SCREEN_WIDTH-40),random.randint(40, SCREEN_HEIGHT-40))

        self.appear_time = pygame.time.get_ticks()
        self.lifetime = lifetime # lifetime in ms

        self.weight = weight

    def update(self):
        if pygame.time.get_ticks() - self.appear_time > self.lifetime:
            self.kill()


class CollisionPoint(pygame.sprite.Sprite):
    def __init__(self, x, y, state):
        super().__init__()
        self.image = pygame.Surface((5, 5), pygame.SRCALPHA)  # Small point
        self.image.fill((0, 255, 0, 255))
        self.change_state = state
        self.rect = self.image.get_rect(center=(x, y))


def game_over_handler():
    DISPLAYSURF.fill(RED)
    DISPLAYSURF.blit(game_over, (60,250))
    pygame.display.update() 
    for sprite in all_sprites:
        sprite.kill()
    appState['RUN'] = False


def get_sign(n):
    return (n > 0) - (n < 0)


def get_movement(state):
    match state:
        case 'UP':
            return (0, -appState.get('speed'))
        case 'DOWN':
            return (0, appState.get('speed'))
        case 'RIGHT':
            return (appState.get('speed'), 0)
        case 'LEFT':
            return (-appState.get('speed'), 0)

game_over = font.render("Game Over", True, 'white')

S1 = SnakeHead(*DISPLAYSURF.get_rect().center)
fruits = pygame.sprite.Group()
Sbodies = pygame.sprite.Group()

collision_points = pygame.sprite.Group()
bodyWindow = list()

all_sprites = pygame.sprite.Group()
all_sprites.add(S1)
all_sprites.add(fruits)

CREATE_FRUIT = pygame.USEREVENT + 1
pygame.time.set_timer(CREATE_FRUIT, 1500)


while appState['RUN']:
    for event in pygame.event.get():              
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == CREATE_FRUIT and len(fruits) < 5:
            lifetime = random.randint(3000, 5000)
            weight = random.randint(1, 5)
            fruit = Fruit(lifetime, weight)
            fruits.add(fruit)
    DISPLAYSURF.fill('black')

    DISPLAYSURF.blit(S1.image, S1.rect)
    S1.move()
    S1.change_direction()

    score = font_small.render(str(SCORE), True, 'yellow')
    DISPLAYSURF.blit(score, (SCREEN_WIDTH - 30,10))

    bodyWindow = bodyWindow[-appState.get('window_size'):]

    collision_points.draw(DISPLAYSURF)

    if pygame.sprite.spritecollideany(S1, fruits):
        # SCORE += random.randint(1, 3)
        appState['window_size'] = SCORE*5 + SNAKE_INITIAL_LENGTH

    for point in collision_points:
        if point not in bodyWindow:
            point.kill()

    for collide_point in bodyWindow[:-50]:
        # if pygame.sprite.collide_rect(collide_point, S1):
        #     game_over_handler()
        if collide_point.rect.collidepoint(S1.rect.center):
            game_over_handler()

    for fruit in fruits:
        if pygame.sprite.collide_rect(fruit, S1):
            SCORE += fruit.weight
            fruit.kill()
        fruit.update()
        DISPLAYSURF.blit(fruit.image, fruit.rect)

    # if pygame.sprite.spritecollideany(S1, Sbodies): game_over_handler()
    LEVEL = SCORE // 10 + 1

    appState['speed'] = LEVEL
    level_display = font_small.render(f"Level:{LEVEL:<3}", True, 'green')
    DISPLAYSURF.blit(level_display, (30, 10))

    pygame.display.update()
    FramePerSec.tick(FPS)

time.sleep(2)
pygame.quit()
sys.exit()
