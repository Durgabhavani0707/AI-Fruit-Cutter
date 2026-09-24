🍎 **AI Fruit Cutter**__

An AI-powered fruit slicing game that uses real-time hand tracking to let players slice fruits with their finger movements through a webcam.

✨ **Features**
🤖 AI Hand Tracking using MediaPipe
✋ Real-time index-finger detection
🍎 Multiple fruit types
💣 Bomb obstacles
❤️ Three-life game system
🔥 Combo and score system
🏆 High-score saving
💥 Particle effects and screen shake
🎯 Smooth fruit physics and collision detection
🎨 Modern game interface
📷 Webcam-based interaction
🖱️ Mouse fallback for gameplay/menu interaction  

🛠️ **Technologies Used**
Technology	Purpose
Python	Core programming
Pygame	Game development and UI
OpenCV	Webcam input
MediaPipe	AI hand tracking
NumPy	Numerical processing
JSON	High-score storage

📂 **Project Structure**
AI-Fruit-Cutter-main/
│
├── collision.py
├── fruit.py
├── game.py
├── hand_landmarker.task
├── hand_tracker.py
├── highscore.json
├── main.py
├── README.md
├── requirements.txt
├── settings.py
└── ui.py

⚙️ **Installation**
1. Clone the repository
git clone https://github.com/Durgabhavani0707/AI-Fruit-Cutter.git
2. Open the project
cd AI-Fruit-Cutter
3. Install dependencies
pip install -r requirements.txt
4. Run the game
python main.py
🎮 How to Play
Start the game.
Allow webcam access.
Move your index finger in front of the camera.
Move across fruits to slice them.
Avoid bombs.
Build combos to increase your score.
Try to beat your high score!

🖱️ Mouse Support

If hand tracking is unavailable, mouse controls can be used as a fallback.

🤖 AI Hand Tracking

The project uses MediaPipe Hand Landmarker to detect hand landmarks from the webcam.

The system tracks the index fingertip landmark and converts its movement into the slicing path used by the game.

Webcam
   ↓
OpenCV
   ↓
MediaPipe Hand Tracking
   ↓
Index Finger Detection
   ↓
Slicing Path
   ↓
Collision Detection
   ↓
Fruit Sliced

🍉 Game Elements
Fruits
🍎 Apple
🍌 Banana
🍊 Orange
🍉 Watermelon

Different fruits provide different scores.

💣 Bombs

Bombs act as obstacles. Slicing a bomb can end the game.

🔥 Combo System

Successfully slicing fruits within a short time window increases the combo and rewards continuous gameplay.

🏆 High Score

The highest score is stored locally in:

highscore.json
🎯 Main Components
main.py

Controls the overall game flow and game states.

game.py

Handles gameplay, scoring, lives, spawning, collisions and game logic.

fruit.py

Contains fruit, bomb, particle and floating-text objects.

hand_tracker.py

Handles webcam input and AI-based hand tracking.

collision.py

Provides collision detection between the finger movement and game objects.

ui.py

Handles the game's menus, HUD, score display and game-over interface.

settings.py

Stores game configuration, dimensions, colors, difficulty and gameplay settings.

🚀 **Future Improvements**
🎵 Background music and sound effects
👥 Multiplayer mode
📈 Detailed player statistics
🧠 Improved hand gesture recognition
🏅 Global leaderboard
📱 More interaction modes
🎨 Additional visual effects
⚡ Further optimization for low-end systems

👩‍💻 Author

Durga Bhavani

B.Tech – Computer Science & Engineering

**GitHub**:
https://github.com/Durgabhavani0707

📜 **License**

This project is developed for educational and project purposes.
