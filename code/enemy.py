from settings import *
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, player):
        super().__init__(groups)
        self.collision_sprites = collision_sprites
        self.player = player
        
        # Animation setup
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 8
        
        # General setup
        self.image = self.animations[0]
        self.rect = self.image.get_rect(center=pos)
        
        # Movement
        self.direction = pygame.Vector2()
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 100  # Pixels per second
        self.knockback = False
        self.knockback_duration = 200  # Milliseconds
        self.knockback_start = None
        self.knockback_direction = pygame.Vector2()

        # Health system
        self.max_health = 3
        self.current_health = self.max_health
        
        # Score value
        self.score_value = 100  # Points awarded when killed
    
    def import_assets(self):
        self.animations = []
        path = join('images', 'enemies', 'blob')
        for image_name in sorted(os.listdir(path)):
            if image_name.endswith('.png'):
                full_path = join(path, image_name)
                self.animations.append(pygame.image.load(full_path).convert_alpha())
    
    def get_direction(self):
        if not self.knockback:
            # Get direction to player
            enemy_pos = pygame.Vector2(self.rect.center)
            player_pos = pygame.Vector2(self.player.rect.center)
            self.direction = (player_pos - enemy_pos).normalize()
        
    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.animations):
            self.frame_index = 0
        self.image = self.animations[int(self.frame_index)]
    
    def check_collision(self, direction):
        # Check collision with obstacles
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:  
                        self.rect.right = sprite.rect.left
                    elif self.direction.x < 0:  
                        self.rect.left = sprite.rect.right
                    self.pos.x = self.rect.centerx
                    self.direction.x = 0
                elif direction == 'vertical':
                    if self.direction.y > 0: 
                        self.rect.bottom = sprite.rect.top
                    elif self.direction.y < 0: 
                        self.rect.top = sprite.rect.bottom
                    self.pos.y = self.rect.centery
                    self.direction.y = 0
        
        # Check collision with player
        if self.rect.colliderect(self.player.rect) and not self.knockback:
            # Apply knockback
            self.knockback = True
            self.knockback_start = pygame.time.get_ticks()
            # Get knockback direction (away from player)
            self.knockback_direction = (pygame.Vector2(self.rect.center) - 
                                      pygame.Vector2(self.player.rect.center)).normalize()
            # Player takes damage
            self.player.take_damage()

        for bullet in self.player.bullet_sprites:
            if self.rect.colliderect(bullet.rect):
                self.current_health -= 1
                bullet.kill()  
                # Apply knockback from bullet
                self.knockback = True
                self.knockback_start = pygame.time.get_ticks()
                self.knockback_direction = pygame.Vector2(bullet.direction)

                # Check if enemy died
                if self.current_health <= 0:
                    self.player.game.increase_score(self.score_value)  
                    self.kill()
                break
    
    def handle_knockback(self):
        if self.knockback:
            current_time = pygame.time.get_ticks()
            if current_time - self.knockback_start >= self.knockback_duration:
                self.knockback = False
            else:
                # Move in knockback direction
                self.direction = self.knockback_direction
    
    def move(self, dt):
        # Horizontal movement
        if self.knockback:
            self.pos.x += self.direction.x * self.speed * 2 * dt  # Faster knockback
        else:
            self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.check_collision('horizontal')
        
        # Vertical movement
        if self.knockback:
            self.pos.y += self.direction.y * self.speed * 2 * dt  # Faster knockback
        else:
            self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = round(self.pos.y)
        self.check_collision('vertical')
    
    def update(self, dt):
        self.handle_knockback()
        self.get_direction()
        self.move(dt)
        self.animate(dt)
