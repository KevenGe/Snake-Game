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
