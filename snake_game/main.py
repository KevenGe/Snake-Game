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