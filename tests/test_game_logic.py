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


class TestRestart:
    def test_restart_creates_fresh_state(self):
        """Verify that creating a new GameLogic resets all state."""
        logic = GameLogic(DifficultyLevel.NORMAL)
        # Play until game over
        for _ in range(GRID_COLS + 5):
            if logic.game_over:
                break
            logic.tick()
        assert logic.game_over

        # "Restart" by creating a new instance
        logic = GameLogic(DifficultyLevel.NORMAL)
        assert not logic.game_over
        assert logic.score == 0
        assert len(logic.snake) == 3
        assert logic.direction == Direction.RIGHT
        assert len(logic.powerup_system.active_powerups) == 0
        assert len(logic.particle_system.particles) == 0

    def test_restart_snake_moves_after_death(self):
        """Verify snake can move normally after restart."""
        logic = GameLogic(DifficultyLevel.NORMAL)
        # Die by hitting wall
        for _ in range(GRID_COLS + 5):
            if logic.game_over:
                break
            logic.tick()
        assert logic.game_over

        # Restart
        logic = GameLogic(DifficultyLevel.NORMAL)
        # Verify snake can move
        old_head = logic.snake[0]
        logic.tick()
        new_head = logic.snake[0]
        assert new_head == Position(old_head.x + 1, old_head.y)

    def test_tick_after_game_over_is_noop(self):
        """Ticks after game_over should be ignored."""
        logic = GameLogic(DifficultyLevel.NORMAL)
        for _ in range(GRID_COLS + 5):
            if logic.game_over:
                break
            logic.tick()
        assert logic.game_over
        score_before = logic.score
        snake_len_before = len(logic.snake)
        # Tick again — should be a no-op
        logic.tick()
        assert logic.score == score_before
        assert len(logic.snake) == snake_len_before
