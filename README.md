# Fruit Cutter AI

Fruit Cutter AI is an interactive, gesture-controlled game built with Python, OpenCV, MediaPipe, and Pygame. It uses your webcam to track your hand, allowing you to slice virtual fruits using your index finger—just like Fruit Ninja, but in real life!

## Features

- **Webcam Integration**: Real-time video feed displayed as the background.
- **Hand Tracking**: Uses MediaPipe to track the index finger tip to act as a virtual blade.
- **Fruit Physics**: Realistic gravity and velocity for fruits spawning from the bottom.
- **Collision Detection**: Slices fruits dynamically when your finger trail crosses them.
- **Difficulty Scaling**: Game progressively speeds up and spawns more fruits as your score increases.
- **Combo System**: Slice multiple fruits quickly to earn combo multipliers.
- **Bombs**: Avoid slicing the black bombs, or it's game over!
- **Local High Scores**: Your highest score is automatically saved and loaded.
- **Modular Architecture**: Easy to extend for new game modes (e.g., Time Attack, Endless).

## Prerequisites

- Python 3.11+
- A working webcam

## Installation

1. Clone or download this repository.
2. Navigate to the project directory:
   ```bash
   cd fruit-cutter-ai
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the game using the following command:
```bash
python main.py
```

### How to Play

1. Stand in front of your webcam.
2. Wave your hand to start the game from the Main Menu.
3. Move your index finger to draw a slicing trail on the screen.
4. Slice fruits to score points.
5. Slice multiple fruits quickly for a combo multiplier.
6. Do not slice the black Bombs!
7. Do not let 3 fruits fall unsliced, or you lose all your lives.

## Project Structure

```
fruit-cutter-ai/
│── main.py            # Entry point and Pygame loop
│── game.py            # Game state, scoring, difficulty, and physics update
│── ui.py              # HUD and menus rendering
│── fruit.py           # Fruit & Bomb classes with particle effects
│── collision.py       # Math helpers for slicing detection
│── hand_tracker.py    # MediaPipe hand tracking and trail rendering
│── settings.py        # Global configuration and constants
│── requirements.txt   # Dependencies
│── README.md          # Documentation
│── assets/            # Directory for images, sounds, and fonts (optional)
```

## Future Enhancements
- Asset Loading: Add PNG sprites for fruits and custom background images.
- Audio: Integrate slicing and explosion sound effects.
- Power-ups: Add Slow-mo, Freeze, or Golden Fruits.
- Additional Game Modes: Implement Time Attack and Endless modes.
