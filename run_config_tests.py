#!/usr/bin/env python3

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_colors_are_valid_hex():
    """All color values must be valid hex or rgba strings."""
    from snake_game.config import COLORS

    for key, value in COLORS.items():
        assert isinstance(value, str), f"{key} is not a string"
        assert value.startswith("#") or value.startswith("rgba"), f"{key} has invalid format: {value}"
    print("✓ test_colors_are_valid_hex passed")


def test_grid_dimensions_positive():
    from snake_game.config import GRID_COLS, GRID_ROWS, CELL_SIZE

    assert GRID_COLS > 0
    assert GRID_ROWS > 0
    assert CELL_SIZE > 0
    print("✓ test_grid_dimensions_positive passed")


def test_difficulty_levels_count():
    from snake_game.config import DIFFICULTY_SETTINGS

    assert len(DIFFICULTY_SETTINGS) == 5
    print("✓ test_difficulty_levels_count passed")


def test_difficulty_settings_keys():
    from snake_game.config import DifficultyLevel, DIFFICULTY_SETTINGS

    required_keys = {"speed", "initial_length", "powerup_chance", "obstacles"}
    for level in DifficultyLevel:
        settings = DIFFICULTY_SETTINGS[level]
        assert required_keys.issubset(settings.keys()), f"Missing keys in {level}"
    print("✓ test_difficulty_settings_keys passed")


def test_powerup_types_count():
    from snake_game.config import POWERUP_TYPES

    assert len(POWERUP_TYPES) == 5
    print("✓ test_powerup_types_count passed")


def test_powerup_durations_positive():
    from snake_game.config import PowerupType, POWERUP_DURATION

    for ptype, duration in POWERUP_DURATION.items():
        assert duration > 0, f"{ptype} has non-positive duration"
    print("✓ test_powerup_durations_positive passed")


if __name__ == "__main__":
    try:
        test_colors_are_valid_hex()
        test_grid_dimensions_positive()
        test_difficulty_levels_count()
        test_difficulty_settings_keys()
        test_powerup_types_count()
        test_powerup_durations_positive()
        print("\n✓ All 6 tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)