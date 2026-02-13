import pygame
from sys import exit
import os
import random

GAME_RESOLUSION = (1024,1024)

PLAYER_X = 0
PLAYER_Y = 300

PLAYER_SPEED = 5

PLAYER_WIDTH = 64
PLAYER_HEIGHT = 128

GRAVITY = 0.5
JUMP_STRENGTH = -13

BLOCKSIZE = 64

FLOOR = 1000 

CAMERA_VERTICAL_THRESHOLD = 200

pygame.init()
window = pygame.display.set_mode(GAME_RESOLUSION)
pygame.display.set_caption("2D minecraft?")
clock = pygame.time.Clock()

def load_image(image_name, scale=None):
    image_path = os.path.join(os.path.dirname(__file__), "images", image_name)
    image = pygame.image.load(image_path)
    if scale is not None:
        image = pygame.transform.scale(image, scale)
    return image

Stone_image = load_image("Stone.png", (BLOCKSIZE, BLOCKSIZE))
grass_image = load_image("grass.png", (BLOCKSIZE, BLOCKSIZE))
Dirt_image = load_image("dirt.png", (BLOCKSIZE, BLOCKSIZE))
background_image = load_image("bg_copy.png", GAME_RESOLUSION)
player_image = load_image("Steve.png", (PLAYER_WIDTH, PLAYER_HEIGHT))

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
    
    def apply_to_blocks(self, blocks):

        for block in blocks:
            block.screen_x = block.world_x - self.x
            block.screen_y = block.world_y - self.y
    
    def apply_to_player(self, player):

        return (player.world_x - self.x, player.world_y - self.y)

class Player:
    def __init__(self):
        self.world_x = PLAYER_X
        self.world_y = PLAYER_Y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.image = player_image
        self.vel_x = 0
        self.vel_y = 0
        self.jumping = False
        self.on_ground = False
    
    def get_rect(self):
        return pygame.Rect(self.world_x, self.world_y, self.width, self.height)

class Tile:
    def __init__(self, x, y, image, block_type='dirt'):
        self.world_x = x
        self.world_y = y
        self.screen_x = x
        self.screen_y = y
        self.image = image
        self.block_type = block_type
    
    def get_rect(self):
        return pygame.Rect(self.world_x, self.world_y, BLOCKSIZE, BLOCKSIZE)

def check_collision_x(player, blocks, vel_x):

    player.world_x += vel_x
    player_rect = player.get_rect()

    for block in blocks:
        block_rect = block.get_rect()
        if player_rect.colliderect(block_rect):

            if vel_x > 0:  
                player.world_x = block.world_x - player.width
            elif vel_x < 0: 
                player.world_x = block.world_x + BLOCKSIZE
            return

def check_collision_y(player, blocks):

    player.on_ground = False

    player.world_y += player.vel_y
    player_rect = player.get_rect()
    

    for block in blocks:
        block_rect = block.get_rect()
        if player_rect.colliderect(block_rect):
            if player.vel_y > 0:  
                player.world_y = block.world_y - player.height
                player.vel_y = 0
                player.jumping = False
                player.on_ground = True
            elif player.vel_y < 0: 
                player.world_y = block.world_y + BLOCKSIZE
                player.vel_y = 0 
            return
    

    if player.world_y + player.height >= FLOOR:
        player.world_y = FLOOR - player.height
        player.vel_y = 0
        player.jumping = False
        player.on_ground = True

def update_camera(camera, player):
    target_x = player.world_x - GAME_RESOLUSION[0] // 2 + player.width // 2
    camera.x += (target_x - camera.x) * 0.1  
    

    player_screen_y = player.world_y - camera.y
    screen_center_y = GAME_RESOLUSION[1] // 2
    

    if player_screen_y < screen_center_y - CAMERA_VERTICAL_THRESHOLD:
        target_y = player.world_y - screen_center_y + CAMERA_VERTICAL_THRESHOLD
        camera.y += (target_y - camera.y) * 0.1
    elif player_screen_y > screen_center_y + CAMERA_VERTICAL_THRESHOLD:
        target_y = player.world_y - screen_center_y - CAMERA_VERTICAL_THRESHOLD
        camera.y += (target_y - camera.y) * 0.1

def gravity(player, blocks):

    if not player.on_ground:
        player.vel_y += GRAVITY
    

    if player.vel_y > 15:
        player.vel_y = 15
    

    check_collision_y(player, blocks)

def map(   
    width=150,
    min_height=1,
    max_height=30,
    smoothness=2,
    seed=None,
    terrain_type='valley',
    gap_chance=0,
    gap_width=(-2, 1),
    platform_height_variance=2.5,
    start_height=6,
    end_height=None,
    slope_direction='none',
    noise_scale=0.5,
    double_layer_chance=0.025,
    stone_depth = 7, 
    ore_chance=0.2
):

    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()
    
    # Determine starting height
    if start_height is not None:
        prev_height = start_height
    else:
        prev_height = rng.randint(min_height, max_height)
    
    # Calculate slope increment if needed
    slope_increment = 0
    if slope_direction != 'none' and end_height is not None:
        slope_increment = (end_height - prev_height) / width
    elif slope_direction == 'up':
        slope_increment = (max_height - min_height) / width
    elif slope_direction == 'down':
        slope_increment = -(max_height - min_height) / width
    
    in_gap = False
    gap_countdown = 0
    
    for i, x in enumerate(range(-width // 2, width // 2)):
        # Handle gaps
        if gap_countdown > 0:
            gap_countdown -= 1
            continue
        elif not in_gap and rng.random() < gap_chance:
            in_gap = True
            gap_countdown = rng.randint(gap_width[0], gap_width[1])
            continue
        else:
            in_gap = False
        
        # Calculate base height based on terrain type
        if terrain_type == 'flat':
            height = (min_height + max_height) // 2
        
        elif terrain_type == 'steps':
            step_size = width // max(1, (max_height - min_height))
            height = min_height + (i // max(1, step_size))
            height = min(height, max_height)
        
        elif terrain_type == 'hills':
            # Sine wave pattern
            import math
            wave = math.sin(i * 0.3 * noise_scale)
            height = int(min_height + (max_height - min_height) * (wave + 1) / 2)
        
        elif terrain_type == 'valley':
            # V-shaped valley
            mid = width // 2
            distance_from_mid = abs(i - mid)
            height = min_height + int((distance_from_mid / mid) * (max_height - min_height))
        
        elif terrain_type == 'mountain':
            # Inverted valley (peak in middle)
            mid = width // 2
            distance_from_mid = abs(i - mid)
            height = max_height - int((distance_from_mid / mid) * (max_height - min_height))
        
        else:  # 'random'
            if smoothness == 0:
                height = rng.randint(min_height, max_height)
            else:
                max_change = max(1, (max_height - min_height) // smoothness)
                height = prev_height + rng.randint(-max_change, max_change)
                height = max(min_height, min(max_height, height))
        
        # Apply slope
        if slope_increment != 0:
            height = int(height + (slope_increment * i))
            height = max(min_height, min(max_height, height))
        
        # Add platform variance
        if platform_height_variance > 0:
            height += rng.randint(0, int(platform_height_variance * noise_scale))
            height = max(min_height, min(max_height, height))
        
        prev_height = height
        
        # Create main column of blocks with different types
        for y in range(height):
            # Determine block type based on position
            if y == height - 1:  # Top block
                block_image = grass_image
                block_type = 'grass'
            elif y < 3:  # Bottom 3 layers
                block_image = Stone_image
                block_type = 'stone'
            else:  # Middle layers
                block_image = Dirt_image
                block_type = 'dirt'
            
            block = Tile(
                x * BLOCKSIZE,
                FLOOR - (y * BLOCKSIZE),
                block_image,
                block_type
            )
            blocks.append(block)
        
        # Add occasional second layer/platform above
        if double_layer_chance > 0 and rng.random() < double_layer_chance:
            layer_height = rng.randint(1, 3)
            layer_y_offset = rng.randint(2, 4)
            for y in range(layer_height):
                # Floating platforms are usually grass on top, dirt below
                if y == layer_height - 1:
                    block_image = grass_image
                    block_type = 'grass'
                else:
                    block_image = Dirt_image
                    block_type = 'dirt'
                
                block = Tile(
                    x * BLOCKSIZE,
                    FLOOR - ((height + layer_y_offset + y) * BLOCKSIZE),
                    block_image,
                    block_type
                )
                blocks.append(block)

def draw(camera, player, blocks):
    window.fill((20, 18, 167))
    window.blit(background_image, (0,0))
    
    camera.apply_to_blocks(blocks)
    player_screen_pos = camera.apply_to_player(player)
    

    for block in blocks:

        if -BLOCKSIZE < block.screen_x < GAME_RESOLUSION[0] and -BLOCKSIZE < block.screen_y < GAME_RESOLUSION[1]:
            window.blit(block.image, (block.screen_x, block.screen_y))
    

    window.blit(player.image, player_screen_pos)


blocks = []
player = Player()
camera = Camera()
map()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    keys = pygame.key.get_pressed()
    

    if (keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]) and player.on_ground:
        player.jumping = True
        player.vel_y = JUMP_STRENGTH
    

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        check_collision_x(player, blocks, -PLAYER_SPEED)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        check_collision_x(player, blocks, PLAYER_SPEED)

    gravity(player, blocks)

    update_camera(camera, player)
    

    draw(camera, player, blocks)
    
    pygame.display.update()
    clock.tick(60)