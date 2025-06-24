import pygame
from pytmx.util_pygame import load_pygame
from random import choice
from support import *
from settings import *


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil water']

class Plant(pygame.sprite.Sprite):
    GRAPHICS_PATH = '../graphics/fruit/'
    PLANT_OFFSETS = {
        'corn': -16,
        'default': -8
    }

    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(groups)

        # Validate plant type
        if plant_type not in GROW_SPEED:
            raise ValueError(f"Invalid plant type: {plant_type}")

        # setup
        self.plant_type = plant_type
        self.soil = soil
        self.frames = import_folder(f'{self.GRAPHICS_PATH}{plant_type}')
        if not self.frames:
            raise ValueError(f"No frames found for plant type: {plant_type}")

        self.check_watered = check_watered

        # plant growing
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False

        # sprite setup
        self.image = self.frames[self.age]
        self.y_offset = self.PLANT_OFFSETS.get(plant_type, self.PLANT_OFFSETS['default'])
        midbottom_pos = pygame.math.Vector2(0, self.y_offset)
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + midbottom_pos)
        self.z = LAYERS['ground plant']

    def grow(self):
        # Dynamically adjust grow speed based on watering
        if self.check_watered(self.rect.center):
            self.grow_speed *= 0.9  # Accelerate growth if watered
        else:
            self.grow_speed *= 1.1  # Slow growth if not watered

        # Update age and harvestable status
        self.age += self.grow_speed

        if int(self.age) > 0:  # plants should be on the main layer
            self.z = LAYERS['main']
            self.hitbox = self.rect.copy().inflate(-30, -self.rect.height * 0.5)

        if self.age >= self.max_age:
            self.age = self.max_age
            self.harvestable = True  # Mark as harvestable when it reaches max age

        # Update the image based on age
        self.image = self.frames[int(self.age)]
        # need rect cuz image change and have different dimensions
        self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))


class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):
        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        self.collision_sprites = collision_sprites

        # graphics
        # self.soil_surf = pygame.image.load('../graphics/soil/o.png')
        self.soil_surfs = import_folder_dict('../graphics/soil/')
        # print(self.soil_surf)
        self.water_surfs = import_folder('../graphics/soil_water')

        #self.create_soil_grid()
        self.create_hit_rects()  # need call!!

        # sounds
        self.hoe_sound = pygame.mixer.Sound('../audio/hoe.wav')
        self.hoe_sound .set_volume(0.4)

        self.plant_sound = pygame.mixer.Sound('../audio/plant.wav')
        self.hoe_sound.set_volume(0.4)

        # if the area is farmable
        # if the soil has been watered
        # if the soil has a plant

    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
        # print(horizontal_tiles)
        # print(vertical_tiles)
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):  # convert all cells into actual positions
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x, y = index_col * TILE_SIZE, index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)  # x,y is topleft, tilesize 64*64
                    self.hit_rects.append(rect)

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:

                    # tile options
                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in row[index_col + 1]
                    l = 'X' in row[index_col - 1]

                    tile_type = 'o'  # the default one

                    # check all sides
                    if all((t,r,b,l)): tile_type = 'x'

                    # horizontal tiles only
                    if l and not any((t, r, b)): tile_type = 'r'
                    if r and not any((t, l, b)): tile_type = 'l'
                    if r and l and not any((t, b)): tile_type = 'lr'

                    # vertical tiles only
                    if t and not any((r, l, b)): tile_type = 'b'
                    if b and not any((r, l, t)): tile_type = 't'
                    if b and t and not any((r, l)): tile_type = 'tb'

                    # T shapes
                    if all((t, b, r)) and not l: tile_type = 'tbr'
                    if all((t, b, l)) and not r: tile_type = 'tbl'
                    if all((l, r, t)) and not b: tile_type = 'lrb'
                    if all((l, r, b)) and not t: tile_type = 'lrt'

                    # corners
                    if l and b and not any((t, r)): tile_type = 'tr'
                    if r and b and not any((t, l)): tile_type = 'tl'
                    if l and t and not any((b, r)): tile_type = 'br'
                    if r and t and not any((b, l)): tile_type = 'bl'


                    SoilTile((index_col * TILE_SIZE, index_row * TILE_SIZE), self.soil_surfs[tile_type],
                             [self.all_sprites, self.soil_sprites])

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                self.hoe_sound.play()

                x, y = rect.x // TILE_SIZE, rect.y // TILE_SIZE  # convert this rect pos back into grid

                if 'F' in self.grid[y][x]:  # y for rows, x for columns
                    # print('farmable')
                    self.grid[y][x].append('X') # on this tile have soil patch
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()

    def water(self, target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                # print('soil tile water')
                # add an entry to the soil grid -> W
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W')
                # create water sprite
                # 1.position from the soil sprite
                pos = soil_sprite.rect.topleft
                # 2. import the folder
                surf = choice(self.water_surfs)
                # 3. create one more sprite
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites])

    def remove_water(self):   # Restart the day water will disappear
            # destroy all water sprites
            for sprite in self.water_sprites.sprites():
                sprite.kill()

            # clean the grid
            for row in self.grid:
                for cell in row:
                    if 'W' in cell:
                        cell.remove('W')

    def water_all(self):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    WaterTile((x, y), choice(self.water_surfs), [self.all_sprites, self.water_sprites])

    def check_watered(self, pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def plant_seed(self, target_pos, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                self.plant_sound.play()

                x = soil_sprite.rect.x // TILE_SIZE  # convert pos inside the grid
                y = soil_sprite.rect.y // TILE_SIZE


                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite,
                          self.check_watered)

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()
