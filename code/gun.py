from settings import *
from math import atan2, degrees

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups, name, shoot_cooldown=500):
        super().__init__(groups)
        self.player = player
        self.distance = 80
        self.player_direction = pygame.Vector2(1,0)

        # Find and load the gun image from any subfolder
        gun_path = None
        for folder_path, _, file_names in walk(join('images', 'gun')):
            if name in file_names:
                gun_path = join(folder_path, name)
                break
        
        if gun_path is None:
            raise ValueError(f"Gun image {name} not found in any gun folder")

        self.gun_surf = pygame.image.load(gun_path).convert_alpha()
        self.image = self.gun_surf
        #player_direction * distance creates a vector pointing in the direction we want
        # Adding this to the player's position places the gun at that distance from the player
        self.rect = self.image.get_rect(center = self.player.rect.center + self.player_direction * self.distance)

        self.gun = True
        
        # shooting setup
        self.can_shoot = True
        self.shoot_time = None
        self.shoot_cooldown = shoot_cooldown

        # Magazine system
        self.magazine_size = 12  # Number of bullets per magazine
        self.current_magazine = self.magazine_size
        self.is_reloading = False
        self.reload_time = None
        self.reload_duration = 1500  # 1.5 seconds to reload

    def reload(self):
        if not self.is_reloading and self.current_magazine < self.magazine_size:
            self.is_reloading = True
            self.reload_time = pygame.time.get_ticks()
            print('reloading...')  # Debug message

    def check_reload(self):
        if self.is_reloading:
            current_time = pygame.time.get_ticks()
            if current_time - self.reload_time >= self.reload_duration:
                self.current_magazine = self.magazine_size
                self.is_reloading = False
                self.can_shoot = True
                print('reload complete')  # Debug message
            
    def shoot(self):
        if self.can_shoot and self.current_magazine > 0 and not self.is_reloading:
            self.current_magazine -= 1
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            return True
        elif self.current_magazine <= 0 and not self.is_reloading:
            self.reload()
        return False

    def get_direction(self):
        mouse_position = pygame.Vector2(pygame.mouse.get_pos())
        # Player is always in the center of the screen 
        # The rect center of the player's is not in the center because of the offset for simulated camera
        player_position = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.player_direction = (mouse_position - player_position).normalize()

    def rotate_gun(self):
        # -90 because the gun sprite points to the right with you have 0 degrees should point up
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90

        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.flip(pygame.transform.rotozoom(self.gun_surf, abs(angle), 1), False, True)

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True

    def update(self, _):
        self.gun_timer()
        self.check_reload()
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance