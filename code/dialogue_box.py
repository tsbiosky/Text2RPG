import pygame


class DialogueBox:
    def __init__(self, font, text, display_surface, image_path, position):
        self.font = font
        self.text = text
        self.display_surface = display_surface
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (176*2, 48*2))


        self.position = position


        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surface.get_rect(center=(self.position[0], self.position[1] - 10))

    def update(self, camera_offset,text):
        self.text_surface = self.font.render(text, True, (255, 255, 255))
        self.image_x = self.position[0] - self.image.get_width() // 2 - camera_offset.x
        self.image_y = self.position[1] - self.image.get_height() - camera_offset.y
        self.text_rect = self.text_surface.get_rect(center=(self.image_x + self.image.get_width() // 2, self.image_y + self.image.get_height() // 2))
    def show(self,camera_offset):
        self.image_x = self.position[0] - self.image.get_width() // 2 - camera_offset.x
        self.image_y = self.position[1] - self.image.get_height() - camera_offset.y
        self.display_surface.blit(self.image, (self.image_x, self.image_y))
        self.display_surface.blit(self.text_surface, self.text_rect)
