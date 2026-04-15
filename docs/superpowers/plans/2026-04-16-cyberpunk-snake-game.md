# Cyberpunk Snake Game Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a cyberpunk neon-themed Snake game with PyQt5 featuring 5 difficulty levels, a powerup system, particle effects, sound, and a leaderboard.

**Architecture:** Modular design with separate files for config, game logic, powerups, UI, particles, sound, and leaderboard. Game logic runs on a QTimer tick; all modules communicate via Qt signals/slots. The UI uses a main window with a game canvas (QWidget paintEvent) and a sidebar for score/controls/leaderboard.

**Tech Stack:** Python 3.12+, PyQt5, uv (package manager), pytest (testing)

---

## File Structure

| File | Responsibility |
|------|---------------|
| `pyproject.toml` | Project metadata and dependencies |
| `snake_game/__init__.py` | Package marker |
| `snake_game/config.py` | All constants, colors, difficulty settings, user preferences |
| `snake_game/main.py` | Entry point — creates QApplication and launches MainWindow |
| `snake_game/game_logic.py` | Core snake movement, collision, food/powerup spawning, score |
| `snake_game/powerup_system.py` | Powerup types, activation, effect management, expiry |
| `snake_game/particle_system.py` | Particle creation, update, lifecycle management |
| `snake_game/game_ui.py` | MainWindow, game canvas painting, sidebar, virtual buttons, menus |
| `snake_game/sound_manager.py` | Sound effect playback and background music via QtMultimedia |
| `snake_game/leaderboard.py` | Top 10 score persistence to JSON, load/save/query |
| `tests/__init__.py` | Test package marker |
| `tests/test_config.py` | Config validation tests |
| `tests/test_game_logic.py` | Game logic unit tests |
| `tests/test_powerup_system.py` | Powerup system tests |
| `tests/test_particle_system.py` | Particle system tests |
| `tests/test_leaderboard.py` | Leaderboard persistence tests |
| `resources/sounds/.gitkeep` | Placeholder for sound assets |

---

### Task 1: Project Setup — pyproject.toml and Package Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `snake_game/__init__.py`
- Create: `resources/sounds/.gitkeep`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "snake-game"
version = "0.1.0"
description = "Cyberpunk neon-themed Snake game built with PyQt5"
requires-python = ">=3.12"
dependencies = [
    "pyqt5>=5.15.0",
]

[project.scripts]
snake-game = "snake_game.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create package directories and init files**

```bash
mkdir -p snake_game tests resources/sounds
touch snake_game/__init__.py tests/__init__.py resources/sounds/.gitkeep
```

- [ ] **Step 3: Install dependencies and verify**

Run: `uv sync`
Expected: Dependencies installed successfully, no errors.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml snake_game/ tests/ resources/
git commit -m "chore: initialize project with pyproject.toml and package skeleton"
```

---

### Task 2: Config Module

**Files:**
- Create: `snake_game/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write failing tests for config**

```python
# tests/test_config.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL — `snake_game.config` module does not exist.

- [ ] **Step 3: Write config module**

```python
# snake_game/config.py
from enum import Enum, auto
from typing import Dict, Any


# ── Grid ──
GRID_COLS = 25
GRID_ROWS = 20
CELL_SIZE = 25


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
    # Duration in game ticks (seconds * 1000 / speed_ms)
    # Stored as seconds for conversion at runtime
    PowerupType.OVERCLOCK: 8,
    PowerupType.FIREWALL: 6,
    PowerupType.DATA_PACKET: 10,
    PowerupType.TIME_DILATION: 7,
    PowerupType.ENERGY_CELL: 0,  # instant consumption
}

MAX_ACTIVE_POWERUPS = 2

# ── Scoring ──
SCORE_PER_FOOD = 10
DOUBLE_SCORE_MULTIPLIER = 2

# ── Leaderboard ──
LEADERBOARD_SIZE = 10
LEADERBOARD_FILE = "leaderboard.json"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_config.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add snake_game/config.py tests/test_config.py
git commit -m "feat: add config module with colors, difficulty, and powerup constants"
```

---

### Task 3: Game Logic — Core Data Structures and Snake Movement

**Files:**
- Create: `snake_game/game_logic.py`
- Test: `tests/test_game_logic.py`

- [ ] **Step 1: Write failing tests for game logic**

```python
# tests/test_game_logic.py
import pytest
from snake_game.config import DifficultyLevel, GRID_COLS, GRID_ROWS
from snake_game.game_logic import GameLogic, Direction, Position


class TestPosition:
    def test_create_position(self):
        p = Position(3, 5)
        assert p.x == 3
        assert p.y == 5

    def test_position_equality(self):
        assert Position(1, 2) == Position(1, 2)
        assert Position(1, 2) != Position(2, 1)


class TestDirection:
    def test_direction_values(self):
        assert Direction.UP.value == (0, -1)
        assert Direction.DOWN.value == (0, 1)
        assert Direction.LEFT.value == (-1, 0)
        assert Direction.RIGHT.value == (1, 0)

    def test_opposite(self):
        assert Direction.UP.opposite() == Direction.DOWN
        assert Direction.DOWN.opposite() == Direction.UP
        assert Direction.LEFT.opposite() == Direction.RIGHT
        assert Direction.RIGHT.opposite() == Direction.LEFT


class TestGameLogicInit:
    def test_initial_snake_length_training(self):
        logic = GameLogic(DifficultyLevel.TRAINING)
        assert len(logic.snake) == 3

    def test_initial_snake_length_insane(self):
        logic = GameLogic(DifficultyLevel.INSANE)
        assert len(logic.snake) == 5

    def test_initial_direction_right(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        assert logic.direction == Direction.RIGHT

    def test_initial_score_zero(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        assert logic.score == 0

    def test_initial_not_paused(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        assert not logic.paused

    def test_initial_not_game_over(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        assert not logic.game_over

    def test_food_on_grid(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        assert 0 <= logic.food.x < GRID_COLS
        assert 0 <= logic.food.y < GRID_ROWS

    def test_food_not_on_snake(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        assert logic.food not in logic.snake


class TestSnakeMovement:
    def test_move_right(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        old_head = logic.snake[0]
        logic.tick()
        new_head = logic.snake[0]
        assert new_head == Position(old_head.x + 1, old_head.y)

    def test_change_direction_up(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        logic.set_direction(Direction.UP)
        logic.tick()
        new_head = logic.snake[0]
        assert new_head.y < logic.snake[1].y

    def test_ignore_opposite_direction(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        # Snake starts moving RIGHT, pressing LEFT should be ignored
        logic.set_direction(Direction.LEFT)
        assert logic.direction == Direction.RIGHT

    def test_snake_grows_when_eating(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        initial_len = len(logic.snake)
        # Place food directly in front of the snake
        head = logic.snake[0]
        logic.food = Position(head.x + 1, head.y)
        logic.tick()
        assert len(logic.snake) == initial_len + 1

    def test_score_increases_when_eating(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        head = logic.snake[0]
        logic.food = Position(head.x + 1, head.y)
        logic.tick()
        assert logic.score == 10


class TestCollision:
    def test_wall_collision_game_over(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        # Move snake head to right wall
        head = logic.snake[0]
        logic.food = Position(head.x + 1, head.y)
        # Move until hitting right wall
        for _ in range(GRID_COLS):
            if logic.game_over:
                break
            logic.tick()
        assert logic.game_over

    def test_self_collision_game_over(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        # Create a snake that will collide with itself
        # Place snake in a U shape
        logic._snake = [
            Position(5, 5),
            Position(5, 4),
            Position(4, 4),
            Position(3, 4),
            Position(3, 5),
            Position(3, 6),
        ]
        logic.direction = Direction.UP
        logic.set_direction(Direction.LEFT)
        logic.tick()
        # Head moves to (4, 5), not a self-collision
        # Now set up for actual self collision
        logic._snake = [
            Position(5, 5),
            Position(6, 5),
            Position(6, 4),
            Position(5, 4),
            Position(4, 4),
            Position(4, 5),
        ]
        logic.direction = Direction.LEFT
        logic.tick()
        assert logic.game_over
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_game_logic.py -v`
Expected: FAIL — `snake_game.game_logic` module does not exist.

- [ ] **Step 3: Write game logic module**

```python
# snake_game/game_logic.py
from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from snake_game.config import (
    CELL_SIZE,
    DIFFICULTY_SETTINGS,
    GRID_COLS,
    GRID_ROWS,
    SCORE_PER_FOOD,
    DifficultyLevel,
)


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def opposite(self) -> Direction:
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[self]

    def delta(self) -> tuple[int, int]:
        return self.value


@dataclass(frozen=True)
class Position:
    x: int
    y: int


class GameLogic:
    def __init__(self, difficulty: DifficultyLevel = DifficultyLevel.NORMAL) -> None:
        self.difficulty = difficulty
        settings = DIFFICULTY_SETTINGS[difficulty]
        self.speed_ms: int = settings["speed"]
        initial_length: int = settings["initial_length"]

        # Snake starts at center-left, heading right
        start_x = GRID_COLS // 4
        start_y = GRID_ROWS // 2
        self._snake: List[Position] = [
            Position(start_x - i, start_y) for i in range(initial_length)
        ]
        self.direction: Direction = Direction.RIGHT
        self._next_direction: Direction = Direction.RIGHT

        self.score: int = 0
        self.paused: bool = False
        self.game_over: bool = False
        self.invincible: bool = False

        self.food: Position = self._random_free_position()
        self.powerups_on_board: List[tuple[Position, str]] = []

    # ── Public API ──

    @property
    def snake(self) -> List[Position]:
        return list(self._snake)

    def set_direction(self, direction: Direction) -> None:
        """Buffer a direction change. Applied on next tick."""
        if direction != self.direction.opposite():
            self._next_direction = direction

    def tick(self) -> None:
        """Advance one game frame."""
        if self.paused or self.game_over:
            return

        self.direction = self._next_direction
        dx, dy = self.direction.delta()
        head = self._snake[0]
        new_head = Position(head.x + dx, head.y + dy)

        # Wall collision
        if not self.invincible:
            if not (0 <= new_head.x < GRID_COLS and 0 <= new_head.y < GRID_ROWS):
                self.game_over = True
                return
        else:
            # Wrap around when invincible
            new_head = Position(new_head.x % GRID_COLS, new_head.y % GRID_ROWS)

        # Self collision
        if not self.invincible and new_head in self._snake:
            self.game_over = True
            return

        self._snake.insert(0, new_head)

        # Check food
        if new_head == self.food:
            self.score += SCORE_PER_FOOD
            self.food = self._random_free_position()
            # Don't remove tail — snake grows
        else:
            self._snake.pop()

    # ── Helpers ──

    def _random_free_position(self) -> Position:
        """Return a random position not occupied by the snake or existing powerups."""
        occupied = set(self._snake)
        for pos, _ in self.powerups_on_board:
            occupied.add(pos)
        occupied.add(self.food) if hasattr(self, "food") else None

        free = [
            Position(x, y)
            for x in range(GRID_COLS)
            for y in range(GRID_ROWS)
            if Position(x, y) not in occupied
        ]
        if not free:
            return Position(0, 0)  # Edge case: board full
        return random.choice(free)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_game_logic.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add snake_game/game_logic.py tests/test_game_logic.py
git commit -m "feat: add game logic with snake movement, collision, and food"
```

---

### Task 4: Powerup System

**Files:**
- Create: `snake_game/powerup_system.py`
- Test: `tests/test_powerup_system.py`

- [ ] **Step 1: Write failing tests for powerup system**

```python
# tests/test_powerup_system.py
import pytest
from snake_game.config import PowerupType, MAX_ACTIVE_POWERUPS
from snake_game.powerup_system import PowerupSystem, ActivePowerup


class TestActivePowerup:
    def test_create(self):
        ap = ActivePowerup(powerup_type=PowerupType.OVERCLOCK, total_ticks=80)
        assert ap.powerup_type == PowerupType.OVERCLOCK
        assert ap.remaining_ticks == 80
        assert not ap.expired

    def test_tick_decrements(self):
        ap = ActivePowerup(powerup_type=PowerupType.OVERCLOCK, total_ticks=5)
        ap.tick()
        assert ap.remaining_ticks == 4

    def test_expired_when_zero(self):
        ap = ActivePowerup(powerup_type=PowerupType.OVERCLOCK, total_ticks=1)
        ap.tick()
        assert ap.expired
        assert ap.remaining_ticks == 0


class TestPowerupSystem:
    def test_initially_no_active_powerups(self):
        system = PowerupSystem(speed_ms=150)
        assert system.active_powerups == []

    def test_should_spawn_rolls_dice(self):
        system = PowerupSystem(speed_ms=150)
        # With 100% chance, should always spawn
        assert system.should_spawn(1.0)
        # With 0% chance, should never spawn
        assert not system.should_spawn(0.0)

    def test_activate_powerup(self):
        system = PowerupSystem(speed_ms=150)
        system.activate(PowerupType.OVERCLOCK)
        assert len(system.active_powerups) == 1
        assert system.active_powerups[0].powerup_type == PowerupType.OVERCLOCK

    def test_max_active_powerups(self):
        system = PowerupSystem(speed_ms=150)
        for i in range(MAX_ACTIVE_POWERUPS + 2):
            system.activate(PowerupType.OVERCLOCK)
        assert len(system.active_powerups) <= MAX_ACTIVE_POWERUPS

    def test_tick_expires_powerup(self):
        system = PowerupSystem(speed_ms=150)
        system.activate(PowerupType.OVERCLOCK)
        # Overclock lasts 8 seconds at 150ms = ~53 ticks
        for _ in range(100):
            system.tick()
        assert len(system.active_powerups) == 0

    def test_has_effect(self):
        system = PowerupSystem(speed_ms=150)
        assert not system.has_effect(PowerupType.OVERCLOCK)
        system.activate(PowerupType.OVERCLOCK)
        assert system.has_effect(PowerupType.OVERCLOCK)

    def test_overclock_speed_multiplier(self):
        system = PowerupSystem(speed_ms=150)
        system.activate(PowerupType.OVERCLOCK)
        effective = system.effective_speed()
        assert effective < 150  # faster

    def test_time_dilation_speed_multiplier(self):
        system = PowerupSystem(speed_ms=150)
        system.activate(PowerupType.TIME_DILATION)
        effective = system.effective_speed()
        assert effective > 150  # slower

    def test_double_score_active(self):
        system = PowerupSystem(speed_ms=150)
        assert not system.double_score_active()
        system.activate(PowerupType.DATA_PACKET)
        assert system.double_score_active()

    def test_energy_cell_extends_powerups(self):
        system = PowerupSystem(speed_ms=150)
        system.activate(PowerupType.OVERCLOCK)
        ticks_before = system.active_powerups[0].remaining_ticks
        system.activate(PowerupType.ENERGY_CELL)
        # Energy cell should extend other powerups, not appear as active
        assert system.active_powerups[0].remaining_ticks > ticks_before
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_powerup_system.py -v`
Expected: FAIL — `snake_game.powerup_system` module does not exist.

- [ ] **Step 3: Write powerup system module**

```python
# snake_game/powerup_system.py
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List

from snake_game.config import (
    MAX_ACTIVE_POWERUPS,
    POWERUP_DURATION,
    PowerupType,
)


EXTEND_RATIO = 0.5  # Energy cell extends existing powerups by 50%


@dataclass
class ActivePowerup:
    powerup_type: PowerupType
    total_ticks: int
    remaining_ticks: int = 0

    def __post_init__(self) -> None:
        if self.remaining_ticks == 0:
            self.remaining_ticks = self.total_ticks

    def tick(self) -> None:
        if self.remaining_ticks > 0:
            self.remaining_ticks -= 1

    @property
    def expired(self) -> bool:
        return self.remaining_ticks <= 0

    @property
    def progress(self) -> float:
        """Returns 0.0–1.0 progress through the powerup's duration."""
        if self.total_ticks == 0:
            return 1.0
        return 1.0 - (self.remaining_ticks / self.total_ticks)


class PowerupSystem:
    def __init__(self, speed_ms: int) -> None:
        self._speed_ms = speed_ms
        self.active_powerups: List[ActivePowerup] = []

    def should_spawn(self, powerup_chance: float) -> bool:
        """Roll the dice: should a powerup spawn after eating food?"""
        return random.random() < powerup_chance

    def activate(self, powerup_type: PowerupType) -> None:
        """Activate a powerup. Energy cell extends existing powerups instead."""
        if powerup_type == PowerupType.ENERGY_CELL:
            self._extend_all()
            return

        if len(self.active_powerups) >= MAX_ACTIVE_POWERUPS:
            # Remove the oldest non-energy-cell powerup to make room
            self.active_powerups.pop(0)

        duration_secs = POWERUP_DURATION[powerup_type]
        ticks = int(duration_secs * 1000 / self._speed_ms)
        self.active_powerups.append(
            ActivePowerup(powerup_type=powerup_type, total_ticks=ticks)
        )

    def tick(self) -> None:
        """Decrement all active powerups. Remove expired ones."""
        for ap in self.active_powerups:
            ap.tick()
        self.active_powerups = [ap for ap in self.active_powerups if not ap.expired]

    def has_effect(self, powerup_type: PowerupType) -> bool:
        return any(ap.powerup_type == powerup_type for ap in self.active_powerups)

    def double_score_active(self) -> bool:
        return self.has_effect(PowerupType.DATA_PACKET)

    def invincibility_active(self) -> bool:
        return self.has_effect(PowerupType.FIREWALL)

    def effective_speed(self) -> int:
        """Return the effective game speed in ms, accounting for powerups."""
        speed = self._speed_ms
        if self.has_effect(PowerupType.OVERCLOCK):
            speed = int(speed * 0.7)  # 30% faster
        if self.has_effect(PowerupType.TIME_DILATION):
            speed = int(speed * 1.5)  # 50% slower
        return max(speed, 20)  # floor at 20ms

    def _extend_all(self) -> None:
        """Energy cell: extend all active powerups by 50% of their original duration."""
        for ap in self.active_powerups:
            bonus = int(ap.total_ticks * EXTEND_RATIO)
            ap.remaining_ticks += bonus
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_powerup_system.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add snake_game/powerup_system.py tests/test_powerup_system.py
git commit -m "feat: add powerup system with 5 powerup types and effect management"
```

---

### Task 5: Particle System

**Files:**
- Create: `snake_game/particle_system.py`
- Test: `tests/test_particle_system.py`

- [ ] **Step 1: Write failing tests for particle system**

```python
# tests/test_particle_system.py
import pytest
from snake_game.particle_system import ParticleSystem, Particle


class TestParticle:
    def test_create_particle(self):
        p = Particle(x=10, y=20, vx=1, vy=-1, color="#00ffcc", size=4, life=1.0, decay=0.05)
        assert p.x == 10
        assert p.y == 20
        assert p.life == 1.0
        assert not p.dead

    def test_particle_update(self):
        p = Particle(x=10, y=20, vx=5, vy=-3, color="#00ffcc", size=4, life=1.0, decay=0.1)
        p.update()
        assert p.x == 15
        assert p.y == 17
        assert p.life == 0.9

    def test_particle_dies(self):
        p = Particle(x=0, y=0, vx=0, vy=0, color="#000", size=1, life=0.1, decay=0.2)
        p.update()
        assert p.dead


class TestParticleSystem:
    def test_initially_empty(self):
        system = ParticleSystem()
        assert len(system.particles) == 0

    def test_spawn_eat_food(self):
        system = ParticleSystem()
        system.spawn_eat_food(x=10, y=15)
        assert len(system.particles) == 20

    def test_spawn_eat_powerup(self):
        system = ParticleSystem()
        system.spawn_eat_powerup(x=5, y=5, color="#ff00ff")
        assert len(system.particles) == 30

    def test_spawn_game_over(self):
        system = ParticleSystem()
        system.spawn_game_over(x=12, y=10)
        assert len(system.particles) == 100

    def test_update_removes_dead(self):
        system = ParticleSystem()
        system.spawn_eat_food(x=0, y=0)
        # Run many updates to let all particles die
        for _ in range(200):
            system.update()
        assert len(system.particles) == 0

    def test_spawn_wall_warp(self):
        system = ParticleSystem()
        system.spawn_wall_warp(x=0, y=10)
        assert len(system.particles) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_particle_system.py -v`
Expected: FAIL — `snake_game.particle_system` module does not exist.

- [ ] **Step 3: Write particle system module**

```python
# snake_game/particle_system.py
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: str
    size: float
    life: float  # 0.0–1.0
    decay: float  # life lost per update

    @property
    def dead(self) -> bool:
        return self.life <= 0

    @property
    def alpha(self) -> float:
        return max(0.0, self.life)

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def update(self) -> None:
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.dead]

    def spawn_eat_food(self, x: float, y: float) -> None:
        """Explosion burst — 20 cyan particles."""
        self._burst(x, y, color="#00ffcc", count=20, speed_range=(1, 5),
                    size_range=(2, 5), life=1.0, decay=0.05)

    def spawn_eat_powerup(self, x: float, y: float, color: str) -> None:
        """Spiral burst — 30 particles in the powerup's color."""
        self._spiral(x, y, color=color, count=30, life=1.5, decay=0.04)

    def spawn_game_over(self, x: float, y: float) -> None:
        """Fragment burst — 100 particles."""
        self._burst(x, y, color="#00ccaa", count=100, speed_range=(1, 8),
                    size_range=(2, 6), life=2.0, decay=0.02)

    def spawn_wall_warp(self, x: float, y: float) -> None:
        """Ripple from the warp point — purple."""
        self._ripple(x, y, color="#b026ff", count=25, life=1.0, decay=0.06)

    # ── Spawn patterns ──

    def _burst(self, x: float, y: float, color: str, count: int,
               speed_range: tuple[float, float], size_range: tuple[float, float],
               life: float, decay: float) -> None:
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=color,
                size=random.uniform(*size_range),
                life=life,
                decay=decay,
            ))

    def _spiral(self, x: float, y: float, color: str, count: int,
                life: float, decay: float) -> None:
        for i in range(count):
            angle = (2 * math.pi / count) * i
            speed = 2 + (i / count) * 3
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=color,
                size=random.uniform(2, 5),
                life=life,
                decay=decay,
            ))

    def _ripple(self, x: float, y: float, color: str, count: int,
                life: float, decay: float) -> None:
        for i in range(count):
            angle = (2 * math.pi / count) * i
            speed = 3
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=color,
                size=random.uniform(1, 3),
                life=life,
                decay=decay,
            ))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_particle_system.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add snake_game/particle_system.py tests/test_particle_system.py
git commit -m "feat: add particle system with burst, spiral, and ripple patterns"
```

---

### Task 6: Leaderboard

**Files:**
- Create: `snake_game/leaderboard.py`
- Test: `tests/test_leaderboard.py`

- [ ] **Step 1: Write failing tests for leaderboard**

```python
# tests/test_leaderboard.py
import json
import pytest
from pathlib import Path
from snake_game.leaderboard import Leaderboard, LeaderboardEntry


class TestLeaderboardEntry:
    def test_create_entry(self):
        entry = LeaderboardEntry(name="Player1", score=100, difficulty="Normal")
        assert entry.name == "Player1"
        assert entry.score == 100


class TestLeaderboard:
    def test_empty_leaderboard(self, tmp_path):
        lb = Leaderboard(filepath=tmp_path / "lb.json")
        assert lb.top_scores() == []

    def test_add_score(self, tmp_path):
        lb = Leaderboard(filepath=tmp_path / "lb.json")
        lb.add_score("Alice", 200, "Normal")
        scores = lb.top_scores()
        assert len(scores) == 1
        assert scores[0].name == "Alice"
        assert scores[0].score == 200

    def test_top_10_only(self, tmp_path):
        lb = Leaderboard(filepath=tmp_path / "lb.json")
        for i in range(15):
            lb.add_score(f"P{i}", (i + 1) * 10, "Normal")
        assert len(lb.top_scores()) == 10

    def test_sorted_descending(self, tmp_path):
        lb = Leaderboard(filepath=tmp_path / "lb.json")
        lb.add_score("Low", 50, "Normal")
        lb.add_score("High", 300, "Normal")
        lb.add_score("Mid", 150, "Normal")
        scores = lb.top_scores()
        assert scores[0].score == 300
        assert scores[1].score == 150
        assert scores[2].score == 50

    def test_persistence(self, tmp_path):
        path = tmp_path / "lb.json"
        lb1 = Leaderboard(filepath=path)
        lb1.add_score("Alice", 200, "Normal")
        # Load again
        lb2 = Leaderboard(filepath=path)
        assert len(lb2.top_scores()) == 1
        assert lb2.top_scores()[0].name == "Alice"

    def test_corrupted_file_recovery(self, tmp_path):
        path = tmp_path / "lb.json"
        path.write_text("NOT VALID JSON{{{")
        lb = Leaderboard(filepath=path)
        assert lb.top_scores() == []

    def test_is_high_score(self, tmp_path):
        lb = Leaderboard(filepath=tmp_path / "lb.json")
        for i in range(10):
            lb.add_score(f"P{i}", (i + 1) * 10, "Normal")
        # Score of 5 should not be top 10 (minimum is 10)
        assert not lb.is_high_score(5)
        # Score of 200 should be top 10
        assert lb.is_high_score(200)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_leaderboard.py -v`
Expected: FAIL — `snake_game.leaderboard` module does not exist.

- [ ] **Step 3: Write leaderboard module**

```python
# snake_game/leaderboard.py
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from snake_game.config import LEADERBOARD_SIZE


@dataclass
class LeaderboardEntry:
    name: str
    score: int
    difficulty: str


class Leaderboard:
    def __init__(self, filepath: Path) -> None:
        self._filepath = filepath
        self._entries: List[LeaderboardEntry] = []
        self._load()

    def add_score(self, name: str, score: int, difficulty: str) -> None:
        self._entries.append(LeaderboardEntry(name=name, score=score, difficulty=difficulty))
        self._entries.sort(key=lambda e: e.score, reverse=True)
        self._entries = self._entries[:LEADERBOARD_SIZE]
        self._save()

    def top_scores(self) -> List[LeaderboardEntry]:
        return list(self._entries)

    def is_high_score(self, score: int) -> bool:
        if len(self._entries) < LEADERBOARD_SIZE:
            return True
        return score > self._entries[-1].score

    def _load(self) -> None:
        if not self._filepath.exists():
            self._entries = []
            return
        try:
            data = json.loads(self._filepath.read_text(encoding="utf-8"))
            self._entries = [LeaderboardEntry(**e) for e in data]
        except (json.JSONDecodeError, TypeError, KeyError):
            self._entries = []

    def _save(self) -> None:
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(e) for e in self._entries]
        self._filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_leaderboard.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add snake_game/leaderboard.py tests/test_leaderboard.py
git commit -m "feat: add leaderboard with JSON persistence and top-10 tracking"
```

---

### Task 7: Sound Manager

**Files:**
- Create: `snake_game/sound_manager.py`

This module wraps QtMultimedia for sound effects and background music. No unit tests (requires Qt runtime), but manual testing will be done when the UI is complete.

- [ ] **Step 1: Write sound manager module**

```python
# snake_game/sound_manager.py
from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from PyQt5.QtMultimedia import QMediaPlayer, QSoundEffect, QMediaContent
    from PyQt5.QtCore import QUrl
    HAS_QTMULTIMEDIA = True
except ImportError:
    HAS_QTMULTIMEDIA = False


SOUNDS_DIR = Path(__file__).parent.parent / "resources" / "sounds"

# Sound file names expected in resources/sounds/
SOUND_FILES = {
    "eat": "eat.wav",
    "powerup": "powerup.wav",
    "wall_hit": "wall_hit.wav",
    "self_hit": "self_hit.wav",
    "game_start": "game_start.wav",
    "pause": "pause.wav",
    "powerup_expire": "powerup_expire.wav",
    "bgm": "bgm.mp3",
}


class SoundManager:
    def __init__(self) -> None:
        self._muted = False
        self._volume = 0.7
        self._sounds: dict[str, QSoundEffect] = {}
        self._bgm_player: Optional[QMediaPlayer] = None

        if not HAS_QTMULTIMEDIA:
            return

        self._bgm_player = QMediaPlayer()
        self._load_sounds()

    def _load_sounds(self) -> None:
        if not HAS_QTMULTIMEDIA:
            return
        for key, filename in SOUND_FILES.items():
            if key == "bgm":
                continue
            filepath = SOUNDS_DIR / filename
            effect = QSoundEffect()
            if filepath.exists():
                effect.setSource(QUrl.fromLocalFile(str(filepath)))
            effect.setVolume(self._volume)
            self._sounds[key] = effect

    def play(self, sound_name: str) -> None:
        if self._muted or not HAS_QTMULTIMEDIA:
            return
        effect = self._sounds.get(sound_name)
        if effect and effect.source().isValid():
            effect.play()

    def play_bgm(self) -> None:
        if self._muted or not HAS_QTMULTIMEDIA or self._bgm_player is None:
            return
        bgm_path = SOUNDS_DIR / SOUND_FILES["bgm"]
        if bgm_path.exists():
            self._bgm_player.setMedia(QMediaContent(QUrl.fromLocalFile(str(bgm_path))))
            self._bgm_player.setVolume(int(self._volume * 100))
            self._bgm_player.play()

    def stop_bgm(self) -> None:
        if self._bgm_player is not None:
            self._bgm_player.stop()

    def set_volume(self, volume: float) -> None:
        """Set volume 0.0–1.0."""
        self._volume = max(0.0, min(1.0, volume))
        for effect in self._sounds.values():
            effect.setVolume(self._volume)
        if self._bgm_player:
            self._bgm_player.setVolume(int(self._volume * 100))

    def toggle_mute(self) -> bool:
        """Toggle mute. Returns new muted state."""
        self._muted = not self._muted
        if self._muted:
            self.stop_bgm()
        else:
            self.play_bgm()
        return self._muted

    @property
    def muted(self) -> bool:
        return self._muted
```

- [ ] **Step 2: Verify the module imports without error**

Run: `uv run python -c "from snake_game.sound_manager import SoundManager; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add snake_game/sound_manager.py
git commit -m "feat: add sound manager with QtMultimedia support and graceful degradation"
```

---

### Task 8: Integrate Powerups and Particles into Game Logic

**Files:**
- Modify: `snake_game/game_logic.py`

- [ ] **Step 1: Write failing tests for powerup integration in game logic**

Append to `tests/test_game_logic.py`:

```python
from snake_game.config import PowerupType
from snake_game.powerup_system import PowerupSystem
from snake_game.particle_system import ParticleSystem


class TestPowerupIntegration:
    def test_powerup_system_initialized(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        assert hasattr(logic, "powerup_system")
        assert isinstance(logic.powerup_system, PowerupSystem)

    def test_particle_system_initialized(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        assert hasattr(logic, "particle_system")
        assert isinstance(logic.particle_system, ParticleSystem)

    def test_eat_food_may_spawn_powerup(self):
        logic = GameLogic(DifficultyLevel.TRAINING)  # 30% powerup chance
        head = logic.snake[0]
        logic.food = Position(head.x + 1, head.y)
        logic.tick()
        # Food was eaten; a powerup may have been placed on the board
        # (non-deterministic, so we just check the mechanism runs)
        assert isinstance(logic.powerups_on_board, list)

    def test_eat_powerup_activates_it(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        head = logic.snake[0]
        powerup_pos = Position(head.x + 1, head.y)
        logic.powerups_on_board = [(powerup_pos, PowerupType.OVERCLOCK)]
        logic.food = Position(head.x + 2, head.y)
        logic.tick()
        # Powerup eaten, should be activated
        assert logic.powerup_system.has_effect(PowerupType.OVERCLOCK)
        assert len(logic.powerups_on_board) == 0

    def test_invincibility_from_firewall(self):
        logic = GameLogic(DifficultyLevel.NORMAL)
        head = logic.snake[0]
        # Activate firewall
        logic.powerup_system.activate(PowerupType.FIREWALL)
        logic.invincible = logic.powerup_system.invincibility_active()
        assert logic.invincible
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_game_logic.py::TestPowerupIntegration -v`
Expected: FAIL — `GameLogic` has no `powerup_system` or `particle_system`.

- [ ] **Step 3: Update game_logic.py to integrate powerups and particles**

Read `snake_game/game_logic.py` and update it. Replace the full file with:

```python
# snake_game/game_logic.py
from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from snake_game.config import (
    DIFFICULTY_SETTINGS,
    GRID_COLS,
    GRID_ROWS,
    SCORE_PER_FOOD,
    DifficultyLevel,
    PowerupType,
)
from snake_game.particle_system import ParticleSystem
from snake_game.powerup_system import PowerupSystem


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def opposite(self) -> Direction:
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[self]

    def delta(self) -> tuple[int, int]:
        return self.value


@dataclass(frozen=True)
class Position:
    x: int
    y: int


class GameLogic:
    def __init__(self, difficulty: DifficultyLevel = DifficultyLevel.NORMAL) -> None:
        self.difficulty = difficulty
        settings = DIFFICULTY_SETTINGS[difficulty]
        self.speed_ms: int = settings["speed"]
        initial_length: int = settings["initial_length"]
        self._powerup_chance: float = settings["powerup_chance"]

        # Snake starts at center-left, heading right
        start_x = GRID_COLS // 4
        start_y = GRID_ROWS // 2
        self._snake: List[Position] = [
            Position(start_x - i, start_y) for i in range(initial_length)
        ]
        self.direction: Direction = Direction.RIGHT
        self._next_direction: Direction = Direction.RIGHT

        self.score: int = 0
        self.paused: bool = False
        self.game_over: bool = False
        self.invincible: bool = False

        self.food: Position = self._random_free_position()
        self.powerups_on_board: List[tuple[Position, PowerupType]] = []

        self.powerup_system = PowerupSystem(self.speed_ms)
        self.particle_system = ParticleSystem()

    # ── Public API ──

    @property
    def snake(self) -> List[Position]:
        return list(self._snake)

    def set_direction(self, direction: Direction) -> None:
        """Buffer a direction change. Applied on next tick."""
        if direction != self.direction.opposite():
            self._next_direction = direction

    def tick(self) -> None:
        """Advance one game frame."""
        if self.paused or self.game_over:
            return

        self.direction = self._next_direction
        self._update_invincibility()

        dx, dy = self.direction.delta()
        head = self._snake[0]
        new_head = Position(head.x + dx, head.y + dy)

        # Wall collision
        if not self.invincible:
            if not (0 <= new_head.x < GRID_COLS and 0 <= new_head.y < GRID_ROWS):
                self.game_over = True
                self.particle_system.spawn_game_over(head.x, head.y)
                return
        else:
            # Wrap around when invincible
            new_head = Position(new_head.x % GRID_COLS, new_head.y % GRID_ROWS)
            if new_head.x != head.x + dx or new_head.y != head.y + dy:
                # Warped through wall
                self.particle_system.spawn_wall_warp(head.x, head.y)

        # Self collision
        if not self.invincible and new_head in self._snake:
            self.game_over = True
            self.particle_system.spawn_game_over(head.x, head.y)
            return

        self._snake.insert(0, new_head)

        # Check food
        if new_head == self.food:
            self._eat_food(new_head)
        else:
            self._snake.pop()

        # Check powerup pickup
        for i, (pos, ptype) in enumerate(self.powerups_on_board):
            if new_head == pos:
                self._eat_powerup(pos, ptype)
                self.powerups_on_board.pop(i)
                break

        # Update systems
        self.powerup_system.tick()
        self.particle_system.update()

    # ── Internal ──

    def _update_invincibility(self) -> None:
        self.invincible = self.powerup_system.invincibility_active()

    def _eat_food(self, pos: Position) -> None:
        multiplier = 2 if self.powerup_system.double_score_active() else 1
        self.score += SCORE_PER_FOOD * multiplier
        self.food = self._random_free_position()
        self.particle_system.spawn_eat_food(pos.x, pos.y)

        # Maybe spawn a powerup
        if self.powerup_system.should_spawn(self._powerup_chance):
            self._spawn_random_powerup()

    def _eat_powerup(self, pos: Position, ptype: PowerupType) -> None:
        from snake_game.config import COLORS
        color_map = {
            PowerupType.OVERCLOCK: COLORS["powerup_speed"],
            PowerupType.FIREWALL: COLORS["powerup_shield"],
            PowerupType.DATA_PACKET: COLORS["powerup_score"],
            PowerupType.TIME_DILATION: COLORS["powerup_time"],
            PowerupType.ENERGY_CELL: COLORS["powerup_extend"],
        }
        self.powerup_system.activate(ptype)
        self.particle_system.spawn_eat_powerup(pos.x, pos.y, color_map.get(ptype, "#ffffff"))

    def _spawn_random_powerup(self) -> None:
        if len(self.powerups_on_board) >= 2:
            return
        pos = self._random_free_position()
        ptype = random.choice(list(PowerupType))
        self.powerups_on_board.append((pos, ptype))

    # ── Helpers ──

    def _random_free_position(self) -> Position:
        """Return a random position not occupied by the snake, food, or powerups."""
        occupied = set(self._snake)
        occupied.add(self.food) if hasattr(self, "food") else None
        for pos, _ in self.powerups_on_board:
            occupied.add(pos)

        free = [
            Position(x, y)
            for x in range(GRID_COLS)
            for y in range(GRID_ROWS)
            if Position(x, y) not in occupied
        ]
        if not free:
            return Position(0, 0)
        return random.choice(free)
```

- [ ] **Step 4: Run all tests to verify they pass**

Run: `uv run pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add snake_game/game_logic.py tests/test_game_logic.py
git commit -m "feat: integrate powerup and particle systems into game logic"
```

---

### Task 9: Game UI — Main Window and Canvas Rendering

**Files:**
- Create: `snake_game/game_ui.py`

This is the largest module. It contains the MainWindow with game canvas painting and sidebar. No unit tests for UI painting (requires Qt runtime), but the game will be manually tested on launch.

- [ ] **Step 1: Write the game UI module**

```python
# snake_game/game_ui.py
from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont,
    QLinearGradient, QRadialGradient,
)

from snake_game.config import (
    CELL_SIZE, GRID_COLS, GRID_ROWS, COLORS,
    DifficultyLevel, PowerupType, POWERUP_DURATION,
)
from snake_game.game_logic import GameLogic, Direction, Position
from snake_game.leaderboard import Leaderboard
from snake_game.sound_manager import SoundManager
from pathlib import Path


# ── Game Canvas ──

class GameCanvas(QWidget):
    """Custom widget that renders the game grid, snake, food, powerups, and particles."""

    def __init__(self, logic: GameLogic, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.logic = logic
        self.setFixedSize(GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self._draw_background(painter)
        self._draw_grid(painter)
        self._draw_particles(painter)
        self._draw_food(painter)
        self._draw_powerups(painter)
        self._draw_snake(painter)
        self._draw_game_over(painter)
        painter.end()

    def _draw_background(self, p: QPainter) -> None:
        p.fillRect(self.rect(), QColor(COLORS["background"]))

    def _draw_grid(self, p: QPainter) -> None:
        pen = QPen(QColor(176, 38, 255, 50), 1)
        p.setPen(pen)
        for x in range(0, GRID_COLS * CELL_SIZE + 1, CELL_SIZE):
            p.drawLine(x, 0, x, GRID_ROWS * CELL_SIZE)
        for y in range(0, GRID_ROWS * CELL_SIZE + 1, CELL_SIZE):
            p.drawLine(0, y, GRID_COLS * CELL_SIZE, y)

    def _draw_food(self, p: QPainter) -> None:
        fx = self.logic.food.x * CELL_SIZE + CELL_SIZE // 2
        fy = self.logic.food.y * CELL_SIZE + CELL_SIZE // 2
        # Glow
        gradient = QRadialGradient(fx, fy, CELL_SIZE)
        gradient.setColorAt(0, QColor(0, 255, 204, 120))
        gradient.setColorAt(1, QColor(0, 255, 204, 0))
        p.setBrush(QBrush(gradient))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(fx, fy), CELL_SIZE * 0.6, CELL_SIZE * 0.6)
        # Core
        p.setBrush(QBrush(QColor(COLORS["food"])))
        radius = CELL_SIZE * 0.3
        p.drawEllipse(QPointF(fx, fy), radius, radius)

    def _draw_powerups(self, p: QPainter) -> None:
        color_map = {
            PowerupType.OVERCLOCK: COLORS["powerup_speed"],
            PowerupType.FIREWALL: COLORS["powerup_shield"],
            PowerupType.DATA_PACKET: COLORS["powerup_score"],
            PowerupType.TIME_DILATION: COLORS["powerup_time"],
            PowerupType.ENERGY_CELL: COLORS["powerup_extend"],
        }
        icon_map = {
            PowerupType.OVERCLOCK: "◈",
            PowerupType.FIREWALL: "⬡",
            PowerupType.DATA_PACKET: "✦",
            PowerupType.TIME_DILATION: "⧉",
            PowerupType.ENERGY_CELL: "⚡",
        }
        for pos, ptype in self.logic.powerups_on_board:
            px = pos.x * CELL_SIZE
            py = pos.y * CELL_SIZE
            color = QColor(color_map.get(ptype, "#ffffff"))
            # Glow
            gradient = QRadialGradient(px + CELL_SIZE / 2, py + CELL_SIZE / 2, CELL_SIZE)
            gradient.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 100))
            gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
            p.setBrush(QBrush(gradient))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(px + CELL_SIZE / 2, py + CELL_SIZE / 2),
                          CELL_SIZE * 0.6, CELL_SIZE * 0.6)
            # Icon
            p.setPen(QPen(color))
            p.setFont(QFont("Segoe UI Symbol", int(CELL_SIZE * 0.6)))
            p.drawText(QRectF(px, py, CELL_SIZE, CELL_SIZE), Qt.AlignCenter,
                       icon_map.get(ptype, "?"))

    def _draw_snake(self, p: QPainter) -> None:
        for i, seg in enumerate(self.logic.snake):
            sx = seg.x * CELL_SIZE
            sy = seg.y * CELL_SIZE
            is_head = i == 0
            color = QColor(COLORS["snake_head"] if is_head else COLORS["snake_body"])
            # Glow for head
            if is_head:
                gradient = QRadialGradient(sx + CELL_SIZE / 2, sy + CELL_SIZE / 2, CELL_SIZE)
                gradient.setColorAt(0, QColor(0, 255, 204, 80))
                gradient.setColorAt(1, QColor(0, 255, 204, 0))
                p.setBrush(QBrush(gradient))
                p.setPen(Qt.NoPen)
                p.drawEllipse(QPointF(sx + CELL_SIZE / 2, sy + CELL_SIZE / 2),
                              CELL_SIZE * 0.8, CELL_SIZE * 0.8)
            # Body segment
            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            margin = 2
            p.drawRoundedRect(sx + margin, sy + margin,
                              CELL_SIZE - 2 * margin, CELL_SIZE - 2 * margin,
                              4, 4)

    def _draw_particles(self, p: QPainter) -> None:
        for particle in self.logic.particle_system.particles:
            color = QColor(particle.color)
            color.setAlphaF(particle.alpha)
            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(particle.x * CELL_SIZE, particle.y * CELL_SIZE),
                          particle.size, particle.size)

    def _draw_game_over(self, p: QPainter) -> None:
        if not self.logic.game_over:
            return
        p.fillRect(self.rect(), QColor(0, 0, 0, 150))
        p.setPen(QPen(QColor(COLORS["neon_magenta"])))
        p.setFont(QFont("Segoe UI", 36, QFont.Bold))
        p.drawText(self.rect(), Qt.AlignCenter, "GAME OVER")


# ── Sidebar ──

class Sidebar(QFrame):
    """Right sidebar: score, active powerups, controls, leaderboard."""

    direction_requested = pyqtSignal(object)  # Direction

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS["ui_bg"]};
                border-left: 2px solid {COLORS["neon_purple"]};
            }}
            QLabel {{
                color: {COLORS["ui_text"]};
                font-size: 14px;
            }}
            QPushButton {{
                background: transparent;
                border: 2px solid {COLORS["neon_cyan"]};
                color: {COLORS["neon_cyan"]};
                border-radius: 6px;
                padding: 10px;
                font-size: 18px;
            }}
            QPushButton:pressed {{
                background: rgba(0, 255, 204, 0.3);
            }}
        """)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # Score
        self.score_label = QLabel("Score: 0")
        self.score_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.score_label.setStyleSheet(f"color: {COLORS['neon_cyan']};")
        layout.addWidget(self.score_label)

        # Difficulty
        self.difficulty_label = QLabel("Normal")
        self.difficulty_label.setStyleSheet(f"color: {COLORS['neon_magenta']};")
        layout.addWidget(self.difficulty_label)

        # Active powerups
        self.powerup_label = QLabel("Powerups: None")
        layout.addWidget(self.powerup_label)

        layout.addStretch()

        # Virtual direction buttons
        btn_layout = QVBoxLayout()
        self.btn_up = QPushButton("▲")
        self.btn_up.clicked.connect(lambda: self.direction_requested.emit(Direction.UP))
        btn_layout.addWidget(self.btn_up)

        mid_row = QHBoxLayout()
        self.btn_left = QPushButton("◀")
        self.btn_left.clicked.connect(lambda: self.direction_requested.emit(Direction.LEFT))
        self.btn_down = QPushButton("▼")
        self.btn_down.clicked.connect(lambda: self.direction_requested.emit(Direction.DOWN))
        self.btn_right = QPushButton("▶")
        self.btn_right.clicked.connect(lambda: self.direction_requested.emit(Direction.RIGHT))
        mid_row.addWidget(self.btn_left)
        mid_row.addWidget(self.btn_down)
        mid_row.addWidget(self.btn_right)
        btn_layout.addLayout(mid_row)
        layout.addLayout(btn_layout)

        layout.addStretch()

        # Leaderboard
        self.leaderboard_label = QLabel("Leaderboard")
        self.leaderboard_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(self.leaderboard_label)
        self.leaderboard_content = QLabel("No scores yet")
        self.leaderboard_content.setWordWrap(True)
        layout.addWidget(self.leaderboard_content)

    def update_score(self, score: int) -> None:
        self.score_label.setText(f"Score: {score}")

    def update_difficulty(self, name: str) -> None:
        self.difficulty_label.setText(name)

    def update_powerups(self, active_powerups: list) -> None:
        if not active_powerups:
            self.powerup_label.setText("Powerups: None")
        else:
            names = [ap.powerup_type.value for ap in active_powerups]
            self.powerup_label.setText("Powerups: " + ", ".join(names))

    def update_leaderboard(self, entries: list) -> None:
        if not entries:
            self.leaderboard_content.setText("No scores yet")
        else:
            lines = []
            for i, entry in enumerate(entries[:10]):
                lines.append(f"{i+1}. {entry.name}: {entry.score}")
            self.leaderboard_content.setText("\n".join(lines))


# ── Main Window ──

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Snake Game — Cyberpunk Edition")
        self.setStyleSheet(f"background: {COLORS['background']};")

        self.difficulty = DifficultyLevel.NORMAL
        self.logic = GameLogic(self.difficulty)
        self.leaderboard = Leaderboard(Path("leaderboard.json"))
        self.sound = SoundManager()

        self._build_ui()
        self._setup_timer()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Canvas
        self.canvas = GameCanvas(self.logic)
        layout.addWidget(self.canvas)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.direction_requested.connect(self.logic.set_direction)
        self.sidebar.update_difficulty(self.difficulty.name)
        self.sidebar.update_leaderboard(self.leaderboard.top_scores())
        layout.addWidget(self.sidebar)

    def _setup_timer(self) -> None:
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._game_tick)
        self.timer.start(self.logic.speed_ms)

    def _game_tick(self) -> None:
        self.logic.tick()
        # Update effective speed from powerups
        effective = self.logic.powerup_system.effective_speed()
        self.timer.setInterval(effective)

        self.canvas.update()
        self.sidebar.update_score(self.logic.score)
        self.sidebar.update_powerups(self.logic.powerup_system.active_powerups)

        if self.logic.game_over:
            self.timer.stop()
            self._handle_game_over()

    def _handle_game_over(self) -> None:
        self.sound.play("self_hit")
        if self.leaderboard.is_high_score(self.logic.score):
            name, ok = QInputDialog.getText(self, "New High Score!",
                                            "Enter your name:", text="Player")
            if ok and name:
                self.leaderboard.add_score(name, self.logic.score, self.difficulty.name)
                self.sidebar.update_leaderboard(self.leaderboard.top_scores())

    # ── Keyboard input ──

    def keyPressEvent(self, event) -> None:  # noqa: N802
        key = event.key()
        key_map = {
            Qt.Key_Up: Direction.UP, Qt.Key_W: Direction.UP,
            Qt.Key_Down: Direction.DOWN, Qt.Key_S: Direction.DOWN,
            Qt.Key_Left: Direction.LEFT, Qt.Key_A: Direction.LEFT,
            Qt.Key_Right: Direction.RIGHT, Qt.Key_D: Direction.RIGHT,
        }
        if key in key_map:
            self.logic.set_direction(key_map[key])
        elif key == Qt.Key_Space:
            self._toggle_pause()
        elif key == Qt.Key_R:
            self._restart()
        elif key == Qt.Key_Escape:
            self._show_menu()

    def _toggle_pause(self) -> None:
        self.logic.paused = not self.logic.paused
        self.sound.play("pause")

    def _restart(self) -> None:
        self.logic = GameLogic(self.difficulty)
        self.canvas.logic = self.logic
        self.sidebar.update_score(0)
        self.sidebar.update_powerups([])
        self.timer.start(self.logic.speed_ms)

    def _show_menu(self) -> None:
        self.logic.paused = True
        msg = QMessageBox(self)
        msg.setWindowTitle("Menu")
        msg.setText("Game Paused")
        msg.setStyleSheet(f"background: {COLORS['background']}; color: {COLORS['ui_text']};")
        resume_btn = msg.addButton("Resume", QMessageBox.AcceptRole)
        restart_btn = msg.addButton("Restart", QMessageBox.ResetRole)
        quit_btn = msg.addButton("Quit", QMessageBox.RejectRole)
        msg.exec_()
        clicked = msg.clickedButton()
        if clicked == resume_btn:
            self.logic.paused = False
        elif clicked == restart_btn:
            self._restart()
        elif clicked == quit_btn:
            self.close()
```

- [ ] **Step 2: Verify the module imports without error**

Run: `uv run python -c "from snake_game.game_ui import MainWindow; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add snake_game/game_ui.py
git commit -m "feat: add game UI with canvas rendering, sidebar, and keyboard controls"
```

---

### Task 10: Entry Point

**Files:**
- Create: `snake_game/main.py`

- [ ] **Step 1: Write the entry point**

```python
# snake_game/main.py
import sys

from PyQt5.QtWidgets import QApplication

from snake_game.game_ui import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the module imports**

Run: `uv run python -c "from snake_game.main import main; print('OK')"`
Expected: `OK` (on a system without display, this may fail with a Qt platform error — that's expected in headless CI)

- [ ] **Step 3: Commit**

```bash
git add snake_game/main.py
git commit -m "feat: add entry point for the snake game"
```

---

### Task 11: Full Integration Test and Manual Verification

**Files:**
- None (verification only)

- [ ] **Step 1: Run all unit tests**

Run: `uv run pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 2: Launch the game for manual testing**

Run: `uv run snake-game`
Expected: Game window opens with cyberpunk-styled snake game. Verify:
- Snake moves with arrow keys and WASD
- Food appears and snake grows when eaten
- Score increases
- Powerups appear on the grid
- Virtual buttons in sidebar work
- Space pauses the game
- R restarts the game
- Game over screen shows on collision
- Leaderboard updates with high scores

- [ ] **Step 3: Final commit if any fixes were needed**

```bash
git add -A
git commit -m "fix: address issues found during integration testing"
```

---

## Self-Review

**1. Spec coverage:**
- 5 difficulty levels: Task 2 (config), Task 3 (game logic), Task 9 (UI)
- 5 powerup types: Task 4 (powerup system), Task 8 (integration)
- Particle effects: Task 5 (particle system), Task 8 (integration)
- UI system with sidebar: Task 9 (game UI)
- Keyboard + virtual controls: Task 9 (game UI)
- Sound + BGM: Task 7 (sound manager)
- Leaderboard: Task 6 (leaderboard), Task 9 (sidebar display)
- All covered.

**2. Placeholder scan:** No TBD, TODO, or vague steps found. All code blocks contain complete implementations.

**3. Type consistency:** `Position` is used consistently as `Position(x, y)`. `PowerupType` enum values match between config and powerup_system. `Direction` enum is consistent across game_logic and game_ui. `ActivePowerup` fields match between powerup_system.py and sidebar display. `leaderboard.top_scores()` returns `List[LeaderboardEntry]` used correctly in game_ui.
