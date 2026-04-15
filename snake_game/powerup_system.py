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
