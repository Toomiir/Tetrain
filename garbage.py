import random
from settings import COLS, GARBAGE_COLOR

class GarbageSystem:
    @staticmethod
    def generate_garbage(amount, hole_col=None):
        """
        Genera una lista de líneas de basura con un agujero (0) aleatorio o específico.
        """
        garbage_rows = []
        for _ in range(amount):
            # Si no se define una columna para el agujero, se elige una al azar entre 0 y COLS-1
            hole = hole_col if hole_col is not None else random.randint(0, COLS - 1)
            
            # Construimos la fila: GARBAGE_COLOR en todos lados menos en la posición del agujero
            row = [GARBAGE_COLOR if col != hole else 0 for col in range(COLS)]
            garbage_rows.append(row)
            
        return garbage_rows