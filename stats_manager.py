import json
import os

class StatsManager:
    FILE_NAME = "pytris_stats.json"

    @staticmethod
    def load_stats():
        if not os.path.exists(StatsManager.FILE_NAME):
            return StatsManager.get_default_stats()
        try:
            with open(StatsManager.FILE_NAME, "r") as f:
                return json.load(f)
        except Exception:
            return StatsManager.get_default_stats()

    @staticmethod
    def save_stats(data):
        try:
            with open(StatsManager.FILE_NAME, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error al guardar estadísticas: {e}")

    @staticmethod
    def get_default_stats():
        return {
            "Combo Survival": {"max_combo": 0, "max_score": 0, "best_time": 0},
            "Speed Survival": {"max_pieces": 0, "max_score": 0, "best_time": 0},
            "Downstack Survival": {"max_lines": 0, "max_score": 0, "best_time": 0},
            "PC Survival": {"max_pcs": 0, "max_streak": 0, "best_time": 0}
        }

    @staticmethod
    def update_record(mode_name, key, value):
        stats = StatsManager.load_stats()
        if mode_name in stats:
            if value > stats[mode_name].get(key, 0):
                stats[mode_name][key] = value
                StatsManager.save_stats(stats)