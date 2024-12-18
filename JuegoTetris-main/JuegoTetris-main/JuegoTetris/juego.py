import keyboard
import threading
import time
import random
import os
from enum import Enum
import copy
import math

COLOURS = ("🟦", "🟥", "🟪", "🟩", "🟧", "🟨")
EMPTY_BOX = "⬜"

class Movement(Enum):
    DOWN = 0
    RIGHT = 1
    LEFT = 2
    ROTATE = 3

class Board():
    BOARD = [[EMPTY_BOX]*10 for _ in range(20)]

    def __init__(self):
        self.boxes = self.BOARD
        self.piece = Piece()
        self.print_board()

    def print_board(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('ESC to exit')
        temp_board = copy.deepcopy(self.boxes)
        for position in self.piece.shape.position:
            if 0 <= position[1] < len(temp_board) and 0 <= position[0] < len(temp_board[0]):
                temp_board[position[1]][position[0]] = self.piece.colour
        for row in temp_board:
            print("".join(map(str, row)))
        print('\n')

    def update_board(self):
        for position in self.piece.shape.position:
            if 0 <= position[1] < len(self.boxes) and 0 <= position[0] < len(self.boxes[0]):
                self.boxes[position[1]][position[0]] = self.piece.colour
        self.piece.change_piece()

    def move_piece(self, movement: Movement) -> None:
        if movement == Movement.ROTATE:
            self.piece.rotation_state = (self.piece.rotation_state + 1) % 4
            self.piece.shape.position = self._rotate_shape()
        else:
            if self._is_valid_move(movement):
                for box in self.piece.shape.position:
                    match movement:
                        case Movement.DOWN:
                            box[1] += 1
                        case Movement.RIGHT:
                            box[0] += 1
                        case Movement.LEFT:
                            box[0] -= 1
                self._full_row_control()
                self.print_board()
            else:
                if movement == Movement.DOWN:
                    self.update_board()

    def _rotate_shape(self):
        angle = self.piece.rotation_state * 90
        rad_angle = math.radians(angle)
        rotation_matrix = [
            [math.cos(rad_angle), -math.sin(rad_angle)],
            [math.sin(rad_angle), math.cos(rad_angle)]
        ]
        new_position = []
        for box in self.piece.shape.position:
            x, y = box
            new_x = round(x * rotation_matrix[0][0] + y * rotation_matrix[0][1])
            new_y = round(x * rotation_matrix[1][0] + y * rotation_matrix[1][1])
            new_position.append([new_x, new_y])
        return new_position

    def _is_valid_move(self, movement: Movement) -> bool:
        for box in self.piece.shape.position:
            match movement:
                case Movement.DOWN:
                    if box[1] >= len(self.boxes) - 1 or self.boxes[box[1] + 1][box[0]] != EMPTY_BOX:
                        return False
                case Movement.RIGHT:
                    if box[0] >= len(self.boxes[0]) - 1 or self.boxes[box[1]][box[0] + 1] != EMPTY_BOX:
                        return False
                case Movement.LEFT:
                    if box[0] <= 0 or self.boxes[box[1]][box[0] - 1] != EMPTY_BOX:
                        return False
                case Movement.ROTATE:
                    new_positions = self._rotate_shape()
                    for pos in new_positions:
                        if pos[0] < 0 or pos[0] >= len(self.boxes[0]) or pos[1] >= len(self.boxes) or self.boxes[pos[1]][pos[0]] != EMPTY_BOX:
                            return False
        return True

    def _full_row_control(self):
        full_rows = []
        for i, row in enumerate(self.boxes):
            if all(cell != EMPTY_BOX for cell in row):
                full_rows.append(i)
        for row_index in sorted(full_rows, reverse=True):
            del self.boxes[row_index]
            self.boxes.insert(0, [EMPTY_BOX] * 10)

class Piece:
    def __init__(self):
        self.colour = COLOURS[random.randint(0, len(COLOURS)-1)]
        self.shape = self._random_shape()
        self.rotation_state = 0

    def _random_shape(self):
        pieces = [_JBlock, _IBlock, _LBlock, _SquareBlock, _TBlock, _ZBlock, _SBlock]
        selected_piece = random.choice(pieces)
        return selected_piece()

    def change_piece(self):
        self.colour = COLOURS[random.randint(0, len(COLOURS)-1)]
        self.shape = self._random_shape()
        self.rotation_state = 0

class _JBlock:
    def __init__(self):
        self.position = [[0, 0], [0, 1], [1, 1], [2, 1]]
        self.rotation = []

class _IBlock:
    def __init__(self):
        self.position = [[0, 1], [1, 1], [2, 1], [3, 1]]
        self.rotation = []

class _LBlock:
    def __init__(self):
        self.position = [[2, 0], [2, 1], [1, 1], [0, 1]]
        self.rotation = []

class _SquareBlock:
    def __init__(self):
        self.position = [[1, 0], [2, 0], [1, 1], [2, 1]]
        self.rotation = []

class _TBlock:
    def __init__(self):
        self.position = [[1, 0], [0, 1], [1, 1], [2, 1]]
        self.rotation = []

class _ZBlock:
    def __init__(self):
        self.position = [[0, 0], [1, 0], [1, 1], [2, 1]]
        self.rotation = []

class _SBlock:
    def __init__(self):
        self.position = [[2, 0], [1, 0], [1, 1], [0, 1]]
        self.rotation = []

key_mapping = {
    'flecha abajo': Movement.DOWN,
    'down': Movement.DOWN,
    's': Movement.DOWN,
    'flecha derecha': Movement.RIGHT,
    'right': Movement.RIGHT,
    'd': Movement.RIGHT,
    'flecha izquierda': Movement.LEFT,
    'left': Movement.LEFT,
    'a': Movement.LEFT,
    'space': Movement.ROTATE
}

def main():
    board = Board()
    key = None
    game_over = False

    def auto_fall():
        nonlocal game_over
        while not game_over:
            time.sleep(1)
            board.move_piece(Movement.DOWN)

    auto_fall_thread = threading.Thread(target=auto_fall)
    auto_fall_thread.start()

    while key != 'esc' and not game_over:
        listener = keyboard.read_event()
        if listener.event_type == keyboard.KEY_DOWN:
            key = listener.name
            if key in key_mapping:
                board.move_piece(key_mapping[key])

        for cell in board.boxes[0]:
            if cell != EMPTY_BOX:
                game_over = True
                break

    game_over = True
    auto_fall_thread.join()
    print("Game Over")

if __name__ == '__main__':
    main()
