import sys
import pygame
import os
import random
import csv
from knight import Knight, HealthBar
from enemies import Enemies
from tiles_and_icons import Knives, ItemBox, Water, Decoration, Exit
from buttons import Button
from pygame import mixer

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Adventure')

# set frame rate
clock = pygame.time.Clock()
FPS = 60

# define game varriables
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 23
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

# define knight action variables
moving_left = False
moving_right = False
knight_death = False
current_time = 0
button_press_time = 0
attack_swing = 750
knife_b = False
knife_thrown = False

# define colors
BG = (144,201, 120)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
PINK = (235, 65, 54)

# load music and sounds
pygame.mixer.music.load('audio/theme music/sea1.wav')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1, 0.0, 5000)
game_over_fx = pygame.mixer.Sound('audio/theme music/game_over.wav')
game_over_fx.set_volume(0.1)
# pygame.mixer.music.load('audio/theme music/game_over.wav')
# pygame.mixer.music.set_volume(0.3)
knight_jump_fx = pygame.mixer.Sound('audio/knight_jump.wav')
knight_jump_fx.set_volume(0.1)
knight_att_fx = pygame.mixer.Sound('audio/knight_attack.wav')
knight_att_fx.set_volume(0.1)
knight_hit_fx = pygame.mixer.Sound('audio/knight_hit.wav')
knight_hit_fx.set_volume(0.1)
knight_death_fx = pygame.mixer.Sound('audio/knight_death.mp3')
knight_death_fx.set_volume(0.1)
knife_throw_fx = pygame.mixer.Sound('audio/knife_throw.wav')
knife_throw_fx.set_volume(0.1)


# load images
# button images
start_image = pygame.image.load('images/buttons/start_btn.png').convert_alpha()
exit_image = pygame.image.load('images/buttons/exit_btn.png').convert_alpha()
restart_image = pygame.image.load('images/buttons/restart_btn.png').convert_alpha()

knife_img = pygame.image.load('images/icons/knife.png').convert_alpha()

# background images
pine1_img = pygame.image.load('images/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('images/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('images/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('images/background/sky_cloud.png').convert_alpha()

# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'images/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# define font
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


# function to reset level
def reset_level():
    enemy_group.empty()
    knife_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_lenght = len(data[0])
        # iterate through each value in level data file
        for z, row in enumerate(data):
            for c, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = c * TILE_SIZE
                    img_rect.y = z * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, c * TILE_SIZE, z * TILE_SIZE, TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, c * TILE_SIZE, z * TILE_SIZE, TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        item_box = ItemBox('Health', c * TILE_SIZE, z * TILE_SIZE, TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 16:
                        item_box = ItemBox('Knives', c * TILE_SIZE, z * TILE_SIZE, TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 17:
                        exit = Exit(img, c * TILE_SIZE, z * TILE_SIZE, TILE_SIZE)
                        exit_group.add(exit)
                    elif tile == 18:
                        knight = Knight(c * TILE_SIZE, z * TILE_SIZE, 1, 3, 5, screen)
                        health_bar = HealthBar(10, 10, knight.health, knight.health)
                    elif tile == 19:
                        enemy = Enemies('demon axe', c * TILE_SIZE, z * TILE_SIZE, 1, 1)
                        enemy_group.add(enemy)
                    elif tile == 20:
                        enemy = Enemies('imp', c * TILE_SIZE, z * TILE_SIZE, 1, 1)
                        enemy_group.add(enemy)
                    elif tile == 21:
                        enemy = Enemies('light bandit', c * TILE_SIZE, z * TILE_SIZE, 1, 1)
                        enemy_group.add(enemy)
                    elif tile == 22:
                        enemy = Enemies('heavy bandit', c * TILE_SIZE, z * TILE_SIZE, 1, 1)
                        enemy_group.add(enemy)

        return knight, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:  # vertical screen fade down
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


# create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

#create buttons
start_button = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_image, 1)
exit_button = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_image, 1)
restart_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_image, 2)

# Sprite groups
enemy_group = pygame.sprite.Group()
knife_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# load in level data and create world
with open(f'levels/level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
knight, health_bar = world.process_data(world_data)

while 1:
    clock.tick(FPS)

    if start_game is False:
        # draw menu
        screen.fill(BG)
        # add buttons
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            pygame.quit()
            sys.exit()
    else:
        # draw background
        draw_bg()
        # draw world map
        world.draw()
        # show knight health
        health_bar.draw(knight.health, screen)
        # show knives
        draw_text(f'KNIVES: ', font, WHITE, 10, 35)
        for x in range(knight.knives):
            screen.blit(knife_img, (90 + (x * 10), 40))

        # draw knight
        knight.update()
        knight.draw(screen)
        # draw enemies
        for enemy in enemy_group:
            enemy.update()
            enemy.ai(knight, TILE_SIZE, screen, RED, world.obstacle_list, water_group, screen_scroll, knight_hit_fx)
            enemy.draw(screen)

        # update and draw groups
        knife_group.update(SCREEN_WIDTH, enemy_group, knife_group, world.obstacle_list, screen_scroll)
        item_box_group.update(knight, screen_scroll)
        decoration_group.update(screen_scroll)
        water_group.update(screen_scroll)
        exit_group.update(screen_scroll)
        knife_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # show intro
        if start_intro is True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        #update player actions
        if knight.alive:
            if moving_left or moving_right:
                knight.update_action(1)  # 1: run
            elif knight.is_hit:
                knight.update_action(4)  # 4: hit
            elif knight.in_air:
                knight.update_action(2)  # 2: jump
            elif knight.attacking is True:
                knight.update_action(5)  # 5: attack
            elif knife_b is True and knife_thrown == False and knight.knives > 0:
                knife = Knives(knight.rect.centerx, knight.rect.centery, knight.direction)
                knife_group.add(knife)
                # reduce knives
                knight.knives -= 1
                knife_thrown = True
                knife_throw_fx.play()
            else:
                knight.update_action(0)  # 0: idle

            screen_scroll, level_complete = knight.move(moving_left, moving_right, screen, world.obstacle_list, water_group, exit_group,
                                        SCREEN_WIDTH, SCREEN_HEIGHT, world.level_lenght, bg_scroll, TILE_SIZE)
            bg_scroll -= screen_scroll

            # check if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # load in level data and create world
                    with open(f'levels/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    knight, health_bar = world.process_data(world_data)

        else:
            if knight.alive is False and knight_death is False:
                knight_death_fx.play()
                knight_death = True
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    knight_death = False
                    # load in level data and create world
                    with open(f'levels/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    knight, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        if event.type == knight.attack_cooldown:
            knight.attacking = False
            pygame.time.set_timer(knight.attack_cooldown, 0)
        if event.type == knight.hit_cooldown:
            knight.is_hit = False
            pygame.time.set_timer(knight.hit_cooldown, 0)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # keyboard pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE and knight.attacking == False:
                knight.attack(enemy_group)
                knight_att_fx.play()
            if event.key == pygame.K_w and knight.alive:
                knight.jump = True
                knight_jump_fx.play()
            if event.key == pygame.K_m:
                knife_b = True
        # keyboard released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            # if event.key == pygame.K_SPACE:
            #     knight.attacking = False
            if event.key == pygame.K_m:
                knife_b = False
                knife_thrown = False

    pygame.display.update()