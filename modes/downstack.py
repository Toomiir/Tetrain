import pygame
import random
from settings import *
from board import Board
from piece import Piece
from stats import Stats
from garbage import GarbageSystem

class Randomizer:
    def __init__(self):
        self.bag = []
        self.queue = []
        self.fill_queue()

    def get_new_bag(self):
        new_bag = list(SHAPES.keys())
        random.shuffle(new_bag)
        return new_bag

    def fill_queue(self):
        while len(self.queue) <= NEXT_PIECES:
            if not self.bag:
                self.bag = self.get_new_bag()
            self.queue.append(Piece(self.bag.pop(0)))

    def get_next_piece(self):
        self.fill_queue()
        piece = self.queue.pop(0)
        self.fill_queue() 
        return piece

def draw_text(surface, text, font, x, y, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

class DownstackMode:
    def __init__(self):
        self.board = Board()
        self.randomizer = Randomizer()
        self.current_piece = self.randomizer.get_next_piece()
        self.stats = Stats()
        
        self.config = {
            "das": DAS,
            "arr": ARR,
            "lock_delay": LOCK_DELAY,
            "soft_drop_speed": SOFT_DROP_SPEED,
            "show_ghost": True,
            "hold_enabled": True
        }

        self.held_piece = None
        self.can_hold = True

        # Métricas y temporizadores de Downstack
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.garbage_incoming_timer = pygame.time.get_ticks()
        self.garbage_interval = 8000  # Recibe una línea de basura cada 8 segundos
        self.garbage_lines_received = 0

        self.keys_held = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_DOWN: False}
        self.das_timer = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0}
        self.das_active = {pygame.K_LEFT: False, pygame.K_RIGHT: False}

        self.last_fall_time = pygame.time.get_ticks()
        self.lock_timer_start = 0
        self.force_lock = False

        # Generamos una altura inicial de basura para arrancar a limpiar
        initial_garbage = GarbageSystem.generate_garbage(5)
        self.board.add_garbage(initial_garbage)
        self.garbage_lines_received += 5

    def handle_event(self, event, current_time):
        kb = self.config.get("keybinds", {
            "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "soft_drop": pygame.K_DOWN,
            "hard_drop": pygame.K_SPACE, "rotate_cw": pygame.K_UP, "rotate_ccw": pygame.K_z, "hold": pygame.K_c
        })

        if event.type == pygame.KEYDOWN:
            if event.key == kb["left"]:
                if self.board.is_valid_position(self.current_piece, dx=-1, dy=0):
                    self.current_piece.move(-1, 0)
                    if self.lock_timer_start > 0: self.lock_timer_start = current_time
                self.das_timer["left"] = current_time
                self.das_active["left"] = False

            elif event.key == kb["right"]:
                if self.board.is_valid_position(self.current_piece, dx=1, dy=0):
                    self.current_piece.move(1, 0)
                    if self.lock_timer_start > 0: self.lock_timer_start = current_time
                self.das_timer["right"] = current_time
                self.das_active["right"] = False

            elif event.key == kb["rotate_cw"]:
                if self.current_piece.rotate(1, self.board):
                    if self.lock_timer_start > 0: self.lock_timer_start = current_time

            elif event.key == kb["rotate_ccw"]:
                if self.current_piece.rotate(-1, self.board):
                    if self.lock_timer_start > 0: self.lock_timer_start = current_time
            
            elif event.key == kb.get("rotate_180", pygame.K_a):
                if self.current_piece.rotate(2, self.board):
                    if self.lock_timer_start > 0: self.lock_timer_start = current_time
            
            elif event.key == kb["hard_drop"]:
                self.current_piece.hard_drop(self.board)
                self.force_lock = True 

            elif event.key == kb["hold"] and self.config.get("hold_enabled", True):
                if self.can_hold:
                    if self.held_piece is None:
                        self.held_piece = self.current_piece
                        self.held_piece.reset_position()
                        self.current_piece = self.randomizer.get_next_piece()
                    else:
                        temp = self.current_piece
                        self.current_piece = self.held_piece
                        self.held_piece = temp
                        self.held_piece.reset_position()
                    self.can_hold = False
                    self.lock_timer_start = 0
                    self.last_fall_time = current_time

    def update(self, current_time):
        kb = self.config.get("keybinds", {
            "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "soft_drop": pygame.K_DOWN,
            "hard_drop": pygame.K_SPACE, "rotate_cw": pygame.K_UP, "rotate_ccw": pygame.K_z, "hold": pygame.K_c
        })
        pressed = pygame.key.get_pressed()

        # Evaluación de DAS / ARR según las teclas asignadas
        for action, dx in [("left", -1), ("right", 1)]:
            key_code = kb[action]
            if pressed[key_code]:
                if not self.das_active.get(action, False):
                    if current_time - self.das_timer.get(action, 0) >= self.config["das"]:
                        self.das_active[action] = True
                        self.das_timer[action] = current_time 
                else:
                    if self.config["arr"] == 0:
                        moved = False
                        while self.board.is_valid_position(self.current_piece, dx=dx, dy=0):
                            self.current_piece.move(dx, 0)
                            moved = True
                        if moved and self.lock_timer_start > 0: self.lock_timer_start = current_time
                    else:
                        if current_time - self.das_timer.get(action, 0) >= self.config["arr"]:
                            if self.board.is_valid_position(self.current_piece, dx=dx, dy=0):
                                self.current_piece.move(dx, 0)
                                if self.lock_timer_start > 0: self.lock_timer_start = current_time
                            self.das_timer[action] = current_time
            else:
                self.das_active[action] = False

        # Soft drop con soporte para Soft Drop Instantáneo / Infinito (0 ms)
        is_soft_dropping = pressed[kb["soft_drop"]]
        if is_soft_dropping and self.config.get("soft_drop_speed", 50) == 0:
            while self.board.is_valid_position(self.current_piece, dx=0, dy=1):
                self.current_piece.move(0, 1)

        # Caída por Gravedad / Lock delay
        is_grounded = not self.board.is_valid_position(self.current_piece, dx=0, dy=1)
        if is_grounded or self.force_lock:
            if self.lock_timer_start == 0 and not self.force_lock:
                self.lock_timer_start = current_time
            elif self.force_lock or (current_time - self.lock_timer_start >= self.config["lock_delay"]):
                self.board.lock_piece(self.current_piece)
                self.board.clear_lines()
                self.current_piece = self.randomizer.get_next_piece()
                self.lock_timer_start = 0
                self.force_lock = False
                self.last_fall_time = current_time
                self.can_hold = True
                if not self.board.is_valid_position(self.current_piece):
                    return True
        else:
            self.lock_timer_start = 0
            sd_speed = self.config.get("soft_drop_speed", 50)
            current_gravity = sd_speed if is_soft_dropping and sd_speed > 0 else 1000
            if current_time - self.last_fall_time >= current_gravity:
                self.current_piece.move(0, 1)
                self.last_fall_time = current_time

        return False

        # 2. Gravity & Lock Delay
        is_grounded = not self.board.is_valid_position(self.current_piece, dx=0, dy=1)

        if is_grounded or self.force_lock:
            if self.lock_timer_start == 0 and not self.force_lock:
                self.lock_timer_start = current_time
            
            elif self.force_lock or (current_time - self.lock_timer_start >= self.config["lock_delay"]):
                is_t_spin = self.board.check_t_spin(self.current_piece)
                self.board.lock_piece(self.current_piece)
                lines_cleared, is_pc = self.board.clear_lines()
                self.stats.update(lines_cleared, is_t_spin, is_pc)

                self.current_piece = self.randomizer.get_next_piece()
                self.lock_timer_start = 0
                self.force_lock = False
                self.last_fall_time = current_time 
                self.can_hold = True  
                
                if not self.board.is_valid_position(self.current_piece):
                    print(f"¡Game Over (Downstack Survival)! Tiempo: {self.elapsed_time}s | Líneas limpiadas: {self.stats.lines}")
                    self.board.clear()
                    initial_garbage = GarbageSystem.generate_garbage(5)
                    self.board.add_garbage(initial_garbage)
                    self.randomizer = Randomizer()
                    self.stats = Stats() 
                    self.current_piece = self.randomizer.get_next_piece()
                    self.held_piece = None
                    self.garbage_lines_received = 5
                    self.start_ticks = current_time
                    self.garbage_incoming_timer = current_time
        else:
            self.lock_timer_start = 0
            current_gravity = self.config["soft_drop_speed"] if self.keys_held[pygame.K_DOWN] else GRAVITY
            if current_time - self.last_fall_time >= current_gravity:
                self.current_piece.move(0, 1)
                self.last_fall_time = current_time

    def draw(self, surface, font):
        surface.fill(BG_COLOR)
        
        self.board.draw(surface)
        
        if self.config["show_ghost"]:
            self.current_piece.draw_ghost(surface, self.board, self.board.offset_x, self.board.offset_y)
        self.current_piece.draw(surface, self.board.offset_x, self.board.offset_y)

        # UI Derecha (Queue)
        ui_x = self.board.offset_x + (self.board.cols * CELL_SIZE) + 30
        ui_y = self.board.offset_y
        for i in range(NEXT_PIECES):
            piece = self.randomizer.queue[i]
            piece.draw_absolute(surface, ui_x, ui_y + i * 3.5 * CELL_SIZE)

        # UI Izquierda (Hold y métricas de Downstack)
        ui_left_x = 20
        ui_left_y = self.board.offset_y
        draw_text(surface, "HOLD", font, ui_left_x, ui_left_y)
        if self.held_piece and self.config["hold_enabled"]:
            self.held_piece.draw_absolute(surface, ui_left_x, ui_left_y + 30)

        stats_y = ui_left_y + 150
        draw_text(surface, f"Mode: DOWNSTACK", font, ui_left_x, stats_y - 30, (100, 255, 200))
        draw_text(surface, f"Time: {self.elapsed_time}s", font, ui_left_x, stats_y)
        draw_text(surface, f"Lines Cleared: {self.stats.lines}", font, ui_left_x, stats_y + 30)
        draw_text(surface, f"Garbage Recv: {self.garbage_lines_received}", font, ui_left_x, stats_y + 60, (255, 150, 150))
        draw_text(surface, f"Score: {self.stats.score}", font, ui_left_x, stats_y + 90)