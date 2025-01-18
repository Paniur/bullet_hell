from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, name, pos, direction, groups):
        super().__init__(groups)
        
        # Find and load the bullet image from any subfolder
        bullet_path = None
        for folder_path, _, file_names in walk(join('images', 'gun')):
            if name in file_names:
                bullet_path = join(folder_path, name)
                break
        
        if bullet_path is None:
            raise ValueError(f"Bullet image {name} not found in any gun folder")

        self.image = pygame.image.load(bullet_path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000
        self.speed = 1400
        self.direction = direction
        self.bullet = True

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
