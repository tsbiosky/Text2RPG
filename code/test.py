import pygame
import sys
import json
# 初始化
pygame.init()
data=json.load(open("./output.json", 'r', encoding='utf-8'))
# 屏幕尺寸（窗口大小）
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("整图地图 + 玩家移动 + NPC对话")
import random
# 加载地图图片（假设是1024x1024）
map_image = pygame.image.load("../graphics/world/world_map.png").convert()
MAP_WIDTH, MAP_HEIGHT = map_image.get_size()
#MAP_WIDTH, MAP_HEIGHT = 2048,2048
# 加载玩家图片
player_img = pygame.image.load("../graphics/character/"+data["player"]["name"]+"_vector.png").convert_alpha()
player_size = 128
player_img = pygame.transform.scale(player_img, (player_size, player_size))

# 加载NPC图片（如果没有NPC图片，创建一个简单的矩形）
# try:
#     npc_img = pygame.image.load("../graphics/character/down/0.jpeg").convert_alpha()
#     npc_img = pygame.transform.scale(npc_img, (player_size, player_size))
# except:
#     # 创建一个简单的NPC图像（蓝色矩形）
#     npc_img = pygame.Surface((player_size, player_size))
#     npc_img.fill((0, 100, 255))  # 蓝色
#     pygame.draw.rect(npc_img, (0, 0, 200), (0, 0, player_size, player_size), 3)  # 边框

# 玩家位置（在地图上的位置，不是屏幕上的位置）
player_x = MAP_WIDTH // 2
player_y = MAP_HEIGHT // 2
player_speed = 8

# NPC类
class NPC:
    def __init__(self, x, y, name, dialogue_array,image_path):
        self.x = x
        self.y = y
        self.name = name
        self.dialogue_array = dialogue_array  # 对话数组，每个元素是 [speaker, message]
        self.interaction_radius = 100  # 交互半径
        self.is_nearby = False
        self.is_dialogue_active = False
        self.current_dialogue_index = 0  # 当前对话索引
        self.image_path=image_path
    def check_proximity(self, player_x, player_y):
        """检查玩家是否在NPC附近"""
        distance = ((player_x - self.x) ** 2 + (player_y - self.y) ** 2) ** 0.5
        self.is_nearby = distance <= self.interaction_radius
        return self.is_nearby
    
    def start_dialogue(self):
        """开始对话"""
        self.is_dialogue_active = True
        self.current_dialogue_index = 0
    
    def next_dialogue(self):
        """下一句对话"""
        if self.is_dialogue_active:
            self.current_dialogue_index += 1
            if self.current_dialogue_index >= len(self.dialogue_array):
                self.end_dialogue()
    
    def get_current_dialogue(self):
        """获取当前对话"""
        if self.is_dialogue_active and self.current_dialogue_index < len(self.dialogue_array):
            return self.dialogue_array[self.current_dialogue_index]
        return None
    
    def end_dialogue(self):
        """结束对话"""
        self.is_dialogue_active = False
        self.current_dialogue_index = 0

# 创建NPC列表
npcs = []
for n in data["npc"]:
    npcs.append(NPC(random.randint(int(MAP_WIDTH*0.3),int(MAP_WIDTH*0.7)), random.randint(int(MAP_HEIGHT*0.3),int(MAP_HEIGHT*0.7)), n["name"], n["dialogue"], "../graphics/character/"+n["name"]+"_vector.png"))

# 字体设置
pygame.font.init()
font = pygame.font.SysFont("arial", 36)
small_font = pygame.font.SysFont("arial", 24)

# 主循环
clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(60)

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 检查是否有NPC在对话中
                dialogue_active = False
                for npc in npcs:
                    if npc.is_dialogue_active:
                        npc.next_dialogue()
                        dialogue_active = True
                        break
                
                # 如果没有对话在进行，检查是否有NPC在附近开始新对话
                if not dialogue_active:
                    for npc in npcs:
                        if npc.is_nearby and not npc.is_dialogue_active:
                            npc.start_dialogue()
                            break
            elif event.key == pygame.K_ESCAPE:
                # 按ESC键结束所有对话
                for npc in npcs:
                    npc.end_dialogue()

    # 移动玩家
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed

    # 限制玩家在地图内
    player_x = max(0, min(MAP_WIDTH - player_size, player_x))
    player_y = max(0, min(MAP_HEIGHT - player_size, player_y))

    # 检查NPC接近状态
    for npc in npcs:
        was_nearby = npc.is_nearby  # 记录之前是否在附近
        npc.check_proximity(player_x, player_y)
        
        # 如果之前在附近但现在不在，自动关闭对话
        if was_nearby and not npc.is_nearby and npc.is_dialogue_active:
            npc.end_dialogue()

    # 计算摄像机（让玩家尽量在屏幕中心）
    camera_x = player_x - SCREEN_WIDTH // 2
    camera_y = player_y - SCREEN_HEIGHT // 2

    # 限制摄像机在地图内
    camera_x = max(0, min(MAP_WIDTH - SCREEN_WIDTH, camera_x))
    camera_y = max(0, min(MAP_HEIGHT - SCREEN_HEIGHT, camera_y))

    # 绘制地图（显示从camera位置开始的部分）
    screen.blit(map_image, (0, 0), (camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT))

    # 绘制NPC
    for npc in npcs:
        npc_screen_x = npc.x - camera_x
        npc_screen_y = npc.y - camera_y
        npc_img = pygame.image.load(npc.image_path).convert_alpha()
        npc_img = pygame.transform.scale(npc_img, (player_size, player_size))
        # 只绘制在屏幕范围内的NPC
        if (0 <= npc_screen_x <= SCREEN_WIDTH and 0 <= npc_screen_y <= SCREEN_HEIGHT):
            screen.blit(npc_img, (npc_screen_x, npc_screen_y))
            
            # 如果NPC在附近，显示交互提示
            if npc.is_nearby and not npc.is_dialogue_active:
                # 绘制交互提示
                prompt_text = small_font.render("space to talk", True, (255, 255, 255))
                prompt_bg = pygame.Surface((prompt_text.get_width() + 10, prompt_text.get_height() + 5))
                prompt_bg.fill((0, 0, 0))
                prompt_bg.set_alpha(180)
                screen.blit(prompt_bg, (npc_screen_x - 5, npc_screen_y - 30))
                screen.blit(prompt_text, (npc_screen_x, npc_screen_y - 25))

    # 计算玩家在屏幕上的位置
    player_screen_x = player_x - camera_x
    player_screen_y = player_y - camera_y
    screen.blit(player_img, (player_screen_x, player_screen_y))

    # 绘制对话界面
    for npc in npcs:
        if npc.is_dialogue_active:
            current_dialogue = npc.get_current_dialogue()
            if current_dialogue:
                speaker, message = current_dialogue
                
                # 对话背景
                dialogue_width = 800
                dialogue_height = 200
                dialogue_x = (SCREEN_WIDTH - dialogue_width) // 2
                dialogue_y = SCREEN_HEIGHT - dialogue_height - 50
                
                dialogue_bg = pygame.Surface((dialogue_width, dialogue_height))
                dialogue_bg.fill((0, 0, 0))
                dialogue_bg.set_alpha(200)
                screen.blit(dialogue_bg, (dialogue_x, dialogue_y))
                
                # 对话边框
                pygame.draw.rect(screen, (255, 255, 255), (dialogue_x, dialogue_y, dialogue_width, dialogue_height), 3)
                
                # 说话者名字
                speaker_color = (255, 255, 0) if speaker != "player" else (0, 255, 255)  # NPC黄色，玩家青色
                name_text = font.render(f"{speaker}:", True, speaker_color)
                screen.blit(name_text, (dialogue_x + 20, dialogue_y + 20))
                
                # 对话内容（自动换行）
                words = message.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    test_surface = small_font.render(test_line, True, (255, 255, 255))
                    if test_surface.get_width() < dialogue_width - 40:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                # 绘制对话行
                for i, line in enumerate(lines):
                    if i < 4:  # 最多显示4行
                        line_text = small_font.render(line, True, (255, 255, 255))
                        screen.blit(line_text, (dialogue_x + 20, dialogue_y + 60 + i * 25))
                
                # 提示按空格继续或ESC关闭对话
                if npc.current_dialogue_index < len(npc.dialogue_array) - 1:
                    continue_text = small_font.render("space to continue", True, (200, 200, 200))
                    screen.blit(continue_text, (dialogue_x + dialogue_width - 150, dialogue_y + dialogue_height - 30))
                else:
                    close_text = small_font.render("esc to close", True, (200, 200, 200))
                    screen.blit(close_text, (dialogue_x + dialogue_width - 150, dialogue_y + dialogue_height - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()
