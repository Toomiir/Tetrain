import json
import os
import pygame
from settings import DAS, ARR, LOCK_DELAY, SOFT_DROP_SPEED

class SettingsManager:
    FILE_NAME = "pytris_config.json"

    @staticmethod
    def get_default_settings():
        return {
            "das": DAS,
            "arr": ARR,
            "lock_delay": LOCK_DELAY,
            "soft_drop_speed": SOFT_DROP_SPEED,
            "show_ghost": True,
            "hold_enabled": True,
            "keybinds": {
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "soft_drop": pygame.K_DOWN,
                "hard_drop": pygame.K_SPACE,
                "rotate_cw": pygame.K_UP,
                "rotate_ccw": pygame.K_z,
                "rotate_180": pygame.K_a,  # <-- NUEVA TECLA AQUÍ
                "hold": pygame.K_c
            }
        }

    @staticmethod
    def load_settings():
        defaults = SettingsManager.get_default_settings()
        if not os.path.exists(SettingsManager.FILE_NAME):
            return defaults
        try:
            with open(SettingsManager.FILE_NAME, "r") as f:
                loaded = json.load(f)
                for k, v in defaults.items():
                    if k not in loaded:
                        loaded[k] = v
                    elif isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            if sub_k not in loaded[k]:
                                loaded[k][sub_k] = sub_v
                return loaded
        except Exception:
            return defaults

    @staticmethod
    def save_settings(settings_dict):
        try:
            with open(SettingsManager.FILE_NAME, "w") as f:
                json.dump(settings_dict, f, indent=4)
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")