"""Shared type shapes for the compile pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict


class Extraction(TypedDict, total=False):
    """Markdown extraction produced from a raw source or source chunk."""

    filename: str
    content: str
    rel_path: str
    file_path: Path
    chunk_index: int
    chunk_total: int
    chunk_heading: str
    parent_filename: str


class PageRecommendation(TypedDict, total=False):
    """Director recommendation for a concept or entity page."""

    name: str
    slug: str
    page_type: str
    entity_type: str
    action: str
    significance: str
    justification: str
    reason: str
    substance: str


class EditorialBrief(TypedDict, total=False):
    """Director brief consumed by later compile steps."""

    summary: str
    key_takeaways: list[str]
    novelty: str
    contradictions: list[dict[str, Any]]
    emphasis: str
    pages: list[PageRecommendation]
    entities: list[PageRecommendation]
    concepts: list[PageRecommendation]
    existing_pages_to_update: list[dict[str, str]]
    questions_raised: list[str]
    suggested_sources: list[str]
    _filename: str
    _rel_path: str
