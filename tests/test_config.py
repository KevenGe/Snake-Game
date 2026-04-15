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


def test_colors_are_valid_hex():
    """All color values must be valid hex or rgba strings."""
    for key, value in COLORS.items():
        assert isinstance(value, str), f"{key} is not a string"
        assert value.startswith("#") or value.startswith("rgba"), f"{key} has invalid format: {value}"


def test_grid_dimensions_positive():
    assert GRID_COLS > 0
    assert GRID_ROWS > 0
    assert CELL_SIZE > 0


def test_difficulty_levels_count():
    assert len(DIFFICULTY_SETTINGS) == 5


def test_difficulty_settings_keys():
    required_keys = {"speed", "initial_length", "powerup_chance", "obstacles"}
    for level in DifficultyLevel:
        settings = DIFFICULTY_SETTINGS[level]
        assert required_keys.issubset(settings.keys()), f"Missing keys in {level}"


def test_powerup_types_count():
    assert len(POWERUP_TYPES) == 5


def test_powerup_durations_positive():
    for ptype, duration in POWERUP_DURATION.items():
        assert duration > 0, f"{ptype} has non-positive duration"