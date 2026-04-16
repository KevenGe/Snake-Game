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
        return max(0.0, min(1.0, self.life))

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

    # -- Spawn patterns --

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
