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
