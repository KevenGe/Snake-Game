from enum import Enum, auto
from typing import Dict, Any


# ── Grid ──
GRID_COLS = 25
GRID_ROWS = 20
CELL_SIZE = 40


# ── Colors ──
COLORS = {
    "background": "#0f0c29",
    "grid": "#1a1533",
    "grid_line": "rgba(176, 38, 255, 0.2)",
    "neon_cyan": "#00ffcc",
    "neon_magenta": "#ff00ff",
    "neon_purple": "#b026ff",
    "food": "#00ffcc",
    "food_glow": "rgba(0, 255, 204, 0.5)",
    "snake_head": "#00ffcc",
    "snake_body": "#00ccaa",
    "powerup_speed": "#00ffff",
    "powerup_shield": "#ff00ff",
    "powerup_score": "#ffff00",
    "powerup_time": "#ff6600",
    "powerup_extend": "#00ff00",
    "ui_bg": "rgba(15, 12, 41, 0.95)",
    "ui_text": "#e0e0ff",
}


# ── Difficulty ──
class DifficultyLevel(Enum):
    TRAINING = 0
    BEGINNER = 1
    NORMAL = 2
    HARD = 3
    INSANE = 4


DIFFICULTY_SETTINGS: Dict[DifficultyLevel, Dict[str, Any]] = {
    DifficultyLevel.TRAINING: {
        "speed": 250,
        "initial_length": 3,
        "powerup_chance": 0.30,
        "obstacles": False,
    },
    DifficultyLevel.BEGINNER: {
        "speed": 200,
        "initial_length": 3,
        "powerup_chance": 0.25,
        "obstacles": False,
    },
    DifficultyLevel.NORMAL: {
        "speed": 150,
        "initial_length": 3,
        "powerup_chance": 0.20,
        "obstacles": False,
    },
    DifficultyLevel.HARD: {
        "speed": 100,
        "initial_length": 4,
        "powerup_chance": 0.15,
        "obstacles": True,
    },
    DifficultyLevel.INSANE: {
        "speed": 60,
        "initial_length": 5,
        "powerup_chance": 0.10,
        "obstacles": True,
    },
}


# ── Powerups ──
class PowerupType(Enum):
    OVERCLOCK = "overclock"
    FIREWALL = "firewall"
    DATA_PACKET = "data_packet"
    TIME_DILATION = "time_dilation"
    ENERGY_CELL = "energy_cell"


POWERUP_TYPES = list(PowerupType)

POWERUP_DURATION: Dict[PowerupType, int] = {
    # Duration in seconds (converted to ticks at runtime)
    PowerupType.OVERCLOCK: 8,
    PowerupType.FIREWALL: 6,
    PowerupType.DATA_PACKET: 10,
    PowerupType.TIME_DILATION: 7,
    PowerupType.ENERGY_CELL: 1,  # instant consumption (but still > 0)
}

MAX_ACTIVE_POWERUPS = 2

# ── Scoring ──
SCORE_PER_FOOD = 10
DOUBLE_SCORE_MULTIPLIER = 2

# ── Leaderboard ──
LEADERBOARD_SIZE = 10
LEADERBOARD_FILE = "leaderboard.json"