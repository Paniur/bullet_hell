from settings import *

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        self.heart_surf = pygame.image.load(join('images', 'UI', 'heart.png')).convert_alpha()
        self.heart_width = self.heart_surf.get_width()

        self.font = pygame.font.Font(None, 36)  
        
    def show_health(self, current_health, max_health):
        for i in range(current_health):
            x = 10 + i * (self.heart_width + 5)  
            y = 10  
            self.display_surface.blit(self.heart_surf, (x, y))

    def show_ammo(self, current_ammo, max_ammo, is_reloading):
        # Create ammo text
        if is_reloading:
            ammo_text = "RELOADING..."
        else:
            ammo_text = f"{current_ammo}/{max_ammo}"
        
        text_surf = self.font.render(ammo_text, True, (0, 0, 0))  # Black text
        text_rect = text_surf.get_rect(topright=(WINDOW_WIDTH - 10, 10))  # 10px from right edge
        self.display_surface.blit(text_surf, text_rect)

    def show_score(self, score):
        # Render score text
        score_text = f"Score: {score}"
        text_surf = self.font.render(score_text, True, (0, 0, 0)) 
        text_rect = text_surf.get_rect(midtop=(WINDOW_WIDTH // 2, 10))  
        self.display_surface.blit(text_surf, text_rect)
