"""Unit tests for klore/linter.py — programmatic scan (no LLM calls)."""

from __future__ import annotations

from pathlib import Path

from klore.linter import (
    _all_wiki_md_files,
    _format_report,
    _format_scan_results,
    _programmatic_scan,
    _select_spot_check_pages,
    _slug_resolves,
)


def _setup_wiki(tmp_path: Path) -> Path:
    """Create a minimal wiki structure for testing."""
    wiki = tmp_path / "wiki"
    for d in ("sources", "concepts", "entities", "reports", "_meta"):
        (wiki / d).mkdir(parents=True)
    (wiki / "index.md").write_text("# Index\n")
    (wiki / "log.md").write_text("# Log\n")
    (wiki / "overview.md").write_text("# Overview\n")
    return wiki


class TestSlugResolves:

    def test_resolves_concept(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        (wiki / "concepts" / "machine-learning.md").write_text("# ML")
        assert _slug_resolves(wiki, "machine-learning") is True

    def test_resolves_entity(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        (wiki / "entities" / "einstein.md").write_text("# Einstein")
        assert _slug_resolves(wiki, "einstein") is True

    def test_resolves_source(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        (wiki / "sources" / "paper-one.md").write_text("# Paper One")
        assert _slug_resolves(wiki, "paper-one") is True

    def test_nonexistent_slug(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        assert _slug_resolves(wiki, "does-not-exist") is False


class TestAllWikiMdFiles:

    def test_collects_all_md_files(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        (wiki / "sources" / "s1.md").write_text("source")
        (wiki / "concepts" / "c1.md").write_text("concept")
        (wiki / "entities" / "e1.md").write_text("entity")

        files = _all_wiki_md_files(wiki)
        names = {f.name for f in files}
        assert "s1.md" in names
        assert "c1.md" in names
        assert "e1.md" in names
        assert "index.md" in names
        assert "log.md" in names

    def test_no_duplicates(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        files = _all_wiki_md_files(wiki)
        assert len(files) == len(set(files))


class TestProgrammaticScan:

    def test_detects_broken_wikilinks(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        (wiki / "concepts" / "ml.md").write_text(
            "# ML\n\nSee [[nonexistent-page]] for details."
        )
        scan = _programmatic_scan(wiki, tmp_path)
        broken = scan["broken_links"]
        assert len(broken) == 1
        assert broken[0]["slug"] == "nonexistent-page"

    def test_valid_wikilinks_not_broken(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        (wiki / "concepts" / "ml.md").write_text("# ML\n\nSee [[transformers]].")
        (wiki / "concepts" / "transformers.md").write_text("# Transformers")
        scan = _programmatic_scan(wiki, tmp_path)
        assert len(scan["broken_links"]) == 0

    def test_detects_orphan_pages(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        # This page exists but nothing links to it
        (wiki / "concepts" / "orphan.md").write_text("# Orphan Topic")
        scan = _programmatic_scan(wiki, tmp_path)
        assert "concepts/orphan.md" in scan["orphan_pages"]

    def test_index_pages_not_orphans(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        scan = _programmatic_scan(wiki, tmp_path)
        orphans = scan["orphan_pages"]
        assert "index.md" not in orphans
        assert "log.md" not in orphans
        assert "overview.md" not in orphans

    def test_detects_outbound_less_pages(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        (wiki / "concepts" / "empty.md").write_text("# Empty\n\nNo links here.")
        scan = _programmatic_scan(wiki, tmp_path)
        assert "concepts/empty.md" in scan["outbound_less"]

    def test_detects_stale_sources(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        raw = tmp_path / "raw"
        raw.mkdir()
        (raw / "paper.md").write_text("new content")
        # State has old hash
        from klore.state import CompileState
        state = CompileState()
        state.file_hashes = {"raw/paper.md": "old_hash"}
        state.save(wiki)

        scan = _programmatic_scan(wiki, tmp_path)
        stale = scan["stale_sources"]
        assert len(stale) == 1
        assert stale[0]["reason"] == "raw file changed since last compile"

    def test_detects_uncompiled_sources(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        raw = tmp_path / "raw"
        raw.mkdir()
        (raw / "new.md").write_text("brand new")

        scan = _programmatic_scan(wiki, tmp_path)
        stale = scan["stale_sources"]
        assert any(s["reason"] == "raw file not yet compiled" for s in stale)

    def test_counts_tags(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        (wiki / "sources" / "s1.md").write_text(
            '---\ntitle: "S1"\ntags: ["ml", "ai"]\n---\n# S1'
        )
        (wiki / "sources" / "s2.md").write_text(
            '---\ntitle: "S2"\ntags: ["ml"]\n---\n# S2'
        )
        scan = _programmatic_scan(wiki, tmp_path)
        assert scan["tag_counts"]["ml"] == 2
        assert scan["tag_counts"]["ai"] == 1
        assert "ai" in scan["rare_tags"]
        assert "ml" not in scan["rare_tags"]


class TestSelectSpotCheckPages:

    def test_selects_concept_and_entity_pages(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        (wiki / "concepts" / "ml.md").write_text("# ML")
        (wiki / "entities" / "einstein.md").write_text("# Einstein")
        pages = _select_spot_check_pages(wiki)
        names = {p.name for p in pages}
        assert "ml.md" in names
        assert "einstein.md" in names

    def test_respects_max_pages(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        for i in range(10):
            (wiki / "concepts" / f"concept-{i}.md").write_text(f"# C{i}")
        pages = _select_spot_check_pages(wiki, max_pages=3)
        assert len(pages) == 3

    def test_skips_index_files(self, tmp_path: Path):
        wiki = _setup_wiki(tmp_path)
        (wiki / "concepts" / "INDEX.md").write_text("# Index")
        (wiki / "concepts" / "real.md").write_text("# Real")
        pages = _select_spot_check_pages(wiki)
        names = {p.name for p in pages}
        assert "INDEX.md" not in names


class TestFormatScanResults:

    def test_formats_clean_scan(self, tmp_path: Path):
        scan = {
            "page_count": 5,
            "broken_links": [],
            "orphan_pages": [],
            "outbound_less": [],
            "stale_sources": [],
            "rare_tags": [],
            "tag_counts": {},
        }
        text = _format_scan_results(scan)
        assert "Pages scanned: 5" in text
        assert "(none)" in text

    def test_formats_issues(self):
        scan = {
            "page_count": 10,
            "broken_links": [{"slug": "broken", "file": "concepts/ml.md"}],
            "orphan_pages": ["entities/orphan.md"],
            "outbound_less": ["sources/s1.md"],
            "stale_sources": [{"source": "raw/old.md", "reason": "changed"}],
            "rare_tags": ["obscure-tag"],
            "tag_counts": {"obscure-tag": 1},
        }
        text = _format_scan_results(scan)
        assert "[[broken]]" in text
        assert "entities/orphan.md" in text
        assert "raw/old.md" in text
        assert "obscure-tag" in text


class TestFormatReport:

    def test_report_with_clean_scan_and_director(self):
        scan = {
            "page_count": 5,
            "broken_links": [],
            "orphan_pages": [],
            "outbound_less": [],
            "stale_sources": [],
            "rare_tags": [],
            "tag_counts": {},
        }
        director = {
            "contradictions": [],
            "stale_claims": [],
            "missing_pages": [],
            "missing_crossrefs": [],
            "thin_pages": [],
            "knowledge_gaps": [],
            "schema_improvements": [],
            "suggested_questions": [],
        }
        report = _format_report(scan, director)
        assert "# Lint Report" in report
        assert "Structural issues: 0" in report
        assert "Editorial issues: 0" in report
        assert "Total: 0" in report

    def test_report_with_parse_error(self):
        scan = {
            "page_count": 3,
            "broken_links": [],
            "orphan_pages": [],
            "outbound_less": [],
            "stale_sources": [],
            "rare_tags": [],
            "tag_counts": {},
        }
        director = {"_parse_error": True, "_raw_output": "bad json"}
        report = _format_report(scan, director)
        assert "could not be parsed" in report
        assert "bad json" in report

    def test_report_counts_issues(self):
        scan = {
            "page_count": 10,
            "broken_links": [{"slug": "a", "file": "b"}],
            "orphan_pages": ["c"],
            "outbound_less": [],
            "stale_sources": [],
            "rare_tags": ["tag1"],
            "tag_counts": {"tag1": 1},
        }
        director = {
            "contradictions": [
                {"page_a": "x", "claim_a": "y", "page_b": "z", "claim_b": "w"}
            ],
            "stale_claims": [],
            "missing_pages": [],
            "missing_crossrefs": [],
            "thin_pages": [],
            "knowledge_gaps": [],
            "schema_improvements": [],
            "suggested_questions": [],
        }
        report = _format_report(scan, director)
        assert "Structural issues: 3" in report  # 1 broken + 1 orphan + 1 rare tag
        assert "Editorial issues: 1" in report
        assert "Total: 4" in report
