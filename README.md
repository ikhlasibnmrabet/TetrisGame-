# # Tetris Web - Flask Application

A web version of Tetris built with Flask, faithfully reproducing the original game's mechanics in Python.

Features
Level Selection Menu: 3 difficulty levels (Easy, Medium, Hard)
Classic Controls: Arrow keys for moving and rotating pieces
Scoring System: Points awarded based on completed lines
Modern Interface: Clean, responsive design with vibrant colors
Game Over Detection: Automatic detection when no more moves are possible


Installation

Clone the repository:
git clone <your-repo-url>
cd jeutetris

Create a virtual environment (optional but recommended):
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate


 # Install dependencies:
pip install -r requirements.txt
Run the application:
python app.py


# Open in your browser:
http://localhost:5000
Select a level from the menu and click “Start Game”
Use arrow keys to control the pieces

# Controls
← → : Move the piece left or right
↓ : Drop the piece faster
↑ : Rotate the piece
Space : Pause / Resume the game

# Project Structure
jeutetris/
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # User interface
├── requirements.txt    # Python dependencies
└── README.md           # This file

# Differences from the Python Version
Web Interface: Replaced Pygame with HTML5 Canvas
Client-Server Communication: REST API for game logic
Session Management: Game state handled server-side with Flask sessions
Same Game Logic: All Tetris rules and mechanics preserved

# Technologies Used
Backend: Flask (Python)
Frontend: HTML5, CSS3, JavaScript
Rendering: HTML5 Canvas
Communication: REST API with JSON

License
MIT License – contributions welcome!
