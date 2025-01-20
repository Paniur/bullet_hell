from settings import *
from enum import Enum
from gun import Gun
from bullet import Bullet
class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    IDLE = 'idle'
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, game):
        super().__init__(groups)
        self.game = game  # Store reference to game instance
        self.load_images()
        self.state = Direction.DOWN
        self.index = 0
        self.image = self.frames[self.state][0]
        self.rect = self.image.get_rect(center = pos)
        self.hitbox_rect = self.rect.inflate(-30, -40)
        self.direction = pygame.Vector2()
        self.speed = 600
        self.pos = pygame.Vector2(pos)
        self.collision_sprites = collision_sprites
        self.all_sprites = groups
        self.bullet_sprites = pygame.sprite.Group()
        self.gun = Gun(self, groups, 'Nambu type 14 ww2.png')  # Start with Nambu pistol

        # Health system
        self.max_health = 5
        self.current_health = self.max_health
        self.invulnerable = False
        self.invulnerable_time = None
        self.invulnerable_duration = 500  # 0.5 seconds of invulnerability after being hit

    def load_images(self):
        # Define scale factor (adjust these values to make player bigger or smaller)
        SCALE_FACTOR = 3  # This will double the size of the sprites
        
        self.frames = {
            Direction.UP: [],
            Direction.DOWN: [],
            Direction.LEFT: [],
            Direction.RIGHT: [],
            Direction.IDLE: []
        }
        
        # Load running animations
        run_sheet_mapping = {
            Direction.UP: 'SMS_Soldier_RUN_NORTH_strip4.png',
            Direction.DOWN: 'SMS_Soldier_RUN_SOUTH_strip4.png',
            Direction.LEFT: 'SMS_Soldier_RUN_WEST_strip4.png',
            Direction.RIGHT: 'SMS_Soldier_RUN_EAST_strip4.png'
        }
        
        for direction, sheet_name in run_sheet_mapping.items():
            sheet = pygame.image.load(join('images', 'soldier', 'RUN', sheet_name)).convert_alpha()
            sheet_width = sheet.get_width()
            frame_width = sheet_width // 4  # 4 frames in each strip
            
            for i in range(4):
                frame_surface = pygame.Surface((frame_width, sheet.get_height()), pygame.SRCALPHA)
                frame_surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet.get_height()))
                # Scale the frame
                scaled_frame = pygame.transform.scale(frame_surface, 
                    (int(frame_width * SCALE_FACTOR), 
                     int(sheet.get_height() * SCALE_FACTOR)))
                self.frames[direction].append(scaled_frame)
        
        # Load idle animations
        idle_sheet_mapping = {
            Direction.UP: 'SMS_Soldier_IDLE_NORTH_strip4.png',
            Direction.DOWN: 'SMS_Soldier_SOUTH_strip4.png',
            Direction.LEFT: 'SMS_Soldier_IDLE_WEST_strip4.png',
            Direction.RIGHT: 'SMS_Soldier_IDLE_EAST_strip4.png'
        }
        
        for direction, sheet_name in idle_sheet_mapping.items():
            sheet = pygame.image.load(join('images', 'soldier', 'IDLE', sheet_name)).convert_alpha()
            sheet_width = sheet.get_width()
            frame_width = sheet_width // 4  # 4 frames in each strip
            
            for i in range(4):
                frame_surface = pygame.Surface((frame_width, sheet.get_height()), pygame.SRCALPHA)
                frame_surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet.get_height()))
                # Scale the frame
                scaled_frame = pygame.transform.scale(frame_surface, 
                    (int(frame_width * SCALE_FACTOR), 
                     int(sheet.get_height() * SCALE_FACTOR)))
                self.frames[Direction.IDLE].append(scaled_frame)

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

        # Handle shooting
        if pygame.mouse.get_pressed()[0]:
            if self.gun.shoot():  # Only create bullet if gun can shoot
                pos = self.gun.rect.center + self.gun.player_direction * 50
                Bullet('bullet_red.png', pos, self.gun.player_direction, 
                      (self.all_sprites, self.bullet_sprites))

        # Handle manual reload with R key
        if keys[pygame.K_r]:
            self.gun.reload()

    def move(self, dt):
        movementX = self.direction.x * self.speed * dt
        self.pos.x += movementX
        self.hitbox_rect.centerx = round(self.pos.x)
        self.collision('horizontal')

        movementY = self.direction.y * self.speed * dt
        self.pos.y += movementY
        self.hitbox_rect.centery = round(self.pos.y)
        self.collision('vertical')

        self.rect.center = self.hitbox_rect.center

    def animate(self, dt):

        if self.direction.x != 0:
            self.state = Direction.RIGHT if self.direction.x > 0 else Direction.LEFT
        if self.direction.y != 0:
            self.state = Direction.DOWN if self.direction.y > 0 else Direction.UP

        if self.direction == pygame.Vector2(0,0):
            self.index = 0
            self.state = Direction.IDLE
        else:
            self.index += 10*dt
        self.image = self.frames[self.state][int(self.index) % len(self.frames[self.state])]

    def take_damage(self):
        if not self.invulnerable:
            self.current_health -= 1
            self.invulnerable = True
            self.invulnerable_time = pygame.time.get_ticks()
            if self.current_health <= 0:
                self.kill()  # Player dies

    def check_invulnerability(self):
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_time >= self.invulnerable_duration:
                self.invulnerable = False

    def update(self, dt):
        self.input()
        self.check_invulnerability()
        self.move(dt)
        self.animate(dt)

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:  
                        self.hitbox_rect.right = sprite.rect.left
                        self.pos.x = self.hitbox_rect.centerx  

                    if self.direction.x < 0:  
                        self.hitbox_rect.left = sprite.rect.right
                        self.pos.x = self.hitbox_rect.centerx 

                else:
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                        self.pos.y = self.hitbox_rect.centery  

                    if self.direction.y < 0:  
                        self.hitbox_rect.top = sprite.rect.bottom
                        self.pos.y = self.hitbox_rect.centery  
