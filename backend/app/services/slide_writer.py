"""
slide_writer.py – Converts SlideSpec objects to slide dicts for the renderer.

Preserves full bullet text (no 120-char truncation that caused content loss).
"""

from __future__ import annotations

from app.models.domain import SlideSpec


def write_slides(slides: list[SlideSpec]) -> list[dict]:
    output: list[dict] = []
    for slide in slides:
        # Keep up to 7 bullets; DO NOT truncate text so content is preserved
        clean_bullets = [b.strip() for b in slide.bullets if b.strip()][:7]
        output.append(
            {
                "title": slide.title,
                "objective": slide.objective,
                "bullets": clean_bullets,
                "references": slide.references,
            }
        )
    return output
