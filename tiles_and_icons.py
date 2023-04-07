import pygame


health_box_image = pygame.image.load('images/icons/health_box.png')
knife_box_image = pygame.image.load('images/icons/knife_box.png')
item_boxes = {
    'Health' : health_box_image,
    'Knives' : knife_box_image
}


class Knives(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = 10
        self.image = pygame.image.load('images/icons/knife.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self, screen_width, enemy_group, knife_group, obstacle_list, screen_scroll):
        # move the knife
        self.rect.x += self.direction * self.speed + screen_scroll
        # check if knife has gone of screen
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()

        # check for collision with level
        for tile in obstacle_list:
            if tile [1].colliderect(self.rect):
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, knife_group, False):
                if enemy.alive:
                    enemy.health -= 50
                    self.kill()


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y, tile_size):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self, screen_scroll):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y, tile_size):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self, screen_scroll):
        self.rect.x += screen_scroll


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y, tile_size):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self, screen_scroll):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y, tile_size):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self, knight, screen_scroll):
        # scroll
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, knight):
            # check the type of box
            if self.item_type == 'Health':
                knight.health += 25
                if knight.health > knight.max_health:
                    knight.health = knight.max_health
            elif self.item_type == 'Knives':
                knight.knives += 5
            # delete the box
            self.kill()