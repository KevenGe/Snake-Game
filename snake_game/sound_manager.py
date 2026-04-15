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
        """Set volume 0.0-1.0."""
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
