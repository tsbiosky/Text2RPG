import pygame
import math
from settings import *
from support import *
from random import randint
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from menu import Menu
from Cow import *
from dialogue_box import DialogueBox

class Level:
    def __init__(self):
        # print("Level __init__ called")
        # get display surface
        self.display_surface = pygame.display.get_surface()
        # sprite groups trees..
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group() # keep track what sprites can be collieded
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        #self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)

        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)


        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 24)
        self.overlay_image = '../graphics/box/0.png'
        self.dialogue_box = None

        # Sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 6
        self.sky = Sky()

        # shop
        self.shop_active = False
        self.menu = Menu(self.player, self.toggle_shop)

        # music
        self.success = pygame.mixer.Sound('../audio/success.wav')
        self.success.set_volume(0.4)
        self.music = pygame.mixer.Sound('../audio/music.mp3')
        self.music.play(loops=-1)

        # npc
        self.dialogue_active = False
    def setup(self):
        tmx_data = load_pygame('../data/map.tmx')

        #npc_layer = tmx_data.get_layer_by_name('npc')

        # house
        # for layer in ['HouseFloor', 'HouseFurnitureBottom']:  # sequence is important
        #     for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
        #         Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
        #
        # for layer in ['HouseWalls', 'HouseFurnitureTop']:
        #     for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
        #         Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['main'])
        #
        # # Fence
        # for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
        #     Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])
        #
        # # trees
        # for obj in tmx_data.get_layer_by_name('Trees'):
        #     Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites, self.tree_sprites], obj.name, self.player_add)
        #
        # # water
        # water_frames = import_folder('../graphics/water')
        # for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
        #     Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
        #
        # # wildflowers
        # for obj in tmx_data.get_layer_by_name('Decoration'):   # retrieves a specific layer from the Tiled map data
        #     WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
        #
        # # collision tiles, set in tiles
        # for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
        #     Generic((x*TILE_SIZE, y*TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)
        #
        # # npc
        # for obj in tmx_data.get_layer_by_name('npc'):
        #     if obj.name == 'npc':
        #         Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, 'npc')
        #
        # # player
        # for obj in tmx_data.get_layer_by_name('Player'): # set start point
        #     if obj.name == 'Start':
        #         self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.tree_sprites, self.interaction_sprites, self.soil_layer, self.toggle_shop)
        #     if obj.name == 'Bed':
        #         Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, 'Bed')
        #     if obj.name == 'Trader':
        #         Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, 'Trader')
        #
        #
        #
        # # Load cows from the CowLayer in the map
        #         cow_frames = import_folder('../graphics/cow')  # Load cow animation frames
        #         for x, y, surf in tmx_data.get_layer_by_name('CowLayer').tiles():
        #             cow = Cow((x * TILE_SIZE, y * TILE_SIZE), cow_frames, self.all_sprites)
        #             cow.start_moving()  # Start the cow's movement
        for obj in tmx_data.get_layer_by_name('Player'): # set start point
            if obj.name == 'Start':
                self.player = Player((obj.x, obj.y), self.all_sprites,self.collision_sprites, self.tree_sprites, self.interaction_sprites, self.toggle_shop)
        tmx_data = load_pygame('../data/map.tmx')
        z = LAYERS['main']
        for layer in tmx_data.visible_layers:  # sequence is important
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, z)
        # Generic(
        #     pos=(0, 0),
        #     surf=pygame.image.load('../graphics/environment/Hogwarts_Floors.png').convert_alpha(),
        #     groups=self.all_sprites, z=LAYERS['ground'])

    def reset(self):
        # sky
        self.sky.start_color = [255, 255, 255]

        # plants, called first.
        self.soil_layer.update_plants()

        # apples on the trees
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()  # reset

        # soil
        self.soil_layer.remove_water()

        # set the rain randomly
        self.raining = randint(0, 10) > 6
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

    def run(self, dt):
        #  print('run game')
        """drawing logic"""
        self.display_surface.fill('black')
        # self.all_sprites.draw(self.display_surface)
        self.all_sprites.custom_draw(self.player)

        """updates"""
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)

        """weather"""
        self.overlay.display()
        # print(self.player.item_inventory)

        # transition overlay
        if self.player.sleep:
            self.transition.play()
        # print(self.player.item_inventory)

        # rain
        if self.raining and not self.shop_active:
            self.rain.update()

        # daytime
        self.sky.display(dt)

        # print(self.shop_active)

        # Check for NPC interactions
        self.check_npc_interactions(dt)

        # hide
        # if self.dialogue_box and not self.player_hit_npc():
        #     self.dialogue_box = None
        if self.dialogue_box and self.player_hit_npc():
            self.dialogue_box.show(self.all_sprites.offset)
        keys = pygame.key.get_pressed()
        #print(keys)
        # update the dialog box and pass the camera offset
        if self.dialogue_box and keys[pygame.K_SPACE]:
            self.dialogue_box.update(self.all_sprites.offset,"qiqi heiheihehie")

    def check_npc_interactions(self, dt):
        npc = self.player_hit_npc()
        if npc:
            if npc.name == 'Trader':
                self.dialogue_box = None
                return
            if npc.name == 'Bed':
                self.dialogue_box = None
                return

            # Set dialogue position
            dialogue_position = (
                npc.rect.centerx + 150,
                npc.rect.top + 50
            )

            # Create or update the dialogue box
            if not self.dialogue_box:
                self.dialogue_box = DialogueBox(self.font, "", self.display_surface, self.overlay_image, dialogue_position)
            else:
                self.dialogue_box.position = dialogue_position
        else:
            # No collision, remove the dialogue box
            self.dialogue_box = None

    # def start_dialogue(self, text, npc_rect):
    #     dialogue_position = (
    #         npc_rect.centerx + 150,
    #         npc_rect.top + 50
    #     )
    #     self.dialogue_box = DialogueBox(self.font, text, self.display_surface, self.overlay_image, dialogue_position)

    def player_hit_npc(self):
        for npc in self.interaction_sprites:
            # print(f"NPC rect: ({npc.rect.x}, {npc.rect.y}, {npc.rect.width}, {npc.rect.height})")
            if self.player.rect.colliderect(npc.rect):
                # print(f"Collision detected with NPC: {npc.name}")
                return npc
        return None


    def player_add(self, item):
        self.player.item_inventory[item] += 1
        self.success.play()


    def toggle_shop(self):
        self.shop_active = not self.shop_active

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery): # sorted is element overlap
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)

