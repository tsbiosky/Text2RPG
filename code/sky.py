import pygame
import random
from settings import *
from support import import_folder
from random import randint, choice
from sprites import Generic

class Sky:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255]  # Initial color (daytime)
        self.end_color = [38, 101, 189]    # End color (blue sky)

    def display(self, dt):
        # Increase the rate of transition for faster day-night cycle
        transition_speed = 0.5

        for index, value in enumerate(self.end_color):
            if self.start_color[index] > value:
                self.start_color[index] -= transition_speed * dt  # Faster change

        self.full_surf.fill(self.start_color)  # Fill with updated color
        self.display_surface.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)  # Draw sky


class Drop(Generic):
    def __init__(self, surf, pos, moving, groups, z):
        # setup
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        # moving
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)

            # Base direction with randomization
            base_direction = pygame.math.Vector2(-2, 5)
            angle_variation = random.uniform(-10, 10)  # Adjust the range for more or less variation
            self.direction = base_direction.rotate(angle_variation)

            # Speed remains in the original range
            self.speed = randint(180, 250)

    def update(self, dt):
        # movement
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # timer, destroy the sprite after lifetime expires
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.rain_drops = import_folder('../graphics/rain/drops/')
        self.rain_floor = import_folder('../graphics/rain/floor/')
        self.floor_w, self.floor_h = pygame.image.load('../graphics/world/ground.png').get_size()

    def create_floor(self):  # surf, pos, moving, groups, z
        Drop(
            choice(self.rain_floor),
            (randint(0, self.floor_w), randint(0, self.floor_h)),
            False,
            self.all_sprites,
            LAYERS['rain floor']
        )

    def create_drops(self):
        Drop(
            choice(self.rain_drops),
            (randint(0, self.floor_w), randint(0, self.floor_h)),
            True,
            self.all_sprites,
            LAYERS['rain drops']
        )

    def update(self):
        self.create_floor()
        self.create_drops()

