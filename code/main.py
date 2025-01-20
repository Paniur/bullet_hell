from settings import *
from player import Player
from sprites import *
from groups import AllSprites
from ui import UI
from enemy import Enemy
from gun import Gun
from pytmx.util_pygame import load_pygame
import pygame
import sys
from random import choice
from enum import Enum

class GameState(Enum):
    START = 1
    PLAYING = 2
    GAME_OVER = 3

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.Font(None, 74)
        self.font_small = pygame.font.Font(None, 36)
        
        # Create text surfaces
        self.title = self.font_big.render("Soldier Hell", True, 'white')
        self.start_text = self.font_small.render("Press SPACE to start", True, 'white')
        self.controls = [
            self.font_small.render("Controls:", True, 'white'),
            self.font_small.render("WASD - Move", True, 'white'),
            self.font_small.render("Mouse - Aim and Shoot", True, 'white'),
            self.font_small.render("R - Reload", True, 'white')
        ]
        
        # Position text
        self.title_rect = self.title.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//3)
        self.start_rect = self.start_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT*2//3)
        
        # Position controls
        self.control_rects = []
        start_y = WINDOW_HEIGHT//2
        for i, text in enumerate(self.controls):
            rect = text.get_rect(centerx=WINDOW_WIDTH//2, centery=start_y + i*30)
            self.control_rects.append(rect)
    
    def draw(self):
        self.screen.fill('black')
        self.screen.blit(self.title, self.title_rect)
        self.screen.blit(self.start_text, self.start_rect)
        for text, rect in zip(self.controls, self.control_rects):
            self.screen.blit(text, rect)

class EndScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.Font(None, 74)
        self.font_small = pygame.font.Font(None, 36)
        
        # Create text surfaces
        self.title = self.font_big.render("Soldier Hell", True, 'white')
        self.end_text = self.font_small.render("Press SPACE to quit", True, 'white')
        self.title_rect = self.title.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT//3)
        self.end_text_rect = self.end_text.get_rect(centerx=WINDOW_WIDTH//2, centery=WINDOW_HEIGHT*2//3)

    def draw(self):
        self.screen.fill('black')
        self.screen.blit(self.title, self.title_rect)
        self.screen.blit(self.end_text, self.end_text_rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("ww2 meets anime hell")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.START
        self.start_screen = StartScreen(self.screen)

        # sprite groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()

        # UI
        self.ui = UI()

        # Score system
        self.score = 0
        self.next_gun_score = 500  # Score needed for next gun upgrade
        self.gun_level = 0
        self.guns = [
            {'name': 'Nambu type 14 ww2.png', 'cooldown': 500, 'magazine': 12},  # Starting gun
            {'name': 'M1911a1 ( WW2 ).png', 'cooldown': 400, 'magazine': 15},  # Level 1
            {'name': 'Walter p38 ww2.png', 'cooldown': 300, 'magazine': 18},  # Level 2
            {'name': 'ppsh-41  ww2.png', 'cooldown': 200, 'magazine': 20},  # Level 3
            {'name': 'Mp40  ww2.png', 'cooldown': 150, 'magazine': 25},  # Level 4
            {'name': 'Stg-44.png', 'cooldown': 100, 'magazine': 30},  # Level 5
        ]
 
        # Enemy spawning
        self.enemy_spawn_time = pygame.time.get_ticks()
        self.enemy_spawn_cooldown = 4000  # 4 seconds
        self.enemy_spawn_positions = []  # Will be filled in setup()

    def setup(self):
        # Load the map
        map = load_pygame(join('data', 'maps', 'world.tmx'))        

        # Create ground sprites
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            pos = (x * TILE_SIZE, y * TILE_SIZE)
            Sprite(pos=pos, surf=image, groups=self.all_sprites)

        # Create collision objects
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        
        # Create collision surfaces
        for obj in map.get_layer_by_name('Collisions'):
            surface = pygame.Surface((obj.width, obj.height))
            CollisionSprite((obj.x, obj.y), surface, self.collision_sprites)

        # Handle entities
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x,obj.y), self.all_sprites, self.collision_sprites, self)
            else:
                self.enemy_spawn_positions.append((obj.x, obj.y))

    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.enemy_spawn_time >= self.enemy_spawn_cooldown:
            if self.enemy_spawn_positions:
                spawn_pos = choice(self.enemy_spawn_positions)
                Enemy(spawn_pos, [self.all_sprites, self.enemy_sprites], 
                     self.collision_sprites, self.player)
                self.enemy_spawn_time = current_time

    def check_gun_upgrade(self):
        if self.score >= self.next_gun_score and self.gun_level < len(self.guns) - 1:
            self.gun_level += 1
            self.next_gun_score += 500
            self.enemy_spawn_cooldown -= 500
            new_gun = self.guns[self.gun_level]
            
            old_gun = self.player.gun
            old_gun.kill()
            
            self.player.gun = Gun(self.player, self.all_sprites, new_gun['name'], 
                                shoot_cooldown=new_gun['cooldown'])
            self.player.gun.magazine_size = new_gun['magazine']
            self.player.gun.current_magazine = new_gun['magazine']

    def increase_score(self, amount):
        self.score += amount
        self.check_gun_upgrade()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if self.state == GameState.START and event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                        self.setup()  # Initialize game when starting

            # Handle different game states
            if self.state == GameState.START:
                self.start_screen.draw()
            elif self.state == GameState.PLAYING:
                dt = self.clock.tick() / 1000
                
                # Update
                self.all_sprites.update(dt)
                self.spawn_enemy()
                
                # Draw
                self.screen.fill('black')
                self.all_sprites.draw(self.player.rect.center)
                
                # UI
                self.ui.show_health(self.player.current_health, self.player.max_health)
                self.ui.show_ammo(self.player.gun.current_magazine, 
                                self.player.gun.magazine_size,
                                self.player.gun.is_reloading)
                self.ui.show_score(self.score)
                if self.score > 4000:
                    self.state = GameState.GAME_OVER
            elif self.state == GameState.GAME_OVER:
                self.end_screen = EndScreen(self.screen)
                self.end_screen.draw()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pygame.quit()
                        sys.exit()
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()
