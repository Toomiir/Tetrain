import pygame
from settings import *
from stats_manager import StatsManager
from settings_manager import SettingsManager

class MainMenu:
    def __init__(self):
        # Eliminamos la opción global de reset del menú principal
        self.options = [
            "Modos de Juego",
            "Configuración de Handling",
            "Asignación de Teclas (Rebinds)",
            "Estadísticas",
            "Salir"
        ]
        self.selected_index = 0
        self.viewing_sub = None  # None, "MODES", "HANDLING", "REBINDS", "STATS"
        self.settings = SettingsManager.load_settings()
        self.setting_index = 0
        self.rebind_target = None
        self.last_adjust_time = 0

    def handle_event(self, event, current_time=0):
        # 1. SUBMENÚ DE ESTADÍSTICAS
        if self.viewing_sub == "STATS":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.viewing_sub = None
            return None

        # 2. SUBMENÚ DE MODOS
        if self.viewing_sub == "MODES":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.viewing_sub = None
                elif event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % 7
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % 7
                elif event.key == pygame.K_RETURN:
                    modes_map = [
                        "Freeplay", "Normal Survival", "Finesse Survival",
                        "T-Spin Survival", "Combo Survival", "Speed Survival", "Downstack Survival"
                    ]
                    chosen = modes_map[self.selected_index]
                    self.viewing_sub = None
                    self.selected_index = 0
                    return chosen
            return None

        # 3. SUBMENÚ DE REBINDS
        if self.viewing_sub == "REBINDS":
            if self.rebind_target:
                if event.type == pygame.KEYDOWN:
                    if event.key != pygame.K_ESCAPE:
                        self.settings["keybinds"][self.rebind_target] = event.key
                        SettingsManager.save_settings(self.settings)
                    self.rebind_target = None
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.viewing_sub = None
                    self.setting_index = 0
                elif event.key == pygame.K_UP:
                    # Sumamos 1 para incluir el botón de reset al final
                    self.setting_index = (self.setting_index - 1) % (len(self.settings["keybinds"]) + 1)
                elif event.key == pygame.K_DOWN:
                    self.setting_index = (self.setting_index + 1) % (len(self.settings["keybinds"]) + 1)
                elif event.key == pygame.K_RETURN:
                    # Si el índice es igual a la cantidad de teclas, significa que estamos en el botón de Reset
                    if self.setting_index == len(self.settings["keybinds"]):
                        defaults = SettingsManager.get_default_settings()
                        self.settings["keybinds"] = defaults["keybinds"].copy()
                        SettingsManager.save_settings(self.settings)
                    else:
                        keys_list = list(self.settings["keybinds"].keys())
                        self.rebind_target = keys_list[self.setting_index]
            return None

        # 4. SUBMENÚ DE HANDLING
        if self.viewing_sub == "HANDLING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.viewing_sub = None
                    self.setting_index = 0
                elif event.key == pygame.K_UP:
                    # Ahora hay 7 opciones (6 configuraciones + 1 botón reset)
                    self.setting_index = (self.setting_index - 1) % 7
                elif event.key == pygame.K_DOWN:
                    self.setting_index = (self.setting_index + 1) % 7
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    direction = -1 if event.key == pygame.K_LEFT else 1
                    self.adjust_handling(direction)
                elif event.key == pygame.K_RETURN:
                    # Si estamos en la opción 6 (Restaurar)
                    if self.setting_index == 6:
                        defaults = SettingsManager.get_default_settings()
                        for k in ["das", "arr", "lock_delay", "soft_drop_speed", "show_ghost", "hold_enabled"]:
                            self.settings[k] = defaults[k]
                        SettingsManager.save_settings(self.settings)
            return None

        # 5. MENÚ PRINCIPAL
        if event.type == pygame.KEYDOWN and self.viewing_sub is None:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                sel = self.options[self.selected_index]
                if sel == "Modos de Juego":
                    self.viewing_sub = "MODES"
                    self.selected_index = 0
                elif sel == "Configuración de Handling":
                    self.viewing_sub = "HANDLING"
                    self.setting_index = 0
                elif sel == "Asignación de Teclas (Rebinds)":
                    self.viewing_sub = "REBINDS"
                    self.setting_index = 0
                elif sel == "Estadísticas":
                    self.viewing_sub = "STATS"
                elif sel == "Salir":
                    return "Salir"
        return None

    def adjust_handling(self, direction):
        if self.setting_index == 0:  # DAS
            self.settings["das"] = max(0, self.settings["das"] + direction * 5)
        elif self.setting_index == 1:  # ARR
            self.settings["arr"] = max(0, self.settings["arr"] + direction * 2)
        elif self.setting_index == 2:  # Lock Delay
            self.settings["lock_delay"] = max(50, self.settings["lock_delay"] + direction * 25)
        elif self.setting_index == 3:  # Soft Drop Speed (0 = Infinito)
            self.settings["soft_drop_speed"] = max(0, self.settings["soft_drop_speed"] + direction * 5)
        elif self.setting_index == 4:  # Ghost
            self.settings["show_ghost"] = not self.settings["show_ghost"]
        elif self.setting_index == 5:  # Hold
            self.settings["hold_enabled"] = not self.settings["hold_enabled"]
        SettingsManager.save_settings(self.settings)

    def update_continuous_input(self, current_time):
        if self.viewing_sub == "HANDLING" and current_time - self.last_adjust_time > 80:
            # Evitamos activar el ajuste continuo en Ghost (4), Hold (5) o Reset (6)
            if self.setting_index in [4, 5, 6]:
                return
                
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.adjust_handling(-1)
                self.last_adjust_time = current_time
            elif keys[pygame.K_RIGHT]:
                self.adjust_handling(1)
                self.last_adjust_time = current_time

    def draw(self, surface, font):
        surface.fill(BG_COLOR)

        if self.viewing_sub == "STATS":
            title = pygame.font.Font(None, 40).render("RÉCORDS HISTÓRICOS", True, (0, 255, 200))
            surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
            stats_data = StatsManager.load_stats()
            y = 95
            for mode, records in stats_data.items():
                surface.blit(font.render(f"--- {mode} ---", True, (255, 220, 0)), (50, y))
                y += 24
                for k, v in records.items():
                    surface.blit(font.render(f"  {k}: {v}", True, (255, 255, 255)), (70, y))
                    y += 20
                y += 4
            back = pygame.font.Font(None, 22).render("Presiona ESC para volver", True, (150, 150, 150))
            surface.blit(back, (SCREEN_WIDTH // 2 - back.get_width() // 2, SCREEN_HEIGHT - 35))
            return

        if self.viewing_sub == "MODES":
            title = pygame.font.Font(None, 40).render("SELECCIONAR MODO", True, (0, 255, 200))
            surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))
            modes = ["Freeplay", "Normal Survival", "Finesse Survival", "T-Spin Survival", "Combo Survival", "Speed Survival", "Downstack Survival"]
            for i, m in enumerate(modes):
                col = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
                pref = "> " if i == self.selected_index else "  "
                surface.blit(font.render(pref + m, True, col), (100, 160 + i * 40))
            back = pygame.font.Font(None, 22).render("Presiona ESC para volver", True, (150, 150, 150))
            surface.blit(back, (SCREEN_WIDTH // 2 - back.get_width() // 2, SCREEN_HEIGHT - 50))
            return

        if self.viewing_sub == "HANDLING":
            title = pygame.font.Font(None, 40).render("CONFIGURACIÓN DE HANDLING", True, (0, 255, 200))
            surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))
            sd_val = f"{self.settings['soft_drop_speed']} ms (¡Infinito!)" if self.settings['soft_drop_speed'] == 0 else f"{self.settings['soft_drop_speed']} ms"
            
            # Se agregó la opción extra al final
            labels = [
                f"DAS (Delay): {self.settings['das']} ms",
                f"ARR (Repeat): {self.settings['arr']} ms",
                f"Lock Delay: {self.settings['lock_delay']} ms",
                f"Soft Drop Speed: {sd_val}",
                f"Mostrar Ghost: {'ON' if self.settings['show_ghost'] else 'OFF'}",
                f"Habilitar Hold: {'ON' if self.settings['hold_enabled'] else 'OFF'}",
                "Restaurar Handling por Defecto"
            ]
            y = 140
            for i, l in enumerate(labels):
                # La opción de Restaurar se pinta roja si no está seleccionada, para resaltar
                col = (255, 255, 0) if i == self.setting_index else ((255, 100, 100) if i == 6 else (255, 255, 255))
                pref = "> " if i == self.setting_index else "  "
                surface.blit(font.render(pref + l, True, col), (80, y))
                y += 45
            
            desc = pygame.font.Font(None, 20).render("Usa Izquierda/Derecha para modificar. Enter en Restaurar.", True, (150, 150, 150))
            surface.blit(desc, (SCREEN_WIDTH // 2 - desc.get_width() // 2, 460))
            back = pygame.font.Font(None, 22).render("Presiona ESC para volver", True, (150, 150, 150))
            surface.blit(back, (SCREEN_WIDTH // 2 - back.get_width() // 2, SCREEN_HEIGHT - 45))
            return

        if self.viewing_sub == "REBINDS":
            title = pygame.font.Font(None, 40).render("ASIGNACIÓN DE TECLAS", True, (0, 255, 200))
            surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))
            y = 150
            keys_items = list(self.settings["keybinds"].items())
            
            # Dibujar las 7 teclas
            for i, (action, key_code) in enumerate(keys_items):
                col = (255, 255, 0) if i == self.setting_index else (255, 255, 255)
                pref = "> " if i == self.setting_index else "  "
                key_name = pygame.key.name(key_code).upper()
                text = f"{action.replace('_', ' ').title()}: [{key_name}]"
                surface.blit(font.render(pref + text, True, col), (80, y))
                y += 38
            
            # Dibujar el botón de restaurar al final
            reset_idx = len(keys_items)
            col = (255, 255, 0) if self.setting_index == reset_idx else (255, 100, 100)
            pref = "> " if self.setting_index == reset_idx else "  "
            surface.blit(font.render(pref + "Restaurar Teclas por Defecto", True, col), (80, y + 15))

            if self.rebind_target:
                prompt = pygame.font.Font(None, 28).render("Presiona la nueva tecla...", True, (255, 100, 100))
                surface.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 480))
            
            back = pygame.font.Font(None, 22).render("Presiona ESC para volver", True, (150, 150, 150))
            surface.blit(back, (SCREEN_WIDTH // 2 - back.get_width() // 2, SCREEN_HEIGHT - 45))
            return

        # Menú Principal
        title = pygame.font.Font(None, 42)
        ts = title.render("TETRIS TRAINER", True, (0, 255, 200))
        surface.blit(ts, ts.get_rect(center=(SCREEN_WIDTH // 2, 80)))
        for i, option in enumerate(self.options):
            col = (255, 255, 0) if i == self.selected_index else (200, 200, 200)
            pref = "> " if i == self.selected_index else "  "
            surface.blit(font.render(pref + option, True, col), font.render(pref + option, True, col).get_rect(center=(SCREEN_WIDTH // 2, 180 + i * 45)))
        instr = pygame.font.Font(None, 20).render("Usa Flechas Arriba/Abajo y Enter para seleccionar", True, (150, 150, 150))
        surface.blit(instr, instr.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))

class GameOverScreen:
    @staticmethod
    def draw(surface, font, mode_name, result_stats):
        surface.fill(BG_COLOR)
        title = pygame.font.Font(None, 48).render("¡GAME OVER!", True, (255, 60, 60))
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))
        mode = font.render(f"Modo: {mode_name}", True, (255, 200, 0))
        surface.blit(mode, (SCREEN_WIDTH // 2 - mode.get_width() // 2, 190))
        y = 250
        for k, v in result_stats.items():
            st = font.render(f"{k}: {v}", True, (255, 255, 255))
            surface.blit(st, (SCREEN_WIDTH // 2 - st.get_width() // 2, y))
            y += 35
        instr = pygame.font.Font(None, 22).render("Presiona ENTER para volver al Menú Principal", True, (150, 150, 150))
        surface.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, SCREEN_HEIGHT - 100))