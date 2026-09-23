"""
fruit.py

Defines the Fruit and Bomb classes, handling their physics and rendering.
"""
import pygame
import random
from settings import WIDTH, HEIGHT, RED, YELLOW, ORANGE, GREEN, BLACK, WHITE

# Increased radii for a better slicing experience
FRUIT_TYPES = [
    {"name": "Apple", "color": RED, "radius": 50, "points": 1},
    {"name": "Banana", "color": YELLOW, "radius": 45, "points": 1},
    {"name": "Orange", "color": ORANGE, "radius": 50, "points": 1},
    {"name": "Watermelon", "color": GREEN, "radius": 60, "points": 2},
]

class Fruit:
    def __init__(self, difficulty_speed_multiplier=1.0):
        self.type = random.choice(FRUIT_TYPES)
        self.name = self.type["name"]
        self.color = self.type["color"]
        self.radius = self.type["radius"]
        self.points = self.type["points"]
        
        # Spawn at random x, below screen. Keep away from absolute edges.
        self.x = random.randint(150, WIDTH - 150)
        self.y = HEIGHT + self.radius
        
        # Calculate a trajectory aimed generally towards the center of the screen
        target_x = random.randint(WIDTH // 4, 3 * WIDTH // 4)
        dx = target_x - self.x
        
        # Reduced speeds by ~35% for better gameplay pacing
        self.vx = (dx / 120.0) * difficulty_speed_multiplier
        self.vy = random.uniform(-13, -16) * difficulty_speed_multiplier
        
        # Smoother, lower gravity to complement reduced vertical speed
        self.gravity = 0.25 * difficulty_speed_multiplier
        
        self.sliced = False
        self.is_bomb = False
        
        self.halves = []
        
    def update(self):
        if not self.sliced:
            self.x += self.vx
            self.y += self.vy
            self.vy += self.gravity
        else:
            for half in self.halves:
                half['x'] += half['vx']
                half['y'] += half['vy']
                half['vy'] += self.gravity

    def draw(self, surface):
        if not self.sliced:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            # Inner details
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x) - 10, int(self.y) - 10), int(self.radius * 0.25))
        else:
            # Draw halves
            for half in self.halves:
                pygame.draw.circle(surface, self.color, (int(half['x']), int(half['y'])), self.radius // 2)

    def slice(self, velocity_x, velocity_y):
        self.sliced = True
        
        # Dynamic push force based on the slice velocity
        push_x = min(max(abs(velocity_y) * 0.05, 2), 6)
        push_y = min(max(abs(velocity_x) * 0.05, 1), 5)
        
        # Separate halves cleanly
        self.halves.append({
            'x': self.x - 20, 'y': self.y,
            'vx': self.vx - push_x,
            'vy': self.vy - push_y,
        })
        self.halves.append({
            'x': self.x + 20, 'y': self.y,
            'vx': self.vx + push_x,
            'vy': self.vy + push_y,
        })

class Bomb(Fruit):
    def __init__(self, difficulty_speed_multiplier=1.0):
        super().__init__(difficulty_speed_multiplier)
        self.name = "Bomb"
        self.color = BLACK
        self.radius = 45
        self.points = 0
        self.is_bomb = True
        
    def draw(self, surface):
        if not self.sliced:
            # Bomb body
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            # Bomb fuse
            pygame.draw.line(surface, RED, (int(self.x), int(self.y) - self.radius), 
                             (int(self.x) + 20, int(self.y) - self.radius - 20), 5)
            # Spark effect
            spark_size = random.randint(4, 8)
            pygame.draw.circle(surface, YELLOW, (int(self.x) + 20, int(self.y) - self.radius - 20), spark_size)
        else:
            # Explosion effect
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), self.radius * 3)
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), int(self.radius * 2.5))
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), int(self.radius * 1.5))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        
        import math
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 15)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.color = color
        self.life = 255.0
        self.decay = random.uniform(8.0, 15.0)
        self.radius = random.uniform(3, 10)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.4 # Higher gravity for juice drops
        
        self.life -= self.decay
        self.radius = max(0, self.radius - 0.15)
        
    def draw(self, surface):
        if self.life > 0 and self.radius > 0:
            alpha = int(max(0, self.life))
            temp_surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (*self.color, alpha), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(temp_surface, (int(self.x - self.radius), int(self.y - self.radius)))

class FloatingText:
    def __init__(self, x, y, text, color, is_combo=False):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 255.0
        self.vy = -1.5 if not is_combo else -3.0
        self.is_combo = is_combo
        self.scale = 1.0 if not is_combo else 1.5
        
    def update(self):
        self.y += self.vy
        self.life -= 4.0 if not self.is_combo else 3.0
        
    def draw(self, surface):
        if self.life > 0:
            alpha = int(max(0, min(255, self.life)))
            font_size = int(36 * self.scale)
            font = pygame.font.Font(None, font_size)
            
            # Shadow
            shadow = font.render(self.text, True, (0, 0, 0))
            shadow.set_alpha(alpha)
            surface.blit(shadow, (self.x - shadow.get_width()//2 + 2, self.y - shadow.get_height()//2 + 2))
            
            # Text
            text_surf = font.render(self.text, True, self.color)
            text_surf.set_alpha(alpha)
            surface.blit(text_surf, (self.x - text_surf.get_width()//2, self.y - text_surf.get_height()//2))
