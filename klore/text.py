"""Shared text helpers for prompts and model responses."""

from __future__ import annotations


def fill_prompt(template: str, **kwargs: object) -> str:
    """Replace {key} placeholders without str.format() brace conflicts."""
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def strip_code_fences(text: str) -> str:
    """Strip a wrapping markdown code fence from model output."""
    stripped = text.strip()
    if stripped.startswith("```"):
        first_nl = stripped.index("\n") if "\n" in stripped else len(stripped)
        stripped = stripped[first_nl + 1:]
    if stripped.endswith("```"):
        stripped = stripped[:-3]
    return stripped.strip()
