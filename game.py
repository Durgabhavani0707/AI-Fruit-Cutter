"""
game.py

Manages game state, logic, scores, and difficulty progression.
"""
import json
import os
import pygame
import random
from settings import (
    HIGH_SCORE_FILE, STARTING_LIVES, COMBO_TIME_WINDOW, 
    DIFFICULTY_LEVELS, WIDTH, HEIGHT, MODE_CLASSIC
)
from fruit import Fruit, Bomb, Particle, FloatingText
from collision import line_intersects_circle

class Game:
    def __init__(self):
        self.state = "MENU" # MENU, PLAYING, GAME_OVER
        self.mode = MODE_CLASSIC
        self.score = 0
        self.high_score = self.load_high_score()
        self.lives = STARTING_LIVES
        
        self.fruits = []
        self.particles = []
        self.floating_texts = []
        self.screen_shake_timer = 0
        
        # Difficulty handling
        self.difficulty_level = 0
        self.last_spawn_time = pygame.time.get_ticks()
        
        # Combo handling
        self.combo = 0
        self.last_slice_time = 0
        
    def load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
            except:
                return 0
        return 0

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open(HIGH_SCORE_FILE, "w") as f:
                json.dump({"high_score": self.high_score}, f)

    def start_game(self):
        self.state = "PLAYING"
        self.score = 0
        self.lives = STARTING_LIVES
        self.fruits = []
        self.particles = []
        self.floating_texts = []
        self.screen_shake_timer = 0
        self.difficulty_level = 0
        self.combo = 0
        self.last_spawn_time = pygame.time.get_ticks()

    def game_over(self):
        self.state = "GAME_OVER"
        self.save_high_score()

    def get_current_difficulty(self):
        # Determine difficulty based on score
        current_diff = DIFFICULTY_LEVELS[0]
        for idx, diff in enumerate(DIFFICULTY_LEVELS):
            if self.score >= diff["score"]:
                self.difficulty_level = idx
                current_diff = diff
            else:
                break
        return current_diff

    def update(self, current_time, finger_pos, prev_finger_pos):
        if self.state != "PLAYING":
            return

        diff_settings = self.get_current_difficulty()

        # Check combo reset
        if current_time - self.last_slice_time > COMBO_TIME_WINDOW:
            self.combo = 0

        # Spawn fruits
        if current_time - self.last_spawn_time > diff_settings["spawn_rate"]:
            self.last_spawn_time = current_time
            if len(self.fruits) < diff_settings["max_fruits"]:
                if random.random() < diff_settings["bomb_chance"]:
                    self.fruits.append(Bomb(diff_settings["speed_multiplier"]))
                else:
                    # Spawn 1 to 3 fruits at once sometimes
                    num_to_spawn = random.randint(1, min(3, diff_settings["max_fruits"] - len(self.fruits) + 1))
                    for _ in range(num_to_spawn):
                        self.fruits.append(Fruit(diff_settings["speed_multiplier"]))

        # Update fruits
        for fruit in self.fruits[:]:
            fruit.update()
            
            # Check collisions if not sliced and we have a trail
            if not fruit.sliced and finger_pos and prev_finger_pos:
                if line_intersects_circle(prev_finger_pos, finger_pos, (fruit.x, fruit.y), fruit.radius):
                    self.slice_fruit(fruit, current_time, finger_pos, prev_finger_pos)

            # Check if fruit fell off screen
            if fruit.y - fruit.radius > HEIGHT and not fruit.sliced:
                self.fruits.remove(fruit)
                if not fruit.is_bomb:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over()
            # Remove sliced fruits when halves fall off
            elif fruit.sliced:
                # Simplification: remove if all halves are off screen
                if all(half['y'] > HEIGHT for half in fruit.halves):
                    self.fruits.remove(fruit)

        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
                
        # Update floating texts
        for ft in self.floating_texts[:]:
            ft.update()
            if ft.life <= 0:
                self.floating_texts.remove(ft)

    def slice_fruit(self, fruit, current_time, finger_pos, prev_finger_pos):
        vx = finger_pos[0] - prev_finger_pos[0]
        vy = finger_pos[1] - prev_finger_pos[1]
        
        fruit.slice(vx, vy)
        
        if fruit.is_bomb:
            self.game_over()
        else:
            # Combo logic
            if current_time - self.last_slice_time <= COMBO_TIME_WINDOW:
                self.combo += 1
            else:
                self.combo = 1
                
            self.last_slice_time = current_time
            
            # Add points (with combo multiplier)
            points_earned = fruit.points * self.combo
            self.score += points_earned
            
            # Screen shake trigger
            self.screen_shake_timer = 150 # ms
            
            # Floating Text
            text_col = (255, 255, 255) if self.combo == 1 else (255, 215, 0)
            self.floating_texts.append(FloatingText(fruit.x, fruit.y, f"+{points_earned}", text_col, False))
            
            if self.combo > 1:
                self.floating_texts.append(FloatingText(fruit.x, fruit.y - 40, f"{self.combo}x COMBO!", (255, 100, 100), True))
            
            # Spawn splash particles
            for _ in range(15):
                self.particles.append(Particle(fruit.x, fruit.y, fruit.color))

    def draw(self, surface):
        for fruit in self.fruits:
            fruit.draw(surface)
            
        for p in self.particles:
            p.draw(surface)
            
        for ft in self.floating_texts:
            ft.draw(surface)
