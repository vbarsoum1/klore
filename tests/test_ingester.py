"""Unit tests for klore/ingester.py — ingestion, conversion, and chunking."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from klore.ingester import (
    CHUNK_THRESHOLD,
    IngestionError,
    _split_by_headings,
    chunk_large_document,
    ingest_file,
    ingest_url,
    slugify,
)


# ── slugify ─────────────────────────────────────────────────────────


class TestSlugify:

    def test_basic_text(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_characters(self):
        assert slugify("What's New? (2024)") == "what-s-new-2024"

    def test_unicode_normalization(self):
        assert slugify("café résumé") == "cafe-resume"

    def test_html_entities_stripped(self):
        assert slugify("Hello &amp; World") == "hello-world"

    def test_empty_string_returns_untitled(self):
        assert slugify("") == "untitled"
        assert slugify("!!!") == "untitled"

    def test_multiple_spaces_and_dashes(self):
        assert slugify("one   two---three") == "one-two-three"

    def test_leading_trailing_stripped(self):
        assert slugify("--hello--") == "hello"


# ── ingest_file ─────────────────────────────────────────────────────


class TestIngestFile:

    def test_copies_file_to_raw(self, tmp_path: Path):
        source = tmp_path / "outside" / "paper.pdf"
        source.parent.mkdir()
        source.write_bytes(b"PDF content")
        raw_dir = tmp_path / "project" / "raw"

        result = ingest_file(source, raw_dir)

        assert result.parent == raw_dir
        assert result.name == "paper.pdf"
        assert result.read_bytes() == b"PDF content"

    def test_no_copy_if_already_in_raw(self, tmp_path: Path):
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        existing = raw_dir / "paper.md"
        existing.write_text("content")

        result = ingest_file(existing, raw_dir)
        assert result == existing

    def test_deduplicates_filename(self, tmp_path: Path):
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        # Pre-existing file with same name
        (raw_dir / "paper.pdf").write_bytes(b"old")

        source = tmp_path / "other" / "paper.pdf"
        source.parent.mkdir()
        source.write_bytes(b"new")

        result = ingest_file(source, raw_dir)
        assert result.name == "paper-1.pdf"
        assert result.read_bytes() == b"new"

    def test_creates_raw_dir_if_missing(self, tmp_path: Path):
        source = tmp_path / "paper.md"
        source.write_text("content")
        raw_dir = tmp_path / "project" / "raw"

        result = ingest_file(source, raw_dir)
        assert raw_dir.is_dir()
        assert result.is_file()

    def test_file_in_subdirectory_of_raw_is_noop(self, tmp_path: Path):
        raw_dir = tmp_path / "raw"
        sub = raw_dir / "subdir"
        sub.mkdir(parents=True)
        existing = sub / "paper.md"
        existing.write_text("content")

        result = ingest_file(existing, raw_dir)
        assert result == existing


# ── ingest_url ──────────────────────────────────────────────────────


class TestIngestUrl:

    def test_saves_url_as_markdown(self, tmp_path: Path):
        raw_dir = tmp_path / "raw"
        mock_result = MagicMock()
        mock_result.title = "Test Article"
        mock_result.text_content = "# Article\n\nContent here."

        with patch("klore.ingester.MarkItDown") as MockMD:
            MockMD.return_value.convert.return_value = mock_result
            result = ingest_url("https://example.com/article", raw_dir)

        assert result.name == "test-article.md"
        assert result.read_text("utf-8") == "# Article\n\nContent here."

    def test_uses_url_as_fallback_title(self, tmp_path: Path):
        raw_dir = tmp_path / "raw"
        mock_result = MagicMock()
        mock_result.title = None
        mock_result.text_content = "Some content"

        with patch("klore.ingester.MarkItDown") as MockMD:
            MockMD.return_value.convert.return_value = mock_result
            result = ingest_url("https://example.com/page", raw_dir)

        assert "example" in result.name

    def test_raises_on_fetch_failure(self, tmp_path: Path):
        raw_dir = tmp_path / "raw"

        with patch("klore.ingester.MarkItDown") as MockMD:
            MockMD.return_value.convert.side_effect = Exception("Network error")
            with pytest.raises(IngestionError, match="Failed to fetch URL"):
                ingest_url("https://bad.example.com", raw_dir)


# ── _split_by_headings ─────────────────────────────────────────────


class TestSplitByHeadings:

    def test_splits_on_h1_and_h2(self):
        text = "# Chapter 1\n\nContent 1.\n\n## Section 1.1\n\nContent 1.1.\n\n# Chapter 2\n\nContent 2."
        chunks = _split_by_headings(text)
        assert len(chunks) == 3
        assert chunks[0][0] == "Chapter 1"
        assert chunks[1][0] == "Section 1.1"
        assert chunks[2][0] == "Chapter 2"

    def test_no_headings_returns_full_document(self):
        text = "Just a plain paragraph with no headings at all."
        chunks = _split_by_headings(text)
        assert len(chunks) == 1
        assert chunks[0][0] == "Full Document"
        assert chunks[0][1] == text

    def test_preamble_before_first_heading(self):
        text = "Some intro text.\n\n# First Heading\n\nContent."
        chunks = _split_by_headings(text)
        assert chunks[0][0] == "Preamble"
        assert "intro text" in chunks[0][1]
        assert chunks[1][0] == "First Heading"

    def test_empty_string(self):
        chunks = _split_by_headings("")
        assert len(chunks) == 1
        assert chunks[0][0] == "Full Document"


# ── chunk_large_document ────────────────────────────────────────────


class TestChunkLargeDocument:

    def test_small_document_returns_none(self):
        content = "Small document. " * 100  # well under 50k words
        result = chunk_large_document(content, "small-doc")
        assert result is None

    def test_large_document_with_headings_is_chunked(self):
        # Build a document > CHUNK_THRESHOLD words with headings
        sections = []
        for i in range(6):
            section_text = f"word " * 10_000
            sections.append(f"# Chapter {i+1}\n\n{section_text}")
        content = "\n\n".join(sections)
        assert len(content.split()) > CHUNK_THRESHOLD

        result = chunk_large_document(content, "big-doc")
        assert result is not None
        assert len(result) >= 2
        # Each chunk should have a heading and content
        for heading, text in result:
            assert len(heading) > 0
            assert len(text) > 0

    def test_large_document_without_headings_splits_by_size(self):
        content = "word " * 60_000  # > CHUNK_THRESHOLD, no headings
        result = chunk_large_document(content, "flat-doc")
        assert result is not None
        assert len(result) >= 2
        assert result[0][0] == "Part 1"

    def test_small_chunks_merged(self):
        # Create a large doc where some sections are tiny
        sections = [
            f"# Big Section\n\n" + "word " * 25_000,
            f"# Tiny\n\nJust a few words.",
            f"# Another Big\n\n" + "word " * 25_000,
            f"# Also Tiny\n\nMore words.",
        ]
        content = "\n\n".join(sections)
        assert len(content.split()) > CHUNK_THRESHOLD

        result = chunk_large_document(content, "mixed-doc")
        assert result is not None
        # Tiny sections should be merged into previous ones
        assert len(result) < 4
