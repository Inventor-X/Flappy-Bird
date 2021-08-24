# #######################FLAPPY BIRD GAME SOURCE CODE###########################################
# #######################THIS GAME IS NOT THE ORIGINAL FLAPPY BIRD GAME THIS IS A REPLICA WITH A NEW LOOK##############################
# importing the required modules
import pygame
import random
from pygame import mixer
import sys
import csv
import os


# resource path for making exe file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# initialising the pygame
pygame.init()
mixer.init()

# loading the images
icon = pygame.image.load(resource_path('sprites/yellowbird-upflap.png'))
bottom_pipe = pygame.image.load(resource_path('sprites/pipe-green.png'))
bottom_pipe = pygame.transform.scale(bottom_pipe,
                                     (int(bottom_pipe.get_width() * 1.5), int(bottom_pipe.get_height() * 2)))
top_pipe = pygame.transform.flip(bottom_pipe, False, True)
# bottom_pipe_orange = pygame.image.load('sprites/pipe-red.png')
# bottom_pipe_orange = pygame.transform.scale(bottom_pipe_orange,
#                                      (int(bottom_pipe_orange.get_width() * 1.5), int(bottom_pipe_orange.get_height() * 2)))
# top_pipe_orange = pygame.transform.flip(bottom_pipe_orange, False, True)
bg = pygame.image.load(resource_path("41524.jpg"))
game_over_img = pygame.image.load(resource_path('game-over.png'))

# game variables
HEIGHT = 600
WIDTH = 1000
clock = pygame.time.Clock()
fps = 60
gravity = 0.75
pipe_height = bottom_pipe.get_height()
gap = 150
pipe_time = pygame.time.get_ticks()
white = (255, 255, 255)
# creating the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
pygame.display.set_icon(icon)


# display score:
def display_score():
    font = pygame.font.Font(resource_path('KGBlankSpaceSketch.ttf'), 48)
    text = font.render(str(int(bird.points)), True, white)
    textRect = text.get_rect()
    textRect.center = (WIDTH // 2, HEIGHT // 10)
    screen.blit(text, textRect)


# importing highscore.csv
file1 = open(resource_path("highscore.csv"), "r")
reader = csv.reader(file1)
highscore_list = list(reader)
highscore_row = highscore_list[0]


# obstacle
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, speed, image, dummy, a):
        pygame.sprite.Sprite.__init__(self)
        self.a = a
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -self.a + dummy
        self.speed = speed
        self.not_crossed = True

    def update(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        # is obstacle crossed by bird
        self.crossed()
        # screen.blit(bottom_pipe, (self.bottom_rect.x, int(self.pipe_height + self.gap - self.a)))
        dx = 0
        if bird.alive:
            dx += self.speed
            self.rect.x += dx
            if self.rect.x <= -75:
                self.kill()
            # collision with bird
            if pygame.sprite.spritecollide(bird, obstacle_group, False):
                hit_sound = mixer.Sound(resource_path("audio/hit.wav"))
                hit_sound.set_volume(3)
                hit_sound.play()
                bird.alive = False

    def crossed(self):
        if bird.rect.x >= self.rect.x + self.rect.width and self.not_crossed:
            points_fx = mixer.Sound(resource_path("audio/point.wav"))
            points_fx.play()
            bird.points += 0.5
            self.not_crossed = False


# base
class Base(pygame.sprite.Sprite):
    def __init__(self, speed, x):
        pygame.sprite.Sprite.__init__(self)
        base = pygame.image.load(resource_path("54038-8-ground-hd-png-image-high-quality.png"))
        base = pygame.transform.scale(base, (int(base.get_width() * 1.6), int(base.get_height() * 0.25)))
        self.image = base
        self.rect = self.image.get_rect()
        self.height = self.image.get_height()
        self.rect.x = x
        self.rect.y = HEIGHT - self.height
        self.speed = speed

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        if bird.alive:
            self.rect.x -= self.speed
            if self.rect.x + self.rect.width <= 0:
                self.rect.x = WIDTH
            # collision with bird
            if pygame.sprite.spritecollide(bird, base_group, False):
                bird.alive = False
                hit_sound = mixer.Sound(resource_path("audio/hit.wav"))
                hit_sound.set_volume(3)
                hit_sound.play()


# background
class Background:
    def __init__(self, speed, x):
        self.image = bg
        self.rect = self.image.get_rect()
        self.height = self.image.get_height()
        self.rect.x = x
        self.rect.y = 0
        self.speed = speed
        self.clicked = False

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        # pos = pygame.mouse.get_pos()
        # if self.rect.collidepoint(pos):
        #     if pygame.mouse.get_pressed()[0]:
        #         self.clicked = True
        #         print("hi")

    def update(self):
        if bird.alive:
            self.rect.x -= self.speed
            if self.rect.x + self.rect.width <= 0:
                self.rect.x = WIDTH


# creating the bird class:
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, scale):
        pygame.sprite.Sprite.__init__(self)
        self.time = pygame.time.get_ticks()
        self.animation_list = []
        self.index = 0
        self.speed = speed
        self.moving = False
        self.vel_y = 0
        self.jump = False
        self.alive = True
        self.scale = scale
        self.points = 0
        for i in range(3):
            img = pygame.image.load(resource_path(f"bird/{i}.png"))
            img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
            self.animation_list.append(img)
        self.image = self.animation_list[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self):
        dx = 0
        dy = 0
        if self.alive:
            # updating the bird position
            if self.moving:

                dx += self.speed
                # jumping
                if self.jump:
                    self.vel_y = -5
                # gravity
                self.vel_y += gravity
                dy += self.vel_y
            self.rect.centerx += dx
            self.rect.centery += dy
            if self.rect.centery <= 10:
                self.rect.centery = 10

    def update(self):
        if self.alive:
            # display_score
            display_score()
            # updating bird animation index
            ANIMATION_DELAY = 80

            if pygame.time.get_ticks() - self.time > ANIMATION_DELAY:
                self.index += 1
                self.time = pygame.time.get_ticks()
                if self.index > 2:
                    self.index = 0
            self.image = self.animation_list[self.index]
        else:
            self.image = pygame.image.load(resource_path("sprites/redbird-midflap.png"))
            self.image = pygame.transform.scale(self.image, (
                int(self.image.get_width() * self.scale), int(self.image.get_height() * self.scale)))

    def draw(self):
        screen.blit(self.image, self.rect)


# Reset
class Reset():
    def __init__(self):
        w = 250
        h = 50
        ##restart button
        self.restart = pygame.Surface((w, h), pygame.SRCALPHA)
        font = pygame.font.Font(resource_path('KGBlankSpaceSketch.ttf'), 48)
        text = font.render("RESTART", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (w // 2, h // 2)
        self.restart.blit(text, textRect)
        self.restart_rect = self.restart.get_rect()
        self.restart_rect.center = (WIDTH * 0.04, HEIGHT * 0.9)
        ##exit button
        self.exit = pygame.Surface((w, h), pygame.SRCALPHA)
        font = pygame.font.Font(resource_path('KGBlankSpaceSketch.ttf'), 48)
        text = font.render("EXIT", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (w // 2, h // 2)
        self.exit.blit(text, textRect)
        self.exit_rect = self.restart.get_rect()
        self.exit_rect.center = (WIDTH * 0.8, HEIGHT * 0.9)

    def reset(self):
        bird.rect.center = (500, 300)
        bird.alive = True
        bird.moving = False
        obstacle_group.empty()
        bird.points = 0

    def draw(self):
        s = pygame.Surface((WIDTH, HEIGHT))
        s.fill((0, 0, 0))
        s.set_alpha(50)
        screen.blit(s, (0, 0))
        screen.blit(game_over_img, (0, -HEIGHT * 0.1))
        screen.blit(self.restart, self.restart_rect.center)
        screen.blit(self.exit, self.exit_rect.center)
        # highscore display:
        font = pygame.font.Font(resource_path('KGBlankSpaceSketch.ttf'), 48)
        text = font.render("HIGH-SCORE: " + str(HIGHSCORE), True, white)
        textRect = text.get_rect()
        textRect.center = (WIDTH * 0.53, HEIGHT * 0.9)
        screen.blit(text, textRect)
        # final score display:
        font = pygame.font.Font(resource_path('KGBlankSpaceSketch.ttf'), 48)
        text = font.render("YOUR-SCORE: " + str(int(bird.points)), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (WIDTH * 0.53, HEIGHT * 0.8)
        screen.blit(text, textRect)
        for event in pygame.event.get():
            # quitting event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                    self.reset()

        pos = pygame.mouse.get_pos()
        if self.restart_rect.collidepoint(pos):
            if pygame.mouse.get_pressed(5)[0]:
                self.reset()

        if self.exit_rect.collidepoint(pos):
            if pygame.mouse.get_pressed(5)[0]:
                pygame.quit()
                sys.exit()


# Start
class Start():
    def __init__(self):
        self.image = pygame.image.load(resource_path("start.png"))
        self.image = pygame.transform.scale(self.image,
                                            (int(self.image.get_width() * 0.15), int(self.image.get_height() * 0.15)))
        self.rect = self.image.get_rect()
        self.rect.center = (int(WIDTH / 2), int(HEIGHT / 2 + 80))
        self.start_game = False

    def draw(self):
        screen.blit(self.image, self.rect)
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:
                self.start_game = True
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.start_game = True


# creating sprite group
obstacle_group = pygame.sprite.Group()
base_group = pygame.sprite.Group()
# creating instances
bird = Bird(500, 300, 0, 1.2)
base = Base(3, 0)
base2 = Base(3, WIDTH)
base_group.add(base)
base_group.add(base2)
background = Background(2, 0)
background2 = Background(2, WIDTH)
reset = Reset()
start = Start()
# background_music:
mixer.music.load(resource_path('audio/background_fx.wav'))
mixer.music.set_volume(0.3)
mixer.music.play(-1)
# creating the main game loop
run = True
while run:
    clock.tick(fps)
    # Highscore updating:
    HIGHSCORE = highscore_row[1]
    # draw background
    background.draw()
    background.update()
    background2.draw()
    background2.update()
    if start.start_game:
        # increasing the level
        if bird.points >= 10:
            gap = 120
            a = random.randint(230, 600)
        else:
            gap = 150
            a = random.randint(250, 600)

        PIPE_DELAY = 1500
        if pygame.time.get_ticks() - pipe_time > PIPE_DELAY and bird.alive:
            obstacle_top = Obstacle(WIDTH, -3, top_pipe, 0, a)
            obstacle_bottom = Obstacle(WIDTH, -3, bottom_pipe, pipe_height + gap, a)
            obstacle_group.add(obstacle_top)
            obstacle_group.add(obstacle_bottom)
            pipe_time = pygame.time.get_ticks()

        # obstacle methods
        obstacle_group.draw(screen)
        obstacle_group.update()

    else:
        start.draw()

    # draw base
    base.draw()
    base.update()
    base2.draw()
    base2.update()

    # bird methods
    bird.update()
    bird.draw()
    bird.move()

    # input the events
    for event in pygame.event.get():
        # quitting event
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()
        # # mouse clicks
        # if background.clicked or background2.clicked:
        #     bird.moving = True
        #     bird.jump = True
        #     wing_sound = mixer.Sound("audio/wing.wav")
        #     wing_sound.set_volume(2)
        #     wing_sound.play()
        #     background.clicked = False
        #     background2.clicked = False
        # else:
        #     bird.jump = False

        # keypoard presses
        if start.start_game:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    bird.moving = True
                    bird.jump = True
                    wing_sound = mixer.Sound(resource_path("audio/wing.wav"))
                    wing_sound.set_volume(2)
                    wing_sound.play()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            # keyboard lifts
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    bird.jump = False
    # bird dies
    if not bird.alive:
        if int(bird.points) >= int(highscore_row[1]):
            highscore_row[1] = str(int(bird.points))
            file2 = open(resource_path("highscore.csv"), "w")
            writer = csv.writer(file2)
            writer.writerow(highscore_row)
            file2.close()
            file1.close()
        reset.draw()

    pygame.display.update()
