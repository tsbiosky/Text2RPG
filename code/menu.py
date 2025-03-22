import pygame
from settings import *
from timer import Timer


FONT_PATH = '../font/LycheeSoda.ttf'
BUTTON_LABELS = {"buy": "Buy", "sell": "Sell"}

class Menu:
    def __init__(self, player, toggle_menu):
        # General setup
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(FONT_PATH, 30)

        # Options
        self.width = 400
        self.space = 10
        self.padding = 8

        # Entries
        self.update_options()

        # Movement
        self.index = 0
        self.timer = Timer(200)

        # Feedback message
        self.feedback_message = ""

    def display_money(self):
        text_surf = self.font.render(f'${self.player.money}', False, BLACK)
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 40))

        pygame.draw.rect(self.display_surface, WHITE, text_rect.inflate(10, 10), 0, 4)
        self.display_surface.blit(text_surf, text_rect)

        # Display feedback message if it exists
        if self.feedback_message:
            feedback_surf = self.font.render(self.feedback_message, False, BLACK)
            feedback_rect = feedback_surf.get_rect(midtop=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30))
            self.display_surface.blit(feedback_surf, feedback_rect)

    def update_options(self):
        """Dynamically updates the menu options."""
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seeds_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()

    def setup(self):
        """Creates text surfaces and calculates the menu layout."""
        self.text_surfs = []
        self.total_height = 0

        for item in self.options:
            text_surf = self.font.render(item, False, BLACK)
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2, self.menu_top, self.width, self.total_height)

        # Buy/Sell text surfaces
        self.buy_text = self.font.render(BUTTON_LABELS["buy"], False, BLACK)
        self.sell_text = self.font.render(BUTTON_LABELS["sell"], False, BLACK)

    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index = (self.index - 1) % len(self.options)
                self.timer.activate()

            if keys[pygame.K_DOWN]:
                self.index = (self.index + 1) % len(self.options)
                self.timer.activate()

            if keys[pygame.K_SPACE]:
                self.timer.activate()
                self.handle_selection()

    def handle_selection(self):
        """Handles buy and sell logic."""
        current_item = self.options[self.index]

        # Sell
        if self.index <= self.sell_border:
            if self.player.item_inventory[current_item] > 0:
                self.player.item_inventory[current_item] -= 1
                self.player.money += SALE_PRICES[current_item]
                self.feedback_message = f"Sold {current_item}!"
            else:
                self.feedback_message = f"No {current_item} to sell!"

        # Buy
        else:
            seed_price = PURCHASE_PRICES[current_item]
            if self.player.money >= seed_price:
                self.player.seeds_inventory[current_item] += 1
                self.player.money -= seed_price
                self.feedback_message = f"Bought {current_item}!"
            else:
                self.feedback_message = f"Not enough money for {current_item}!"

    def show_entry(self, text_surf, amount, top, selected):
        """Displays a single menu entry."""
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, WHITE, bg_rect, 0, 4)

        # Text
        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        # Amount
        amount_surf = self.font.render(str(amount), False, BLACK)
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        # Selected
        if selected:
            pygame.draw.rect(self.display_surface, BLACK, bg_rect, 4, 4)
            if self.index <= self.sell_border:  # Sell
                pos_rect = self.sell_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
                self.display_surface.blit(self.sell_text, pos_rect)
            else:  # Buy
                pos_rect = self.buy_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
                self.display_surface.blit(self.buy_text, pos_rect)

    def update(self):
        self.input()
        self.display_money()

        # Display entries with scrolling
        visible_entries = 10  # Number of entries visible at once
        start_index = max(0, self.index - visible_entries // 2)
        end_index = min(len(self.text_surfs), start_index + visible_entries)

        for text_index in range(start_index, end_index):
            text_surf = self.text_surfs[text_index]
            top = self.main_rect.top + (text_index - start_index) * (text_surf.get_height() + (self.padding * 2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seeds_inventory.values())
            amount = amount_list[text_index]
            self.show_entry(text_surf, amount, top, self.index == text_index)