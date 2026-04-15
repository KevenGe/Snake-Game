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

        self.powerups_on_board: List[tuple[Position, PowerupType]] = []
        self.food: Position = self._random_free_position()

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
