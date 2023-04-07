import os
import pygame
from pygame import mixer
import time

mixer.init()

GRAVITY = 0.75
SCROLL_THRESH = 200
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


class Knight(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, knives, surface):
        super().__init__()
        self.alive = True
        self.size = 65
        self.speed = speed
        self.knives = knives
        self.start_knives = knives
        self.attacking = False
        self.attack_cooldown = 0
        self.is_hit = False
        self.hit_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.flip = False
        self.vel_y = 0
        self.jump = False
        self.in_air = False
        self.direction = 1
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the player
        animation_types = ['Idle', 'Run', 'Jump', 'Death', 'Hurt', 'Attack']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in folder
            num_of_frames = len(os.listdir(f'images/knight/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'images/knight/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), (int(img.get_height() * scale))))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect = self.rect.inflate(-30, 0)
        self.width = self.rect.width
        self.height = self.rect.height
        self.rect.center = (x, y)

    def update(self):
        self.check_alive()
        self.update_animation()

    def hit(self):
        self.health -= 10
        if self.is_hit is False:
            self.is_hit = True
            pygame.time.set_timer(self.hit_cooldown, 300)  # resets the cooldown in 0.3 seconds

    def check_alive(self):
        if self.health <= 0:

            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def move(self, moving_left, moving_right, screen, obstacle_list, water_group,
             exit_group, screen_width, screen_height, level_lenght, bg_scroll, tile_size):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump is True and self.in_air is False:
            self.vel_y = -13
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # check collision
        for tile in obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
        # check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check if fallen off the map
        if self.rect.bottom > screen_height:
            self.health = 0

        # check if going off the edges of the screen
        if self.rect.left + dx < 0 or self.rect.right > screen_width:
            dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        #pygame.draw.rect(screen, RED, self.rect)

        # update scroll based on player position
        if (self.rect.right > screen_width - SCROLL_THRESH and bg_scroll < (level_lenght * tile_size) - screen_width)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
            self.rect.x -= dx
            screen_scroll = -dx

        return screen_scroll, level_complete

    def attack(self, enemy_group):
        if self.attacking is False:
            self.attacking = True
            pygame.time.set_timer(self.attack_cooldown, 700)  # sets the attack cooldown to 0.7 seconds
            #print('attack')
            for enemy in enemy_group:
                if pygame.sprite.collide_rect(self, enemy):
                    if enemy.alive:
                        enemy.health -= 50

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation setting
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100

        # update image depending on current time
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out then reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def draw(self, surface):
        surface.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health, surface):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(surface, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(surface, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(surface, GREEN, (self.x, self.y, 150 * ratio, 20))

