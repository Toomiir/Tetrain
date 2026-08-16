import pygame
import numpy as np

class SoundManager:
    _initialized = False

    @classmethod
    def init(cls):
        if not cls._initialized:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=1)
                cls._initialized = True
            except Exception as e:
                print(f"No se pudo inicializar el audio: {e}")

    @staticmethod
    def play_sound(sound_type):
        if not SoundManager._initialized:
            return
        try:
            duration = 0.08
            sample_rate = 22050
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            
            if sound_type == "place":
                freq = 200
            elif sound_type == "hold":
                freq = 400
            elif sound_type == "combo":
                freq = 600
            elif sound_type == "tspin":
                freq = 800
            else:
                freq = 300

            wave = 0.3 * np.sin(2 * np.pi * freq * t)
            sound_data = (wave * 32767).astype(np.int16)
            sound = pygame.sndarray.make_sound(sound_data)
            sound.play()
        except Exception:
            pass # Falla silenciosa si el entorno no soporta sndarray