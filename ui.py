"""
ui.py

Handles UI drawing (Score, Lives, Game Over screen).
"""
import pygame
from settings import WIDTH, HEIGHT, WHITE, BLACK, RED, BLUE

class UI:
    def __init__(self):
        pygame.font.init()
        self.font_large = pygame.font.SysFont('Arial', 64, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 24)

    def draw_hud(self, surface, score, high_score, lives, combo, fps):
        """Draw HUD elements: Score, High Score, Lives, FPS, Combo"""
        # Background bar for HUD
        hud_bg = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 150))
        surface.blit(hud_bg, (0, 0))

        # Score
        score_text = self.font_medium.render(f"Score: {score}", True, WHITE)
        surface.blit(score_text, (20, 10))

        # High Score
        hs_text = self.font_medium.render(f"High Score: {high_score}", True, WHITE)
        surface.blit(hs_text, (250, 10))

        # FPS
        fps_text = self.font_small.render(f"FPS: {int(fps)}", True, (0, 255, 255))
        surface.blit(fps_text, (WIDTH - 120, 15))

        # Combo
        if combo > 1:
            combo_text = self.font_large.render(f"{combo}x COMBO!", True, (255, 215, 0)) # Gold
            surface.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 80))

        # Lives (Hearts)
        heart_color = RED
        for i in range(lives):
            x = WIDTH - 200 + (i * 40)
            y = 25
            self.draw_heart(surface, x, y, 15, heart_color)

    def draw_heart(self, surface, x, y, size, color):
        """Helper to draw a simple heart shape."""
        # Simple placeholder for heart: two circles and a triangle
        pygame.draw.circle(surface, color, (x - size // 2, y - size // 2), size // 2)
        pygame.draw.circle(surface, color, (x + size // 2, y - size // 2), size // 2)
        pygame.draw.polygon(surface, color, [
            (x - size, y - size // 2),
            (x + size, y - size // 2),
            (x, y + size)
        ])

    def draw_game_over(self, surface, score, high_score):
        # Darken screen
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Texts
        go_text = self.font_large.render("GAME OVER", True, RED)
        score_text = self.font_medium.render(f"Final Score: {score}", True, WHITE)
        hs_text = self.font_medium.render(f"High Score: {high_score}", True, (255, 215, 0))

        surface.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 3))
        surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 3 + 80))
        surface.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, HEIGHT // 3 + 130))

    def draw_restart_button(self, surface, rect, is_hovering, progress):
        current_time = pygame.time.get_ticks()
        if not hasattr(self, 'hover_anim'):
            self.hover_anim = 0.0
            self.last_time = current_time
        
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Smooth hover scale (200ms)
        if is_hovering:
            self.hover_anim = min(1.0, self.hover_anim + dt / 200.0)
        else:
            self.hover_anim = max(0.0, self.hover_anim - dt / 200.0)
            
        ease = 1.0 - (1.0 - self.hover_anim) ** 3 # Cubic ease out for smoother feel
        
        # Flash scale
        flash_scale = 0.05 if progress >= 1.0 else 0.0
        scale = 1.0 + 0.10 * ease + flash_scale
        
        # Animate upward 10 pixels
        y_offset = -10 * ease
        
        # New dimensions
        w = int(rect.width * scale)
        h = int(rect.height * scale)
        x = rect.centerx - w // 2
        y = rect.centery - h // 2 + y_offset
        anim_rect = pygame.Rect(x, y, w, h)
        
        # Brighten color based on hover
        base_color = (0, 120, 60)
        hover_color = (0, 220, 110)
        
        # Pulse while hovering
        pulse = 0
        if is_hovering and progress < 1.0:
            import math
            pulse = (math.sin(current_time / 150.0) + 1.0) * 0.5 * 30
            
        r = int(base_color[0] + (hover_color[0] - base_color[0]) * ease + pulse)
        g = int(base_color[1] + (hover_color[1] - base_color[1]) * ease + pulse)
        b = int(base_color[2] + (hover_color[2] - base_color[2]) * ease + pulse)
        
        if progress >= 1.0:
            # White flash
            r, g, b = 255, 255, 255
            
        r, g, b = min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))
        
        # Soft glow
        if ease > 0.01:
            glow_surface = pygame.Surface((w + 40, h + 40), pygame.SRCALPHA)
            for i in range(4):
                alpha = int(40 * ease * (1.0 - i/4.0))
                pygame.draw.rect(glow_surface, (0, 255, 120, alpha), 
                                 (20 - i*3, 20 - i*3, w + i*6, h + i*6), border_radius=15 + i*3)
            surface.blit(glow_surface, (x - 20, y - 20))
            
        # Draw base button
        pygame.draw.rect(surface, (r, g, b), anim_rect, border_radius=15)
        
        # Draw faint static border
        static_border_color = (0, 150, 75)
        if ease == 0:
            static_border_color = WHITE
        pygame.draw.rect(surface, static_border_color, anim_rect, max(2, int(2 * scale)), border_radius=15)
        
        # Draw the animated loading border
        if progress > 0 and progress < 1.0:
            self._draw_partial_rounded_rect(surface, anim_rect, 15, 4, progress)
        
        # Text
        text_color = (0, 120, 60) if progress >= 1.0 else WHITE
        text = self.font_medium.render("RESTART", True, text_color)
        text_x = anim_rect.centerx - text.get_width() // 2
        text_y = anim_rect.centery - text.get_height() // 2
        surface.blit(text, (text_x, text_y))

    def draw_main_menu(self, surface):
        # Main Menu placeholder
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        title = self.font_large.render("FRUIT CUTTER AI", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        
        prompt = self.font_medium.render("Raise your hand and wave to start", True, WHITE)
        surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 50))

    def _draw_partial_rounded_rect(self, surface, rect, radius, thickness, progress):
        if progress <= 0: return
        import math
        
        # Supersample for anti-aliasing
        scale = 2
        w = rect.width * scale
        h = rect.height * scale
        r = radius * scale
        t = thickness * scale
        
        temp_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        points = []
        # Top edge
        points.append((r, t/2))
        points.append((w - r, t/2))
        # Top-Right arc
        arc_pts = 20 # Increased resolution for smoother corners
        for i in range(1, arc_pts + 1):
            angle = math.radians(270 + 90 * (i / arc_pts))
            points.append((w - r + (r - t/2) * math.cos(angle), r + (r - t/2) * math.sin(angle)))
        # Right edge
        points.append((w - t/2, r))
        points.append((w - t/2, h - r))
        # Bottom-Right arc
        for i in range(1, arc_pts + 1):
            angle = math.radians(0 + 90 * (i / arc_pts))
            points.append((w - r + (r - t/2) * math.cos(angle), h - r + (r - t/2) * math.sin(angle)))
        # Bottom edge
        points.append((w - r, h - t/2))
        points.append((r, h - t/2))
        # Bottom-Left arc
        for i in range(1, arc_pts + 1):
            angle = math.radians(90 + 90 * (i / arc_pts))
            points.append((r + (r - t/2) * math.cos(angle), h - r + (r - t/2) * math.sin(angle)))
        # Left edge
        points.append((t/2, h - r))
        points.append((t/2, r))
        # Top-Left arc
        for i in range(1, arc_pts + 1):
            angle = math.radians(180 + 90 * (i / arc_pts))
            points.append((r + (r - t/2) * math.cos(angle), r + (r - t/2) * math.sin(angle)))
        # Close the loop perfectly
        points.append((r, t/2))
        
        # Calculate segments and lengths
        lengths = []
        total_len = 0
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i+1]
            dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
            lengths.append(dist)
            total_len += dist
            
        target_len = total_len * progress
        
        # Build sub path
        sub_points = [points[0]]
        current_len = 0
        for i in range(len(points) - 1):
            seg_len = lengths[i]
            if current_len + seg_len <= target_len:
                sub_points.append(points[i+1])
                current_len += seg_len
            else:
                # Interpolate
                remaining = target_len - current_len
                fraction = remaining / seg_len if seg_len > 0 else 0
                p1 = points[i]
                p2 = points[i+1]
                end_x = p1[0] + (p2[0] - p1[0]) * fraction
                end_y = p1[1] + (p2[1] - p1[1]) * fraction
                sub_points.append((end_x, end_y))
                break
                
        # Draw sub path
        if len(sub_points) > 1:
            pygame.draw.lines(temp_surf, WHITE, False, sub_points, int(t))
            for p in sub_points:
                pygame.draw.circle(temp_surf, WHITE, (int(p[0]), int(p[1])), int(t/2))
                
        final_surf = pygame.transform.smoothscale(temp_surf, (rect.width, rect.height))
        surface.blit(final_surf, rect.topleft)


