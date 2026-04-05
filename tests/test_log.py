"""Unit tests for klore/log.py — append-only log operations."""

from __future__ import annotations

from pathlib import Path

from klore.log import append_log, read_recent_log


class TestAppendLog:

    def test_creates_log_if_missing(self, tmp_path: Path):
        append_log(tmp_path, "ingest", "Added paper.pdf", "1 source added")
        log = (tmp_path / "log.md").read_text("utf-8")
        assert log.startswith("# Log")
        assert "ingest" in log
        assert "Added paper.pdf" in log

    def test_appends_to_existing_log(self, tmp_path: Path):
        (tmp_path / "log.md").write_text("# Log\n", encoding="utf-8")
        append_log(tmp_path, "ingest", "First", "Details 1")
        append_log(tmp_path, "lint", "Second", "Details 2")
        log = (tmp_path / "log.md").read_text("utf-8")
        assert "First" in log
        assert "Second" in log
        # Both entries present
        assert log.count("## [") == 2

    def test_includes_editorial_notes(self, tmp_path: Path):
        append_log(
            tmp_path, "ingest", "Paper", "Details",
            editorial_notes="High significance source"
        )
        log = (tmp_path / "log.md").read_text("utf-8")
        assert "Editorial: High significance source" in log

    def test_timestamp_format(self, tmp_path: Path):
        append_log(tmp_path, "lint", "Check", "Details")
        log = (tmp_path / "log.md").read_text("utf-8")
        # ISO-8601 timestamp pattern
        import re
        assert re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", log)


class TestReadRecentLog:

    def test_no_log_returns_placeholder(self, tmp_path: Path):
        result = read_recent_log(tmp_path)
        assert result == "(no log yet)"

    def test_empty_log_returns_placeholder(self, tmp_path: Path):
        (tmp_path / "log.md").write_text("# Log\n", encoding="utf-8")
        result = read_recent_log(tmp_path)
        assert result == "(no entries yet)"

    def test_returns_recent_entries(self, tmp_path: Path):
        for i in range(5):
            append_log(tmp_path, "ingest", f"Entry {i}", f"Details {i}")
        result = read_recent_log(tmp_path, n=3)
        assert "Entry 4" in result
        assert "Entry 3" in result
        assert "Entry 2" in result

    def test_n_limits_entries(self, tmp_path: Path):
        for i in range(10):
            append_log(tmp_path, "ingest", f"Entry {i}", f"Details {i}")
        result = read_recent_log(tmp_path, n=2)
        # Should have only last 2
        assert "Entry 9" in result
        assert "Entry 8" in result
        assert "Entry 0" not in result
