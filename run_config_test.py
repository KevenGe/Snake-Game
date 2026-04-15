#!/usr/bin/env python3

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from snake_game.config import (
        COLORS,
        GRID_COLS,
        GRID_ROWS,
        CELL_SIZE,
        DifficultyLevel,
        DIFFICULTY_SETTINGS,
        POWERUP_TYPES,
        POWERUP_DURATION,
    )
    print("ERROR: Config module exists! This should fail in TDD.")
except ImportError as e:
    print(f"SUCCESS: Expected failure - {e}")
    sys.exit(0)  # Exit with 0 to indicate expected failure