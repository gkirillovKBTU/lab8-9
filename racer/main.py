import pygame, sys
import random
import time
 
pygame.init()
 
FPS = 60
FramePerSec = pygame.time.Clock()
 
# constant colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
 
# Screen information : width, height, and consts
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COIN_SCORE = 0
COIN_COUNTER = 0

# Fonts and text setting
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Load background image
background = pygame.image.load("AnimatedStreet.png")

# Create the main game window
DISPLAYSURF = pygame.display.set_mode((400,600))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")


# Enemy class for moving obstacles
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center=(random.randint(40,SCREEN_WIDTH-40),0) # Enemy start position

    def move(self):
        global SCORE, SPEED
        self.rect.move_ip(0,SPEED) # Enemy moves down the road with increasing speed
        if (self.rect.top > 600): # If it goes off the screen  reset position
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0) # Respawn at a new position


# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, weight=random.randint(1, 3)):
        super().__init__() 
        self.image = pygame.image.load("coinmod.png")
        self.rect = self.image.get_rect()
        self.rect.center=(random.randint(40,SCREEN_WIDTH-40),0) 
        self.weight = weight # random weight to each coin

    def move(self):
        global SCORE
        self.rect.move_ip(0,10)
        if (self.rect.top > 600):
            self.start_begin() # Reset coins position when ioff screen

    def start_begin(self):
        self.weight = random.randint(1, 3)
        self.rect.top = 0
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0) # Coin respawns


# Player class f
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520) # Player's starting position

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > 0: # Check left boundary
            if pressed_keys[pygame.K_LEFT]:
                self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH: # Check right boundary      
            if pressed_keys[pygame.K_RIGHT]:
                self.rect.move_ip(5, 0)

# Initiating play and enemies
P1 = Player()
E1 = Enemy()
coin_generator = Coin()

# grouping enemy and coins
enemies = pygame.sprite.Group()
enemies.add(E1)
coins = pygame.sprite.Group()
coins.add(coin_generator)

# Creating a group of all sprites
all_sprites = pygame.sprite.Group()
all_sprites.add(enemies)
all_sprites.add(P1)
all_sprites.add(coins)

# Custom event to increase the game speed every second
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)


while True:
    for event in pygame.event.get():              
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == INC_SPEED:
            SPEED += 2

    # Draw the background
    DISPLAYSURF.blit(background, (0,0))
    
    # Display the score
    scores = font_small.render(str(SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10,10))
    coin_score = font_small.render(str(COIN_SCORE), True, 'yellow') # "yellow" should be in tuple format
    DISPLAYSURF.blit(coin_score, (SCREEN_WIDTH - 30,10))

    # Update positions
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # collision with enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound('crash.wav').play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30,250)) # Display game over message

        pygame.display.update()
        for entity in all_sprites:
            entity.kill()
        time.sleep(2) # Pause before exiting
        pygame.quit()
        sys.exit()

    # collision with coins
    coin_collided = pygame.sprite.spritecollideany(P1, coins)
    if coin_collided:
        COIN_SCORE += coin_collided.weight # Increase coin score
        COIN_COUNTER += 1
        SPEED += COIN_COUNTER // 5 # Increase speed every 5 coins
        COIN_COUNTER %= 5 # reset counter

        for coin in coins:
            if pygame.sprite.collide_rect(coin, P1): coin.start_begin()

    pygame.display.update()
    FramePerSec.tick(FPS)
