from settings import *
from math import atan2, degrees
class Bullet(pygame.sprite.Sprite):
    def __init__(self, name, pos, direction, groups):
        super().__init__(groups)
        
        # Define scale factor for bullet
        SCALE_FACTOR = 4  # Adjust this value to change bullet size
        
        # Find and load the bullet image from any subfolder
        bullet_path = None
        for folder_path, _, file_names in walk(join('images', 'gun')):
            if name in file_names:
                bullet_path = join(folder_path, name)
                break
        
        if bullet_path is None:
            raise ValueError(f"Bullet image {name} not found in any gun folder")

        # Load and scale the bullet image
        original_image = pygame.image.load(bullet_path).convert_alpha()
        original_size = original_image.get_size()
        self.image = pygame.transform.scale(original_image, 
            (int(original_size[0] * SCALE_FACTOR), 
             int(original_size[1] * SCALE_FACTOR)))
        
        self.rect = self.image.get_rect(center=pos)
        
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000
        self.speed = 1400
        self.direction = direction
        self.bullet = True
        angle = degrees(atan2(self.direction.x, self.direction.y)) - 90
        self.image = pygame.transform.rotozoom(self.image, angle, 1)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
