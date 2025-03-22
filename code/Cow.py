import pygame
from random import randint
from settings import *
from support import *


class Cow(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups):
        super().__init__(groups)
        self.frames = frames
        self.frames_index = 0
        self.image = self.frames[self.frames_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = 5  # Adjust the z-layer as needed
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.3, -self.rect.height * 0.6)

        self.moving = False
        self.direction = 1  # 1 means moving right, -1 means moving left
        self.x_speed = 1

    def animate(self, dt):  # Switch animation frames
        self.frames_index += 6 * dt  # Change frame every second (6 frames per second)
        if self.frames_index >= len(self.frames):
            self.frames_index = 0
        self.image = self.frames[int(self.frames_index)]

    def update(self, dt):
        if self.moving:
            # Simulate cow movement
            self.rect.x += self.x_speed * self.direction

            # Check if the cow hits the screen boundaries, reverse direction
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.direction *= -1  # Reverse direction

        self.animate(dt)

    def start_moving(self):
        self.moving = True

    def stop_moving(self):
        self.moving = False