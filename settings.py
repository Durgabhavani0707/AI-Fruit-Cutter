"""
settings.py

Contains all configuration and settings for the Fruit Cutter AI game.
"""
import os

# Resolution
WIDTH = 1280
HEIGHT = 720
FPS = 60

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
HIGH_SCORE_FILE = os.path.join(BASE_DIR, "highscore.json")

# Game Modes
MODE_CLASSIC = "CLASSIC"
# Future modes: MODE_TIME_ATTACK = "TIME_ATTACK", MODE_ENDLESS = "ENDLESS"

# Game Settings
STARTING_LIVES = 3
COMBO_TIME_WINDOW = 1000  # ms within which multiple slices count as a combo

# Difficulty thresholds (score based)
DIFFICULTY_LEVELS = [
    {"score": 0, "spawn_rate": 2000, "speed_multiplier": 1.0, "max_fruits": 2, "bomb_chance": 0.1},
    {"score": 10, "spawn_rate": 1500, "speed_multiplier": 1.1, "max_fruits": 3, "bomb_chance": 0.15},
    {"score": 25, "spawn_rate": 1000, "speed_multiplier": 1.2, "max_fruits": 4, "bomb_chance": 0.2},
    {"score": 50, "spawn_rate": 800, "speed_multiplier": 1.4, "max_fruits": 5, "bomb_chance": 0.25},
    {"score": 100, "spawn_rate": 600, "speed_multiplier": 1.6, "max_fruits": 6, "bomb_chance": 0.3},
]
