from __future__ import annotations


def verify_claims(slides: list[dict], sources: list[dict]) -> dict:
    evidence_ok = bool(sources)
    issues: list[str] = []

    if not evidence_ok:
        issues.append("No sources found for claims")

    conflicts = []
    seen = set()
    for slide in slides:
        title = slide.get("title", "")
        if title in seen:
            conflicts.append(f"Duplicate slide title detected: {title}")
        seen.add(title)

    if conflicts:
        issues.extend(conflicts)

    return {
        "evidence_ok": evidence_ok,
        "conflicts": conflicts,
        "issues": issues,
    }
