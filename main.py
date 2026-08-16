import pygame
import sys
from settings import *
from menu import MainMenu, GameOverScreen
from settings_manager import SettingsManager
from stats_manager import StatsManager
from modes.freeplay import FreeplayMode
from modes.survival import SurvivalMode
from modes.finesse_survival import FinesseSurvivalMode
from modes.tspin_survival import TSpinSurvivalMode
from modes.combo_survival import ComboSurvivalMode
from modes.speed_survival import SpeedSurvivalMode
from modes.downstack import DownstackMode
from modes.pc_survival import PCSurvivalMode

def apply_settings_to_mode(mode):
    settings = SettingsManager.load_settings()
    if hasattr(mode, 'config'):
        mode.config["das"] = settings.get("das", DAS)
        mode.config["arr"] = settings.get("arr", ARR)
        mode.config["lock_delay"] = settings.get("lock_delay", LOCK_DELAY)
        mode.config["soft_drop_speed"] = settings.get("soft_drop_speed", SOFT_DROP_SPEED)
        mode.config["show_ghost"] = settings.get("show_ghost", True)
        mode.config["hold_enabled"] = settings.get("hold_enabled", True)
        mode.config["keybinds"] = settings.get("keybinds", {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "soft_drop": pygame.K_DOWN,
            "hard_drop": pygame.K_SPACE,
            "rotate_cw": pygame.K_UP,
            "rotate_ccw": pygame.K_z,
            "rotate_180": pygame.K_a,  # <-- SE AÑADE AL FALLBACK
            "hold": pygame.K_c
        })

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pytris Trainer")
    clock = pygame.time.Clock()
    
    font = pygame.font.Font(None, 28)

    menu = MainMenu()
    current_mode = None
    current_mode_name = ""
    state = "MENU"
    last_game_stats = {}

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if state == "MENU":
                action = menu.handle_event(event, current_time)
                if action == "Salir":
                    running = False
                elif action in ["Freeplay", "Normal Survival", "Finesse Survival", "T-Spin Survival", 
                                "Combo Survival", "Speed Survival", "Downstack Survival", "PC Survival"]:
                    current_mode_name = action
                    
                    if action == "Freeplay":
                        current_mode = FreeplayMode()
                    elif action == "Normal Survival":
                        current_mode = SurvivalMode()
                    elif action == "Finesse Survival":
                        current_mode = FinesseSurvivalMode()
                    elif action == "T-Spin Survival":
                        current_mode = TSpinSurvivalMode()
                    elif action == "Combo Survival":
                        current_mode = ComboSurvivalMode()
                    elif action == "Speed Survival":
                        current_mode = SpeedSurvivalMode()
                    elif action == "Downstack Survival":
                        current_mode = DownstackMode()
                    elif action == "PC Survival":
                        current_mode = PCSurvivalMode()
                    
                    apply_settings_to_mode(current_mode)
                    state = "PLAYING"
            
            elif state == "PLAYING":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "MENU"
                else:
                    current_mode.handle_event(event, current_time)
            
            elif state == "GAMEOVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    state = "MENU"

        if state == "MENU":
            menu.update_continuous_input(current_time)
            menu.draw(screen, font)
        elif state == "PLAYING":
            game_over = current_mode.update(current_time)
            if game_over:
                state = "GAMEOVER"
            else:
                current_mode.draw(screen, font)

        elif state == "GAMEOVER":
            GameOverScreen.draw(screen, font, current_mode_name, last_game_stats)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()