import json
import pytest
from pathlib import Path
from snake_game.leaderboard import Leaderboard, LeaderboardEntry


class TestLeaderboardEntry:
    def test_create_entry(self):
        entry = LeaderboardEntry(name="Player1", score=100, difficulty="Normal")
        assert entry.name == "Player1"
        assert entry.score == 100


class TestLeaderboard:
    def test_empty_leaderboard(self, tmp_path):
        lb = Leaderboard(filepath=tmp_path / "lb.json")
        assert lb.top_scores() == []

    def test_add_score(self, tmp_path):
        lb = Leaderboard(filepath=tmp_path / "lb.json")
        lb.add_score("Alice", 200, "Normal")
        scores = lb.top_scores()
        assert len(scores) == 1
        assert scores[0].name == "Alice"
        assert scores[0].score == 200

    def test_top_10_only(self, tmp_path):
        lb = Leaderboard(filepath=tmp_path / "lb.json")
        for i in range(15):
            lb.add_score(f"P{i}", (i + 1) * 10, "Normal")
        assert len(lb.top_scores()) == 10

    def test_sorted_descending(self, tmp_path):
        lb = Leaderboard(filepath=tmp_path / "lb.json")
        lb.add_score("Low", 50, "Normal")
        lb.add_score("High", 300, "Normal")
        lb.add_score("Mid", 150, "Normal")
        scores = lb.top_scores()
        assert scores[0].score == 300
        assert scores[1].score == 150
        assert scores[2].score == 50

    def test_persistence(self, tmp_path):
        path = tmp_path / "lb.json"
        lb1 = Leaderboard(filepath=path)
        lb1.add_score("Alice", 200, "Normal")
        # Load again
        lb2 = Leaderboard(filepath=path)
        assert len(lb2.top_scores()) == 1
        assert lb2.top_scores()[0].name == "Alice"

    def test_corrupted_file_recovery(self, tmp_path):
        path = tmp_path / "lb.json"
        path.write_text("NOT VALID JSON{{{")
        lb = Leaderboard(filepath=path)
        assert lb.top_scores() == []

    def test_is_high_score(self, tmp_path):
        lb = Leaderboard(filepath=tmp_path / "lb.json")
        for i in range(10):
            lb.add_score(f"P{i}", (i + 1) * 10, "Normal")
        # Score of 5 should not be top 10 (minimum is 10)
        assert not lb.is_high_score(5)
        # Score of 200 should be top 10
        assert lb.is_high_score(200)
