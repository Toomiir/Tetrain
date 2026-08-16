import pygame
from settings import *

class Board:
    def __init__(self):
        self.cols = COLS
        self.rows = ROWS
        self.grid = []
        self.offset_x = (SCREEN_WIDTH - (self.cols * CELL_SIZE)) // 2
        self.offset_y = (SCREEN_HEIGHT - (self.rows * CELL_SIZE)) // 2
        self.clear()

    def clear(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def is_valid_position(self, piece, dx=0, dy=0, test_shape=None):
        shape_to_test = test_shape if test_shape is not None else piece.shape
        for row_idx, row in enumerate(shape_to_test):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    target_x = piece.x + col_idx + dx
                    target_y = piece.y + row_idx + dy

                    if target_x < 0 or target_x >= self.cols: return False
                    if target_y >= self.rows: return False
                    if target_y >= 0 and self.grid[target_y][target_x] != 0: return False
        return True

    def check_t_spin(self, piece):
        if piece.name != 'T' or not piece.last_move_was_rotation:
            return False
            
        corners = [
            (piece.x, piece.y),             
            (piece.x + 2, piece.y),         
            (piece.x, piece.y + 2),         
            (piece.x + 2, piece.y + 2)      
        ]
        
        filled_corners = 0
        for cx, cy in corners:
            if cx < 0 or cx >= self.cols or cy >= self.rows or (cy >= 0 and self.grid[cy][cx] != 0):
                filled_corners += 1
                
        return filled_corners >= 3

    def lock_piece(self, piece):
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell == 1 and piece.y + row_idx >= 0:
                    self.grid[piece.y + row_idx][piece.x + col_idx] = piece.color

    def clear_lines(self):
        new_grid = [row for row in self.grid if 0 in row]
        lines_cleared = self.rows - len(new_grid)
        
        for _ in range(lines_cleared):
            new_grid.insert(0, [0 for _ in range(self.cols)])
            
        self.grid = new_grid
        is_pc = all(cell == 0 for row in self.grid for cell in row)
        return lines_cleared, is_pc

    def add_garbage(self, garbage_rows):
        """Desplaza el tablero hacia arriba e inserta las filas de basura por abajo"""
        for row in garbage_rows:
            self.grid.pop(0)  # Elimina la fila superior
            self.grid.append(row) # Agrega la línea de basura abajo

    def draw(self, surface):
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(
                    self.offset_x + col * CELL_SIZE,
                    self.offset_y + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                cell_value = self.grid[row][col]
                if cell_value == 0:
                    pygame.draw.rect(surface, EMPTY_COLOR, rect)
                    pygame.draw.rect(surface, GRID_COLOR, rect, 1)
                else:
                    pygame.draw.rect(surface, cell_value, rect)
                    #pygame.draw.rect(surface, (255, 255, 255), rect, 1)