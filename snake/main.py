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


class SnakeBody(pygame.sprite.Sprite):
    def __init__(self, x, y, state, radius=10):
        super().__init__()
        self.radius = radius
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, 'green', (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.current_state = state

    def change_direction(self, point):
        self.current_state = point.change_state

    def move(self):

        self.rect.move_ip(get_movement(self.current_state))
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

defaultBody = partial(SnakeBody, 25, *DISPLAYSURF.get_rect().center)
snakeHeadImage = pygame.image.load("snakeout.png")
SCORE = 0
appState = dict(
    speed=1,
    RUN=True
)
font_small = pygame.font.SysFont("Verdana", 20)

font = pygame.font.SysFont("Verdana", 60)
game_over = font.render("Game Over", True, 'white')


# Try to use State pattern
class SnakeHead(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__() 
        self.image = snakeHeadImage
        self.rect = self.image.get_rect(center=(x, y))
        self.current_state = 'DOWN'
        self.tail = self

    def change_direction(self):
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

        cur_center = self.rect.center
        point = CollisionPoint(cur_center[0], cur_center[1], self.current_state)
        collision_points.add(point)

    def move(self):

        self.rect.move_ip(get_movement(self.current_state))
        # self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        # self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))
        if self.rect.x > SCREEN_WIDTH or self.rect.x < 0 or \
           self.rect.y > SCREEN_WIDTH or self.rect.y < 0:
            game_over_handler()


class Fruit(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("appleout.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40,SCREEN_WIDTH-40),random.randint(40, SCREEN_HEIGHT-40))


class CollisionPoint(pygame.sprite.Sprite):
    def __init__(self, x, y, state):
        super().__init__()
        self.image = pygame.Surface((6, 6), )  # Small point
        self.image.fill(RED)
        self.change_state = state
        self.rect = self.image.get_rect(center=(x, y))


S1 = SnakeHead(*DISPLAYSURF.get_rect().center)
fruits = pygame.sprite.Group()
Sbodies = pygame.sprite.Group()

collision_points = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
all_sprites.add(S1)
all_sprites.add(fruits)

CREATE_FRUIT = pygame.USEREVENT + 1
pygame.time.set_timer(CREATE_FRUIT, 1500)


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


while appState['RUN']:
    for event in pygame.event.get():              
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == CREATE_FRUIT and len(fruits) < 5:
            fruit = Fruit()
            fruits.add(fruit)
    DISPLAYSURF.fill('black')

    DISPLAYSURF.blit(S1.image, S1.rect)
    S1.move()
    S1.change_direction()

    score = font_small.render(str(SCORE), True, 'yellow')
    DISPLAYSURF.blit(score, (SCREEN_WIDTH - 30,10))

    collision_points.draw(DISPLAYSURF)

    if pygame.sprite.spritecollideany(S1, fruits):
        SCORE += 1
        snakeBodiesNeeded = SCORE // 3 + 1
        if len(Sbodies) < snakeBodiesNeeded:
            last_node = S1.tail
            last_coords = last_node.rect.center
            movement = get_movement(last_node.current_state)
            new_coords = (last_coords[0] - (get_sign(movement[0]) * last_node.rect.width),
                          last_coords[1] - (get_sign(movement[1]) * last_node.rect.height))
            sbody = SnakeBody(*new_coords, last_node.current_state)
            Sbodies.add(sbody)
            S1.tail = sbody

    for i, body in enumerate(Sbodies):
        collided_point = pygame.sprite.spritecollideany(body, collision_points)
        if collided_point: body.change_direction(collided_point)
        DISPLAYSURF.blit(body.image, body.rect)
        body.move()

    last_node_checked = pygame.sprite.spritecollideany(S1.tail, collision_points)
    if last_node_checked: last_node_checked.kill()

    for fruit in fruits:
        if pygame.sprite.collide_rect(fruit, S1):
            fruit.kill()
        DISPLAYSURF.blit(fruit.image, fruit.rect)

    # if pygame.sprite.spritecollideany(S1, Sbodies): game_over_handler()

    appState['speed'] = SCORE // 10 + 1

    pygame.display.update()
    FramePerSec.tick(FPS)

time.sleep(2)
pygame.quit()
sys.exit()