# snake_game/game_ui.py
from __future__ import annotations

from typing import Optional
import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QMessageBox, QInputDialog,
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

# Cross-platform font families (first available is used)
_UI_FONT = "Segoe UI, Helvetica, Arial, sans-serif"
_SYMBOL_FONT = "Segoe UI Symbol, Apple Symbols, Noto Sans Symbols, sans-serif"


def _data_dir() -> Path:
    """Return the platform-standard app data directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"
    d = base / "snake-game"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── Game Canvas ──

class GameCanvas(QWidget):
    """Custom widget that renders the game grid, snake, food, powerups, and particles."""

    def __init__(self, logic: GameLogic, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.logic = logic
        self.setFixedSize(GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE)
        self.setFocusPolicy(Qt.StrongFocus)

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
            PowerupType.OVERCLOCK: "\u25c8",
            PowerupType.FIREWALL: "\u2b21",
            PowerupType.DATA_PACKET: "\u2726",
            PowerupType.TIME_DILATION: "\u29c9",
            PowerupType.ENERGY_CELL: "\u26a1",
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
            p.setFont(QFont(_SYMBOL_FONT, int(CELL_SIZE * 0.6)))
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
        p.setFont(QFont(_UI_FONT, 36, QFont.Bold))
        p.drawText(self.rect(), Qt.AlignCenter, "GAME OVER")
        # Draw restart hint below
        hint_rect = QRectF(self.rect())
        hint_rect.setTop(hint_rect.center().y() + 30)
        p.setPen(QPen(QColor(COLORS["neon_cyan"])))
        p.setFont(QFont(_UI_FONT, 14))
        p.drawText(hint_rect, Qt.AlignHCenter | Qt.AlignTop, "Press R to Restart")


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
        self.score_label.setFont(QFont(_UI_FONT, 20, QFont.Bold))
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

        # Virtual direction buttons (NoFocus so keyboard stays on canvas)
        btn_layout = QVBoxLayout()
        self.btn_up = QPushButton("\u25b2")
        self.btn_up.setFocusPolicy(Qt.NoFocus)
        self.btn_up.clicked.connect(lambda: self.direction_requested.emit(Direction.UP))
        btn_layout.addWidget(self.btn_up)

        mid_row = QHBoxLayout()
        self.btn_left = QPushButton("\u25c0")
        self.btn_left.setFocusPolicy(Qt.NoFocus)
        self.btn_left.clicked.connect(lambda: self.direction_requested.emit(Direction.LEFT))
        self.btn_down = QPushButton("\u25bc")
        self.btn_down.setFocusPolicy(Qt.NoFocus)
        self.btn_down.clicked.connect(lambda: self.direction_requested.emit(Direction.DOWN))
        self.btn_right = QPushButton("\u25b6")
        self.btn_right.setFocusPolicy(Qt.NoFocus)
        self.btn_right.clicked.connect(lambda: self.direction_requested.emit(Direction.RIGHT))
        mid_row.addWidget(self.btn_left)
        mid_row.addWidget(self.btn_down)
        mid_row.addWidget(self.btn_right)
        btn_layout.addLayout(mid_row)
        layout.addLayout(btn_layout)

        layout.addStretch()

        # Leaderboard
        self.leaderboard_label = QLabel("Leaderboard")
        self.leaderboard_label.setFont(QFont(_UI_FONT, 12, QFont.Bold))
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


# ── Custom Title Bar ──

class TitleBar(QFrame):
    """Frameless window title bar with cyberpunk neon styling."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(32)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS["background"]};
                border-bottom: 1px solid {COLORS["neon_purple"]};
            }}
            QLabel {{
                color: {COLORS["neon_cyan"]};
            }}
        """)
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 6, 0)
        layout.setSpacing(0)

        # Title
        title = QLabel("Snake Game — Cyberpunk Edition")
        title.setFont(QFont(_UI_FONT, 10))
        layout.addWidget(title)
        layout.addStretch()

        # Minimize button
        self.btn_min = QPushButton("—")
        self.btn_min.setFixedSize(36, 28)
        self.btn_min.setFocusPolicy(Qt.NoFocus)
        self.btn_min.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {COLORS["ui_text"]};
                border: none; font-size: 16px;
            }}
            QPushButton:hover {{
                background: rgba(176, 38, 255, 0.3);
            }}
        """)
        layout.addWidget(self.btn_min)

        # Close button
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(36, 28)
        self.btn_close.setFocusPolicy(Qt.NoFocus)
        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {COLORS["neon_magenta"]};
                border: none; font-size: 14px;
            }}
            QPushButton:hover {{
                background: rgba(255, 0, 255, 0.3);
            }}
        """)
        layout.addWidget(self.btn_close)

    # ── Drag to move ──
    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.window().pos()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag_pos is not None:
            self.window().move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._drag_pos = None


# ── Main Window ──

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Snake Game \u2014 Cyberpunk Edition")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(f"background: {COLORS['background']};")

        self.difficulty = DifficultyLevel.NORMAL
        self.logic = GameLogic(self.difficulty)
        self.leaderboard = Leaderboard(_data_dir() / "leaderboard.json")
        self.sound = SoundManager()

        self._build_ui()
        self._setup_timer()
        self.canvas.setFocus()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom title bar
        self.title_bar = TitleBar(self)
        self.title_bar.btn_min.clicked.connect(self.showMinimized)
        self.title_bar.btn_close.clicked.connect(self.close)
        main_layout.addWidget(self.title_bar)

        # Game area: canvas + sidebar
        game_row = QWidget()
        game_layout = QHBoxLayout(game_row)
        game_layout.setContentsMargins(0, 0, 0, 0)
        game_layout.setSpacing(0)

        # Canvas
        self.canvas = GameCanvas(self.logic)
        game_layout.addWidget(self.canvas)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.direction_requested.connect(self.logic.set_direction)
        self.sidebar.update_difficulty(self.difficulty.name)
        self.sidebar.update_leaderboard(self.leaderboard.top_scores())
        game_layout.addWidget(self.sidebar)

        main_layout.addWidget(game_row)

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

        # Show game over dialog with restart option
        msg = QMessageBox(self)
        msg.setWindowTitle("Game Over")
        msg.setText(f"Score: {self.logic.score}")
        msg.setStyleSheet(f"background: {COLORS['background']}; color: {COLORS['ui_text']};")
        restart_btn = msg.addButton("Restart", QMessageBox.AcceptRole)
        quit_btn = msg.addButton("Quit", QMessageBox.RejectRole)
        msg.exec_()
        clicked = msg.clickedButton()
        if clicked == restart_btn:
            self._restart()
        elif clicked == quit_btn:
            self.close()

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
        self.sidebar.direction_requested.disconnect()
        self.sidebar.direction_requested.connect(self.logic.set_direction)
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
