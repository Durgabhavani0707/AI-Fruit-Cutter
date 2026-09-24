"""
settings.py

Contains all configuration and settings for the Fruit Cutter AI game.
"""

import os


# ============================================================
# Screen / Performance
# ============================================================

WIDTH = 1280
HEIGHT = 720
FPS = 60


# ============================================================
# Colors (RGB)
# ============================================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)


# ============================================================
# Paths
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")

HIGH_SCORE_FILE = os.path.join(
    BASE_DIR,
    "highscore.json"
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "hand_landmarker.task"
)


# ============================================================
# Game Modes
# ============================================================

MODE_CLASSIC = "CLASSIC"

# Future modes:
# MODE_TIME_ATTACK = "TIME_ATTACK"
# MODE_ENDLESS = "ENDLESS"


# ============================================================
# General Game Settings
# ============================================================

STARTING_LIVES = 3

# Time in milliseconds during which consecutive slices
# are counted as a combo.
COMBO_TIME_WINDOW = 1000


# ============================================================
# Collision Settings
# ============================================================

# Extra collision buffer used for fast hand movement.
# Higher value = easier slicing.
COLLISION_BUFFER_MIN = 25
COLLISION_BUFFER_MAX = 55

# Maximum distance the fingertip can jump between frames
# before tracking correction is applied.
MAX_FINGER_JUMP = 180


# ============================================================
# Hand Tracking Settings
# ============================================================

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Smaller inference resolution improves performance.
INFERENCE_WIDTH = 320
INFERENCE_HEIGHT = 240

# Number of trail points shown behind the fingertip.
TRAIL_LENGTH = 18

# Smoothing values.
MIN_SMOOTHING = 0.30
MAX_SMOOTHING = 0.95

# Time in seconds after which an old hand-detection result
# is considered stale.
TRACKING_TIMEOUT = 0.35


# ============================================================
# Difficulty Levels
# ============================================================

DIFFICULTY_LEVELS = [
    {
        "score": 0,
        "spawn_rate": 2000,
        "speed_multiplier": 1.0,
        "max_fruits": 2,
        "bomb_chance": 0.10,
    },

    {
        "score": 10,
        "spawn_rate": 1500,
        "speed_multiplier": 1.1,
        "max_fruits": 3,
        "bomb_chance": 0.15,
    },

    {
        "score": 25,
        "spawn_rate": 1000,
        "speed_multiplier": 1.2,
        "max_fruits": 4,
        "bomb_chance": 0.20,
    },

    {
        "score": 50,
        "spawn_rate": 800,
        "speed_multiplier": 1.4,
        "max_fruits": 5,
        "bomb_chance": 0.25,
    },

    {
        "score": 100,
        "spawn_rate": 600,
        "speed_multiplier": 1.6,
        "max_fruits": 6,
        "bomb_chance": 0.30,
    },
]


# ============================================================
# Fruit Settings
# ============================================================

# Starting position range keeps fruits away from the extreme
# left and right edges of the screen.

FRUIT_SPAWN_MARGIN = 150

# Gravity applied to fruits.
FRUIT_GRAVITY = 0.25

# Number of particles generated when slicing a fruit.
FRUIT_PARTICLE_COUNT = 10

# Number of particles generated when slicing a bomb.
BOMB_PARTICLE_COUNT = 30


# ============================================================
# Visual Effects
# ============================================================

# Maximum number of particles allowed at once.
MAX_PARTICLES = 250

# Screen shake duration in milliseconds.
SCREEN_SHAKE_DURATION = 250

# Maximum screen shake intensity.
SCREEN_SHAKE_INTENSITY = 10


# ============================================================
# UI Settings
# ============================================================

FONT_SIZE_SMALL = 24
FONT_SIZE_MEDIUM = 32
FONT_SIZE_LARGE = 48
FONT_SIZE_TITLE = 72


# ============================================================
# Audio Settings
# ============================================================

SOUND_ENABLED = True

# Master volume: 0.0 - 1.0
MASTER_VOLUME = 0.6

SLICE_SOUND_VOLUME = 0.5
BOMB_SOUND_VOLUME = 0.7
COMBO_SOUND_VOLUME = 0.6
GAME_OVER_SOUND_VOLUME = 0.7