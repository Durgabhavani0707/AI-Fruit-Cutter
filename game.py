"""
game.py

Manages:
- Game state
- Fruit spawning
- Fruit slicing
- Bombs
- Score
- High score
- Lives
- Combo system
- Difficulty progression
- Particles
- Floating score text
- Screen shake
"""

import json
import os
import random
import pygame

from settings import (
    HIGH_SCORE_FILE,
    STARTING_LIVES,
    COMBO_TIME_WINDOW,
    DIFFICULTY_LEVELS,
    WIDTH,
    HEIGHT,
    MODE_CLASSIC,
)

from fruit import Fruit, Bomb, Particle, FloatingText
from collision import line_intersects_circle


class Game:

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):

        # Game states:
        # MENU
        # PLAYING
        # GAME_OVER

        self.state = "MENU"

        self.mode = MODE_CLASSIC

        # -----------------------------------------------------
        # Score
        # -----------------------------------------------------

        self.score = 0
        self.high_score = self.load_high_score()

        # -----------------------------------------------------
        # Player
        # -----------------------------------------------------

        self.lives = STARTING_LIVES

        # -----------------------------------------------------
        # Game objects
        # -----------------------------------------------------

        self.fruits = []
        self.particles = []
        self.floating_texts = []

        # -----------------------------------------------------
        # Effects
        # -----------------------------------------------------

        self.screen_shake_timer = 0

        # -----------------------------------------------------
        # Difficulty
        # -----------------------------------------------------

        self.difficulty_level = 0

        self.last_spawn_time = pygame.time.get_ticks()

        # -----------------------------------------------------
        # Combo
        # -----------------------------------------------------

        self.combo = 0
        self.last_slice_time = 0

        # -----------------------------------------------------
        # Statistics
        # -----------------------------------------------------

        self.total_slices = 0
        self.fruits_missed = 0
        self.bombs_sliced = 0

    # =========================================================
    # HIGH SCORE
    # =========================================================

    def load_high_score(self):

        if not os.path.exists(HIGH_SCORE_FILE):
            return 0

        try:

            with open(
                HIGH_SCORE_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            return int(
                data.get("high_score", 0)
            )

        except (
            OSError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ):

            return 0

    # =========================================================
    # SAVE HIGH SCORE
    # =========================================================

    def save_high_score(self):

        if self.score <= self.high_score:
            return

        self.high_score = self.score

        try:

            # Make sure the directory exists
            directory = os.path.dirname(
                HIGH_SCORE_FILE
            )

            if directory:
                os.makedirs(
                    directory,
                    exist_ok=True
                )

            with open(
                HIGH_SCORE_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    {
                        "high_score": self.high_score
                    },
                    file,
                    indent=4
                )

        except OSError as error:

            print(
                f"Could not save high score: {error}"
            )

    # =========================================================
    # START GAME
    # =========================================================

    def start_game(self):

        self.state = "PLAYING"

        # -----------------------------------------------------
        # Reset score
        # -----------------------------------------------------

        self.score = 0

        # -----------------------------------------------------
        # Reset lives
        # -----------------------------------------------------

        self.lives = STARTING_LIVES

        # -----------------------------------------------------
        # Clear objects
        # -----------------------------------------------------

        self.fruits.clear()
        self.particles.clear()
        self.floating_texts.clear()

        # -----------------------------------------------------
        # Reset effects
        # -----------------------------------------------------

        self.screen_shake_timer = 0

        # -----------------------------------------------------
        # Reset difficulty
        # -----------------------------------------------------

        self.difficulty_level = 0

        # -----------------------------------------------------
        # Reset combo
        # -----------------------------------------------------

        self.combo = 0
        self.last_slice_time = 0

        # -----------------------------------------------------
        # Reset statistics
        # -----------------------------------------------------

        self.total_slices = 0
        self.fruits_missed = 0
        self.bombs_sliced = 0

        # -----------------------------------------------------
        # Reset spawning timer
        # -----------------------------------------------------

        self.last_spawn_time = pygame.time.get_ticks()

    # =========================================================
    # GAME OVER
    # =========================================================

    def game_over(self):

        if self.state == "GAME_OVER":
            return

        self.state = "GAME_OVER"

        # Save high score
        self.save_high_score()

    # =========================================================
    # GET CURRENT DIFFICULTY
    # =========================================================

    def get_current_difficulty(self):

        current_diff = DIFFICULTY_LEVELS[0]

        self.difficulty_level = 0

        for index, difficulty in enumerate(
            DIFFICULTY_LEVELS
        ):

            if self.score >= difficulty["score"]:

                self.difficulty_level = index
                current_diff = difficulty

            else:
                break

        return current_diff

    # =========================================================
    # SPAWN FRUITS
    # =========================================================

    def spawn_fruits(self, diff_settings):

        max_fruits = diff_settings["max_fruits"]

        # How many objects currently exist
        current_count = len(self.fruits)

        if current_count >= max_fruits:
            return

        available_slots = (
            max_fruits - current_count
        )

        # -----------------------------------------------------
        # Bomb chance
        # -----------------------------------------------------

        bomb_chance = diff_settings.get(
            "bomb_chance",
            0.0
        )

        if random.random() < bomb_chance:

            self.fruits.append(
                Bomb(
                    diff_settings[
                        "speed_multiplier"
                    ]
                )
            )

            return

        # -----------------------------------------------------
        # Normal fruit spawning
        # -----------------------------------------------------

        max_spawn = min(
            3,
            available_slots
        )

        number_to_spawn = random.randint(
            1,
            max_spawn
        )

        for _ in range(number_to_spawn):

            if len(self.fruits) >= max_fruits:
                break

            self.fruits.append(
                Fruit(
                    diff_settings[
                        "speed_multiplier"
                    ]
                )
            )

    # =========================================================
    # UPDATE GAME
    # =========================================================

    def update(
        self,
        current_time,
        finger_pos,
        prev_finger_pos
    ):

        if self.state != "PLAYING":
            return

        # -----------------------------------------------------
        # Get current difficulty
        # -----------------------------------------------------

        diff_settings = (
            self.get_current_difficulty()
        )

        # =====================================================
        # COMBO RESET
        # =====================================================

        if (
            self.combo > 0
            and current_time - self.last_slice_time
            > COMBO_TIME_WINDOW
        ):

            self.combo = 0

        # =====================================================
        # FRUIT SPAWNING
        # =====================================================

        spawn_rate = diff_settings.get(
            "spawn_rate",
            1000
        )

        if (
            current_time - self.last_spawn_time
            >= spawn_rate
        ):

            self.last_spawn_time = current_time

            self.spawn_fruits(
                diff_settings
            )

        # =====================================================
        # UPDATE FRUITS
        # =====================================================

        fruits_to_remove = []

        for fruit in self.fruits:

            # -------------------------------------------------
            # Update physics
            # -------------------------------------------------

            fruit.update()

            # -------------------------------------------------
            # Collision / slicing
            # -------------------------------------------------

            if (
                not fruit.sliced
                and finger_pos is not None
                and prev_finger_pos is not None
            ):

                hit = line_intersects_circle(
                    prev_finger_pos,
                    finger_pos,
                    (fruit.x, fruit.y),
                    fruit.radius
                )

                if hit:

                    self.slice_fruit(
                        fruit,
                        current_time,
                        finger_pos,
                        prev_finger_pos
                    )

            # -------------------------------------------------
            # Fruit missed
            # -------------------------------------------------

            if (
                not fruit.sliced
                and fruit.y - fruit.radius > HEIGHT
            ):

                fruits_to_remove.append(
                    fruit
                )

                # Missing normal fruit costs a life
                if not fruit.is_bomb:

                    self.lives -= 1
                    self.fruits_missed += 1

                    # Reset combo when a fruit is missed
                    self.combo = 0

                    # Small screen shake
                    self.screen_shake_timer = max(
                        self.screen_shake_timer,
                        100
                    )

                    # Game over
                    if self.lives <= 0:

                        self.lives = 0

                        self.game_over()

            # -------------------------------------------------
            # Sliced fruit
            # -------------------------------------------------

            elif fruit.sliced:

                if self.sliced_fruit_off_screen(
                    fruit
                ):

                    fruits_to_remove.append(
                        fruit
                    )

        # -----------------------------------------------------
        # Remove fruits safely AFTER iteration
        # -----------------------------------------------------

        for fruit in fruits_to_remove:

            if fruit in self.fruits:

                self.fruits.remove(fruit)

        # =====================================================
        # PARTICLES
        # =====================================================

        particles_to_remove = []

        for particle in self.particles:

            particle.update()

            if particle.life <= 0:

                particles_to_remove.append(
                    particle
                )

        for particle in particles_to_remove:

            if particle in self.particles:

                self.particles.remove(
                    particle
                )

        # =====================================================
        # FLOATING TEXT
        # =====================================================

        texts_to_remove = []

        for floating_text in self.floating_texts:

            floating_text.update()

            if floating_text.life <= 0:

                texts_to_remove.append(
                    floating_text
                )

        for floating_text in texts_to_remove:

            if floating_text in self.floating_texts:

                self.floating_texts.remove(
                    floating_text
                )

        # =====================================================
        # SCREEN SHAKE
        # =====================================================

        if self.screen_shake_timer > 0:

            # Timer is reduced by main.py
            # so we don't change it here.

            self.screen_shake_timer = max(
                0,
                self.screen_shake_timer
            )

    # =========================================================
    # CHECK SLICED FRUIT OFF SCREEN
    # =========================================================

    def sliced_fruit_off_screen(self, fruit):

        if not fruit.halves:
            return True

        # Remove when every half has moved below screen
        return all(
            half["y"] > HEIGHT + 100
            for half in fruit.halves
        )

    # =========================================================
    # SLICE FRUIT
    # =========================================================

    def slice_fruit(
        self,
        fruit,
        current_time,
        finger_pos,
        prev_finger_pos
    ):

        # -----------------------------------------------------
        # Safety check
        # -----------------------------------------------------

        if fruit.sliced:
            return

        # -----------------------------------------------------
        # Calculate finger movement
        # -----------------------------------------------------

        velocity_x = (
            finger_pos[0]
            - prev_finger_pos[0]
        )

        velocity_y = (
            finger_pos[1]
            - prev_finger_pos[1]
        )

        # -----------------------------------------------------
        # Slice fruit
        # -----------------------------------------------------

        fruit.slice(
            velocity_x,
            velocity_y
        )

        # =====================================================
        # BOMB
        # =====================================================

        if fruit.is_bomb:

            self.bombs_sliced += 1

            # Big explosion effect
            self.create_bomb_explosion(
                fruit.x,
                fruit.y
            )

            # Strong screen shake
            self.screen_shake_timer = 500

            # Game over
            self.game_over()

            return

        # =====================================================
        # NORMAL FRUIT
        # =====================================================

        self.total_slices += 1

        # -----------------------------------------------------
        # COMBO
        # -----------------------------------------------------

        if (
            current_time - self.last_slice_time
            <= COMBO_TIME_WINDOW
        ):

            self.combo += 1

        else:

            self.combo = 1

        self.last_slice_time = current_time

        # -----------------------------------------------------
        # Calculate score
        # -----------------------------------------------------

        points_earned = (
            fruit.points * self.combo
        )

        self.score += points_earned

        # -----------------------------------------------------
        # Update high score immediately
        # -----------------------------------------------------

        if self.score > self.high_score:

            self.high_score = self.score

        # -----------------------------------------------------
        # Screen shake
        # -----------------------------------------------------

        self.screen_shake_timer = max(
            self.screen_shake_timer,
            150
        )

        # =====================================================
        # FLOATING SCORE
        # =====================================================

        if self.combo == 1:

            text_color = (
                255,
                255,
                255
            )

        else:

            text_color = (
                255,
                215,
                0
            )

        self.floating_texts.append(
            FloatingText(
                fruit.x,
                fruit.y,
                f"+{points_earned}",
                text_color,
                False
            )
        )

        # =====================================================
        # COMBO TEXT
        # =====================================================

        if self.combo >= 2:

            self.floating_texts.append(
                FloatingText(
                    fruit.x,
                    fruit.y - 40,
                    f"{self.combo}x COMBO!",
                    (
                        255,
                        100,
                        100
                    ),
                    True
                )
            )

        # =====================================================
        # FRUIT PARTICLES
        # =====================================================

        self.create_fruit_particles(
            fruit
        )

    # =========================================================
    # CREATE FRUIT PARTICLES
    # =========================================================

    def create_fruit_particles(self, fruit):

        # Watermelon gets slightly more particles
        if fruit.points >= 2:

            particle_count = 22

        else:

            particle_count = 15

        for _ in range(
            particle_count
        ):

            self.particles.append(
                Particle(
                    fruit.x,
                    fruit.y,
                    fruit.color
                )
            )

    # =========================================================
    # CREATE BOMB EXPLOSION
    # =========================================================

    def create_bomb_explosion(
        self,
        x,
        y
    ):

        # Explosion particles
        explosion_colors = [
            (255, 60, 0),
            (255, 140, 0),
            (255, 215, 0),
            (255, 255, 255),
        ]

        for _ in range(45):

            color = random.choice(
                explosion_colors
            )

            self.particles.append(
                Particle(
                    x,
                    y,
                    color
                )
            )

        # Explosion text
        self.floating_texts.append(
            FloatingText(
                x,
                y,
                "BOOM!",
                (
                    255,
                    80,
                    0
                ),
                True
            )
        )

    # =========================================================
    # DRAW
    # =========================================================

    def draw(self, surface):

        # -----------------------------------------------------
        # Draw fruits
        # -----------------------------------------------------

        for fruit in self.fruits:

            fruit.draw(surface)

        # -----------------------------------------------------
        # Draw particles
        # -----------------------------------------------------

        for particle in self.particles:

            particle.draw(surface)

        # -----------------------------------------------------
        # Draw floating text
        # -----------------------------------------------------

        for floating_text in self.floating_texts:

            floating_text.draw(surface)