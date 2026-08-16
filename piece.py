import pygame
from settings import *

class Piece:
    def __init__(self, shape_name):
        self.name = shape_name
        self.color = COLORS[shape_name]
        self.last_move_was_rotation = False
        self.reset_position()

    def reset_position(self):
        self.shape = SHAPES[self.name]
        self.rotation_state = 0 
        self.x = (COLS // 2) - (len(self.shape[0]) // 2)
        self.y = 0 
        self.last_move_was_rotation = False

    def move(self, dx, dy):
        # Si la pieza efectivamente se traslada, ya no cuenta como rotación como última acción
        if dx != 0 or dy != 0:
            self.last_move_was_rotation = False
            
        self.x += dx
        self.y += dy

    def hard_drop(self, board):
        drop_distance = 0
        while board.is_valid_position(self, dx=0, dy=drop_distance + 1):
            drop_distance += 1
        # Si no baja nada (drop_distance=0), conserva la bandera de rotación (útil para T-Spins en el piso)
        self.move(0, drop_distance)

    def rotate(self, direction, board):
        if self.name == 'O':
            return False

        new_state = (self.rotation_state + direction) % 4

        # 1 = Clockwise (90°), -1 = Counter-Clockwise (-90°), 2 = 180°
        if direction == 1:
            new_shape = [list(row) for row in zip(*self.shape[::-1])]
        elif direction == -1:
            new_shape = [list(row) for row in reversed(list(zip(*self.shape)))]
        elif direction == 2:
            # Rotación de 180 grados (invertir filas y columnas)
            new_shape = [list(reversed(row)) for row in reversed(self.shape)]
        else:
            return False

        # Seleccionar la tabla de Kicks correspondiente
        if direction == 2:
            kicks = WALL_KICKS_180
        else:
            kicks = WALL_KICKS_I if self.name == 'I' else WALL_KICKS_JLSTZ
            
        kicks_to_try = kicks.get((self.rotation_state, new_state), [(0, 0)])

        for dx, dy in kicks_to_try:
            if board.is_valid_position(self, dx=dx, dy=dy, test_shape=new_shape):
                self.shape = new_shape
                self.x += dx
                self.y += dy
                self.rotation_state = new_state
                self.last_move_was_rotation = True
                return True 
        
        return False

    def draw(self, surface, offset_x, offset_y):
        for row_idx, row in enumerate(self.shape):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    px = offset_x + (self.x + col_idx) * CELL_SIZE
                    py = offset_y + (self.y + row_idx) * CELL_SIZE
                    rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surface, self.color, rect)
                    pygame.draw.rect(surface, (255, 255, 255), rect, 1)

    def draw_ghost(self, surface, board, offset_x, offset_y):
        drop_distance = 0
        while board.is_valid_position(self, dx=0, dy=drop_distance + 1):
            drop_distance += 1

        for row_idx, row in enumerate(self.shape):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    px = offset_x + (self.x + col_idx) * CELL_SIZE
                    py = offset_y + (self.y + drop_distance + row_idx) * CELL_SIZE
                    rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surface, self.color, rect, 2) 

    def draw_absolute(self, surface, px, py):
        for row_idx, row in enumerate(self.shape):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    rect = pygame.Rect(px + col_idx * CELL_SIZE, py + row_idx * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surface, self.color, rect)
                    pygame.draw.rect(surface, (255, 255, 255), rect, 1)