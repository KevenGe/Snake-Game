from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from snake_game.config import LEADERBOARD_SIZE


@dataclass
class LeaderboardEntry:
    name: str
    score: int
    difficulty: str


class Leaderboard:
    def __init__(self, filepath: Path) -> None:
        self._filepath = filepath
        self._entries: List[LeaderboardEntry] = []
        self._load()

    def add_score(self, name: str, score: int, difficulty: str) -> None:
        self._entries.append(LeaderboardEntry(name=name, score=score, difficulty=difficulty))
        self._entries.sort(key=lambda e: e.score, reverse=True)
        self._entries = self._entries[:LEADERBOARD_SIZE]
        self._save()

    def top_scores(self) -> List[LeaderboardEntry]:
        return list(self._entries)

    def is_high_score(self, score: int) -> bool:
        if len(self._entries) < LEADERBOARD_SIZE:
            return True
        return score > self._entries[-1].score

    def _load(self) -> None:
        if not self._filepath.exists():
            self._entries = []
            return
        try:
            data = json.loads(self._filepath.read_text(encoding="utf-8"))
            self._entries = [LeaderboardEntry(**e) for e in data]
        except (json.JSONDecodeError, TypeError, KeyError):
            self._entries = []

    def _save(self) -> None:
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(e) for e in self._entries]
        self._filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")
