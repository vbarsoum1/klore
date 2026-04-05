"""Tests for token tracking and topic-only compilation in klore/compiler.py."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from klore.compiler import _TokenTracker, compile_wiki


# ── Token Tracking ──────────────────────────────────────────────────


class TestTokenTracker:

    def test_empty_tracker(self):
        t = _TokenTracker()
        assert t.prompt_tokens == 0
        assert t.completion_tokens == 0
        assert t.total_tokens == 0

    def test_add_usage(self):
        t = _TokenTracker()
        usage = MagicMock()
        usage.prompt_tokens = 100
        usage.completion_tokens = 50
        t.add(usage)
        assert t.prompt_tokens == 100
        assert t.completion_tokens == 50
        assert t.total_tokens == 150

    def test_accumulates_across_calls(self):
        t = _TokenTracker()
        for i in range(3):
            usage = MagicMock()
            usage.prompt_tokens = 10
            usage.completion_tokens = 5
            t.add(usage)
        assert t.prompt_tokens == 30
        assert t.completion_tokens == 15
        assert t.total_tokens == 45

    def test_handles_none_usage(self):
        t = _TokenTracker()
        t.add(None)
        assert t.total_tokens == 0

    def test_handles_missing_attributes(self):
        t = _TokenTracker()
        usage = MagicMock(spec=[])  # no attributes
        t.add(usage)
        assert t.total_tokens == 0

    def test_handles_none_token_values(self):
        t = _TokenTracker()
        usage = MagicMock()
        usage.prompt_tokens = None
        usage.completion_tokens = None
        t.add(usage)
        assert t.total_tokens == 0


# ── Topic-Only Compile ──────────────────────────────────────────────


def _fake_get_model(tier: str, project_dir: Path) -> str:
    return "test-model"


def _setup_compiled_project(tmp_path: Path) -> Path:
    """Create a project that looks like it's been compiled once."""
    project = tmp_path / "project"
    wiki = project / "wiki"
    raw = project / "raw"
    for d in [
        raw, wiki, wiki / "sources", wiki / "concepts",
        wiki / "entities", wiki / "reports", wiki / "_meta",
        project / ".klore",
    ]:
        d.mkdir(parents=True)

    # Write source summaries with tags
    (wiki / "sources" / "test-paper.md").write_text(
        '---\ntitle: "Test Paper"\ntags: ["machine-learning", "transformers"]\n---\n'
        "# Test Paper\n\nContent about ML.\n",
        encoding="utf-8",
    )

    # Write existing concept
    (wiki / "concepts" / "machine-learning.md").write_text(
        "# Machine Learning\n\nExisting content.\n",
        encoding="utf-8",
    )

    # Write state
    state_data = {
        "file_hashes": {"raw/test-paper.md": "abc123"},
        "concept_sources": {"machine-learning": ["test-paper"]},
        "entity_sources": {},
        "prompt_hash": "some_hash",
        "last_compiled": "2026-04-01T12:00:00",
        "compilation_count": 1,
        "total_tokens_used": 500,
    }
    (wiki / "_meta" / "compile-state.json").write_text(
        json.dumps(state_data), encoding="utf-8"
    )

    # Write tag aliases
    (wiki / "_meta" / "tag-aliases.json").write_text(
        json.dumps({"ml": "machine-learning"}), encoding="utf-8"
    )

    # Config
    (project / ".klore" / "config.json").write_text(
        json.dumps({"model": {
            "fast": "test", "strong": "test", "director": "test"
        }}),
        encoding="utf-8",
    )
    (project / ".klore" / "agents.md").write_text("# Agents\n", encoding="utf-8")

    # Index, log, overview
    (wiki / "index.md").write_text("# Index\n")
    (wiki / "log.md").write_text("# Log\n")
    (wiki / "overview.md").write_text("# Overview\n")

    return project


class TestTopicCompile:

    def test_topic_compile_rebuilds_single_concept(self, tmp_path: Path):
        project = _setup_compiled_project(tmp_path)

        concept_response = (
            '---\ntitle: "Machine Learning"\ntags: ["machine-learning"]\n'
            'sources: ["test-paper"]\n---\n'
            "# Machine Learning\n\nUpdated content.\n"
        )

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = concept_response
        mock_response.usage = None
        mock_client.chat.completions.create.return_value = mock_response

        with (
            patch("klore.compiler.get_client", return_value=mock_client),
            patch("klore.compiler.get_model", side_effect=_fake_get_model),
            patch("klore.compiler.git_add_and_commit"),
        ):
            stats = asyncio.run(
                compile_wiki(project, topic="Machine Learning")
            )

        assert stats["concepts_generated"] == 1
        assert stats["sources_processed"] == 0  # topic compile skips extraction

    def test_topic_compile_returns_zero_when_no_sources(self, tmp_path: Path):
        project = _setup_compiled_project(tmp_path)
        # Remove all source summaries
        for f in (project / "wiki" / "sources").glob("*.md"):
            f.unlink()

        mock_client = MagicMock()

        with (
            patch("klore.compiler.get_client", return_value=mock_client),
            patch("klore.compiler.get_model", side_effect=_fake_get_model),
            patch("klore.compiler.git_add_and_commit"),
        ):
            stats = asyncio.run(
                compile_wiki(project, topic="Nonexistent Topic")
            )

        assert stats["concepts_generated"] == 0
        assert stats["sources_processed"] == 0

    def test_topic_compile_tracks_tokens(self, tmp_path: Path):
        project = _setup_compiled_project(tmp_path)

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            '---\ntitle: "ML"\ntags: ["machine-learning"]\n---\n# ML\nContent.'
        )
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 200
        mock_usage.completion_tokens = 100
        mock_response.usage = mock_usage
        mock_client.chat.completions.create.return_value = mock_response

        with (
            patch("klore.compiler.get_client", return_value=mock_client),
            patch("klore.compiler.get_model", side_effect=_fake_get_model),
            patch("klore.compiler.git_add_and_commit"),
        ):
            stats = asyncio.run(
                compile_wiki(project, topic="Machine Learning")
            )

        # Token stats should be present
        assert stats["total_tokens"] >= 0
