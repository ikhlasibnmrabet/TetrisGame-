from flask import Flask, render_template, request, jsonify, session
import random
import json

app = Flask(__name__)
app.secret_key = 'tetris_secret_key'

# Paramètres du jeu (identiques à test3.py)
ROWS, COLS = 20, 10
CELL_SIZE = 30
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'L': (255, 165, 0),
    'J': (0, 0, 255)
}

PIECES = {
    'I': [['.....', '.....', '..I..', '..I..', '..I..', '..I..', '.....']],
    'O': [['.....', '.....', '..OO.', '..OO.', '.....']],
    'T': [['.....', '..T..', '.TTT.', '.....']],
    'S': [['.....', '..SS.', '.SS..', '.....']],
    'Z': [['.....', '.ZZ..', '..ZZ.', '.....']],
    'L': [['.....', '..L..', '..L..', '..LL.', '.....']],
    'J': [['.....', '..J..', '..J..', '.JJ..', '.....']]
}

LETTERS = list(PIECES.keys())

level_speeds = {
    1: 1000,   # Facile : 1 seconde
    2: 600,    # Moyen  : 0,6 seconde
    3: 200    # Difficile : 0,35 seconde
}

class InvalidMoveError(Exception):
    pass

class GameOverError(Exception):
    pass

class Shape:
    def __init__(self, letter):
        self.letter = letter
        self.x = 3
        self.y = 0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Piece(Shape):
    def __init__(self, letter):
        self.letter = letter
        raw_shape = PIECES[letter][0]
        # Correction : prendre le carré central comme dans la version web
        self.shape = [list(row[2:7]) for row in raw_shape[1:6]]
        self.x = 3
        self.y = 0

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))
        # Convertir les tuples en listes
        self.shape = [list(row) for row in self.shape]

    def to_dict(self):
        return {
            'letter': self.letter,
            'shape': self.shape,
            'x': self.x,
            'y': self.y
        }

    @classmethod
    def from_dict(cls, data):
        piece = cls(data['letter'])
        piece.shape = data['shape']
        piece.x = data['x']
        piece.y = data['y']
        return piece

class Grid:
    def __init__(self):
        self.grid = [['.'] * COLS for _ in range(ROWS)]

    def valid_position(self, piece):
        for i in range(len(piece.shape)):
            for j in range(len(piece.shape[i])):
                if piece.shape[i][j] != '.':
                    row = piece.y + i
                    col = piece.x + j
                    if row >= ROWS or col < 0 or col >= COLS:
                        return False
                    if row >= 0 and self.grid[row][col] != '.':
                        return False
        return True

    def place_piece(self, piece):
        for i in range(len(piece.shape)):
            for j in range(len(piece.shape[i])):
                if piece.shape[i][j] != '.':
                    self.grid[piece.y + i][piece.x + j] = piece.letter

    def to_dict(self):
        return {
            'grid': self.grid
        }

    @classmethod
    def from_dict(cls, data):
        grid = cls()
        grid.grid = data['grid']
        return grid

class AdvancedGrid(Grid):
    def clear_lines(self):
        full_lines = [i for i, row in enumerate(self.grid) if '.' not in row]
        for i in full_lines:
            del self.grid[i]
            self.grid.insert(0, ['.'] * COLS)
        return len(full_lines)

class TetrisGame:
    def __init__(self, state=None, level_speed=None, level_chosen=1):
        if state:
            self.grid = AdvancedGrid.from_dict(state['grid'])
            self.current_index = state['current_index']
            self.piece = Piece.from_dict(state['piece'])
            self.score = state['score']
            self.lines_cleared = state.get('lines_cleared', 0)
            self.current_level = state.get('current_level', 1)
            self.level_speed = state.get('level_speed', 1000)
            self.game_over = state['game_over']
            self.level_chosen = state.get('level_chosen', 1)
        else:
            self.grid = AdvancedGrid()
            self.current_index = 0
            self.piece = Piece(LETTERS[self.current_index])
            self.score = 0
            self.lines_cleared = 0
            self.current_level = 1
            self.level_speed = level_speed if level_speed is not None else 1000
            self.game_over = False
            self.level_chosen = level_chosen

    def to_dict(self):
        return {
            'grid': self.grid.to_dict(),
            'current_index': self.current_index,
            'piece': self.piece.to_dict(),
            'score': self.score,
            'lines_cleared': self.lines_cleared,
            'current_level': self.current_level,
            'level_speed': self.level_speed,
            'game_over': self.game_over,
            'level_chosen': self.level_chosen
        }

    def next_piece(self):
        self.current_index = (self.current_index + 1) % len(LETTERS)
        return Piece(LETTERS[self.current_index])

    def update_level(self):
        new_level = max(self.level_chosen, min(3, (self.lines_cleared // 10) + 1))
        if new_level != self.current_level:
            self.current_level = new_level
        self.level_speed = level_speeds.get(self.current_level, 300)

    def drop_piece(self):
        if self.game_over:
            raise GameOverError("Fin du jeu.")
        self.piece.y += 1
        if not self.grid.valid_position(self.piece):
            self.piece.y -= 1
            self.grid.place_piece(self.piece)
            lines_cleared = self.grid.clear_lines()
            self.score += lines_cleared * 100
            self.lines_cleared += lines_cleared
            self.update_level()
            self.piece = self.next_piece()
            if not self.grid.valid_position(self.piece):
                self.game_over = True
                raise GameOverError("Plus d'espace pour une nouvelle pièce. Fin du jeu.")

    def move_left(self):
        if self.game_over:
            raise GameOverError("Fin du jeu.")
        self.piece.x -= 1
        if not self.grid.valid_position(self.piece):
            self.piece.x += 1
            raise InvalidMoveError("Déplacement à gauche invalide.")

    def move_right(self):
        if self.game_over:
            raise GameOverError("Fin du jeu.")
        self.piece.x += 1
        if not self.grid.valid_position(self.piece):
            self.piece.x -= 1
            raise InvalidMoveError("Déplacement à droite invalide.")

    def rotate(self):
        if self.game_over:
            raise GameOverError("Fin du jeu.")
        old_shape = [row[:] for row in self.piece.shape]
        self.piece.shape = list(zip(*self.piece.shape[::-1]))
        self.piece.shape = [list(row) for row in self.piece.shape]
        if not self.grid.valid_position(self.piece):
            self.piece.shape = old_shape
            raise InvalidMoveError("Rotation invalide.")

def get_game_state():
    """Récupère l'état du jeu depuis la session"""
    if 'game_state' not in session:
        return None
    return TetrisGame.from_dict(session['game_state'])

def save_game_state(game_state):
    """Sauvegarde l'état du jeu dans la session"""
    session['game_state'] = game_state.to_dict()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.get_json()
    level = data.get('level', 1)
    speed = level_speeds.get(level, 1000)
    session['game_state'] = None
    game = TetrisGame(level_speed=speed, level_chosen=level)
    game.current_level = level
    game.level_chosen = level
    game.level_speed = speed
    session['game_state'] = game.to_dict()
    return jsonify({'status': 'success'})

@app.route('/get_state')
def get_state():
    if 'game_state' not in session or session['game_state'] is None:
        return jsonify({'error': 'No game started'})
    game = TetrisGame(session['game_state'])
    return jsonify(game.to_dict())

@app.route('/move', methods=['POST'])
def move():
    if 'game_state' not in session or session['game_state'] is None:
        return jsonify({'error': 'No game started'})
    data = request.get_json()
    direction = data.get('direction')
    game = TetrisGame(session['game_state'])
    try:
        if direction == 'left':
            game.move_left()
        elif direction == 'right':
            game.move_right()
        elif direction == 'down':
            game.drop_piece()
        elif direction == 'rotate':
            game.rotate()
        else:
            return jsonify({'error': 'Commande inconnue'})
        session['game_state'] = game.to_dict()
        return jsonify({'success': True, 'state': game.to_dict()})
    except (InvalidMoveError, GameOverError) as e:
        session['game_state'] = game.to_dict()
        return jsonify({'success': False, 'error': str(e), 'state': game.to_dict()})

@app.route('/update', methods=['POST'])
def update():
    if 'game_state' not in session or session['game_state'] is None:
        return jsonify({'error': 'No game started'})
    game = TetrisGame(session['game_state'])
    try:
        game.drop_piece()
        session['game_state'] = game.to_dict()
        return jsonify({'success': True, 'state': game.to_dict()})
    except (InvalidMoveError, GameOverError) as e:
        session['game_state'] = game.to_dict()
        return jsonify({'success': False, 'error': str(e), 'state': game.to_dict()})

if __name__ == '__main__':
    app.run(debug=True) 