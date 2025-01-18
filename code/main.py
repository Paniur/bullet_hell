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

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("ww2 meets anime hell")
        self.clock = pygame.time.Clock()
        self.running = True

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

        self.setup()

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
            dt = self.clock.tick() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update
            self.spawn_enemy()
            self.all_sprites.update(dt)

            # draw
            self.screen.fill((255, 255, 255))
            self.all_sprites.draw(self.player.rect.center)
            # Draw UI on top
            self.ui.show_health(self.player.current_health, self.player.max_health)
            self.ui.show_ammo(self.player.gun.current_magazine, 
                            self.player.gun.magazine_size,
                            self.player.gun.is_reloading)
            self.ui.show_score(self.score)
            pygame.display.update()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
