class Stats:
    def __init__(self):
        self.score = 0
        self.lines = 0
        self.level = 1
        
        self.combo = -1  # Empieza en -1 para que la primera limpieza sea Combo 0
        self.b2b_active = False
        
        # Estadísticas puras
        self.total_t_spins = 0
        self.total_tetrises = 0
        self.perfect_clears = 0

    def update(self, lines_cleared, is_t_spin, is_pc):
        if lines_cleared > 0:
            self.combo += 1
            self.lines += lines_cleared
            self.level = (self.lines // 10) + 1  # Sube de nivel cada 10 líneas
            
            base_points = 0
            
            # Puntuación Base
            if is_t_spin:
                self.total_t_spins += 1
                if lines_cleared == 1: base_points = 800
                elif lines_cleared == 2: base_points = 1200
                elif lines_cleared == 3: base_points = 1600
            else:
                if lines_cleared == 1: base_points = 100
                elif lines_cleared == 2: base_points = 300
                elif lines_cleared == 3: base_points = 500
                elif lines_cleared == 4: 
                    base_points = 800
                    self.total_tetrises += 1
            
            # Back-to-Back (B2B) Bonus
            is_difficult_clear = (is_t_spin or lines_cleared == 4)
            if is_difficult_clear:
                if self.b2b_active:
                    base_points = int(base_points * 1.5)  # 50% extra por B2B
                self.b2b_active = True
            else:
                self.b2b_active = False # Rompe el B2B si hacés un clear regular

            # Combo Bonus
            if self.combo > 0:
                base_points += 50 * self.combo

            # Perfect Clear Bonus
            if is_pc:
                self.perfect_clears += 1
                base_points += 3000

            # Añadimos los puntos finales multiplicados por el nivel
            self.score += base_points * self.level
        else:
            # Si se colocó una pieza y no se limpió nada, se rompe el combo
            self.combo = -1