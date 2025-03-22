import pygame
from settings import *

class Transition:
    def __init__(self, reset, player):
        # set up
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # overlay image
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255   # white color
        self.speed = -1  # Color Gradient

    def play(self):
        self.color += self.speed
        # self.color = max(0, min(255, self.color))
        # call reset - wakeup player - set the speed
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            self.reset()
        if self.color > 255:
            self.color = 255
            self.player.sleep = False
            self.speed = -1

        self.image.fill((self.color, self.color, self.color))  # rgb
        self.display_surface.blit(self.image, (0,0), special_flags=pygame.BLEND_RGBA_MULT)  # blending mode
