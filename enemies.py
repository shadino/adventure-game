import os
import pygame
from pygame import mixer
import random


GRAVITY = 0.75
RED = (255, 0, 0)


class Enemies(pygame.sprite.Sprite):
    def __init__(self, enemy_type, x, y, scale, speed):
        super().__init__()
        self.alive = True
        self.enemy_type = enemy_type
        self.speed = speed
        self.attack_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 30, 20)
        self.idling = False
        self.idling_counter = 0

        # load enemy types ( Idle for now )
        animation_types = ['Idle', 'Run', 'Death', 'Hurt', 'Attack']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in folder
            num_of_frames = len(os.listdir(f'images/enemies/{self.enemy_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'images/enemies/{self.enemy_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(2)

    def move(self, moving_left, moving_right, obstacle_list, water_group, screen, color):
        # reset movement variables
        #screen_scroll = 0
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
                #if the ai has hit a wall then make it turn around
                self.direction *= -1
                self.move_counter = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if above the ground, i.e. falling
                if self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        #check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        #pygame.draw.rect(screen, RED, self.rect)

    def attack(self, knight):
        if knight.alive:
            self.attack_cooldown = 200
            knight.hit()

    def ai(self, knight, tile_size, screen, color, obstacle_list, water_group, screen_scroll, knight_hit_sound):
        if self.alive and knight.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  #0: Idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai is near the knight
            if self.vision.colliderect(knight.rect):  # lower the vision so that when enemy detects the knight he starts attacking
                # stop running and face the knight
                #self.update_action(0)  #0: Idle
                # attack
                if self.attack_cooldown == 0:
                    self.attack(knight)
                    knight_hit_sound.play()
                    self.update_action(4)
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right, obstacle_list, water_group, screen, color)
                    self.update_action(1)  #1: Run
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 15 * self.direction, self.rect.centery)
                    #pygame.draw.rect(screen, color, self.vision)

                    if self.move_counter > tile_size:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        #scroll
        self.rect.x += screen_scroll

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
            if self.action == 2:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def draw(self, surface):
        surface.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
