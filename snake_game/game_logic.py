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

        self.powerups_on_board: List[tuple[Position, str]] = []
        self.food: Position = self._random_free_position()

    # -- Public API --

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
            # Don't remove tail -- snake grows
        else:
            self._snake.pop()

    # -- Helpers --

    def _random_free_position(self) -> Position:
        """Return a random position not occupied by the snake or existing powerups."""
        occupied = set(self._snake)
        for pos, _ in self.powerups_on_board:
            occupied.add(pos)
        if hasattr(self, "food"):
            occupied.add(self.food)

        free = [
            Position(x, y)
            for x in range(GRID_COLS)
            for y in range(GRID_ROWS)
            if Position(x, y) not in occupied
        ]
        if not free:
            return Position(0, 0)  # Edge case: board full
        return random.choice(free)
