"""Support helpers for wiki compilation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from klore.compile_types import EditorialBrief, Extraction, PageRecommendation
from klore.ingester import slugify
from klore.state import CompileState

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def parse_frontmatter(markdown: str) -> dict[str, Any]:
    """Extract YAML frontmatter from a markdown string."""
    parts = markdown.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def source_summary_slug(extraction: Extraction) -> str:
    """Return the wiki/sources slug for an extraction."""
    filename = extraction["filename"]
    slug = slugify(extraction.get("parent_filename", filename).rsplit(".", 1)[0])
    if "chunk_index" in extraction:
        slug = f"{slug}-ch{extraction['chunk_index']:02d}"
    return slug


def source_slugs_for_raw_rel_path(raw_rel_path: Path | str) -> list[str]:
    """Return possible source-summary slugs for a raw source path."""
    return [slugify(Path(raw_rel_path).stem)]


def report_tags(report_file: Path) -> list[str]:
    """Read concept tags from a saved report's frontmatter."""
    fm = parse_frontmatter(report_file.read_text("utf-8"))
    if not isinstance(fm, dict):
        return []
    return [str(tag).strip() for tag in fm.get("tags", []) or []]


def collect_related_reports(wiki_dir: Path, concept_slug: str) -> list[Path]:
    """Find saved reports that should contribute to a concept page."""
    reports_dir = wiki_dir / "reports"
    if not reports_dir.is_dir():
        return []

    related: list[Path] = []
    for report_file in sorted(reports_dir.glob("*.md")):
        content = report_file.read_text("utf-8")
        tags = report_tags(report_file)
        links = {slug.strip() for slug in WIKILINK_RE.findall(content)}
        if concept_slug in tags or concept_slug in links:
            related.append(report_file)
    return related


def page_recommendations(
    brief: EditorialBrief,
    page_type: str | None = None,
) -> list[PageRecommendation]:
    """Return normalized page recommendations from new and legacy brief schemas."""
    pages: list[PageRecommendation] = []
    for page_info in brief.get("pages", []) or []:
        if page_type is None or page_info.get("page_type") == page_type:
            pages.append(page_info)

    legacy_key = None
    if page_type == "entity":
        legacy_key = "entities"
    elif page_type == "concept":
        legacy_key = "concepts"

    if legacy_key:
        pages.extend(brief.get(legacy_key, []) or [])

    return pages


def remove_raw_source_outputs(
    wiki_dir: Path,
    state: CompileState,
    removed_sources: list[Path],
) -> int:
    """Remove generated summaries and state mappings for deleted raw sources."""
    removed_count = 0
    sources_dir = wiki_dir / "sources"

    for rel_path in removed_sources:
        for source_slug in source_slugs_for_raw_rel_path(rel_path):
            candidates = []
            if sources_dir.is_dir():
                candidates.extend(sources_dir.glob(f"{source_slug}.md"))
                candidates.extend(sources_dir.glob(f"{source_slug}-ch*.md"))

            for candidate in candidates:
                if candidate.is_file():
                    candidate.unlink()
                    removed_count += 1

            for mapping in (state.concept_sources, state.entity_sources):
                empty_keys: list[str] = []
                for page_slug, source_slugs in mapping.items():
                    kept = [
                        s for s in source_slugs
                        if s != source_slug and not s.startswith(f"{source_slug}-ch")
                    ]
                    if kept:
                        mapping[page_slug] = kept
                    else:
                        empty_keys.append(page_slug)
                for page_slug in empty_keys:
                    del mapping[page_slug]

        state.file_hashes.pop(str(rel_path), None)

    return removed_count
