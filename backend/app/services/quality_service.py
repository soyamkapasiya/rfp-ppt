from app.models.domain import QualityReport


def score_deck(
    slides: list[dict],
    has_sources: bool,
    freshness_flags: int = 0,
    conflict_flags: int = 0,
    compliance_covered: bool = True,
) -> QualityReport:
    clarity = min(100, 60 + len(slides))
    evidence = 85 if has_sources else 45
    feasibility = 80 if len(slides) >= 15 else 55
    readability = 82

    penalties = freshness_flags * 4 + conflict_flags * 6 + (0 if compliance_covered else 15)
    overall = max(0, int((clarity + evidence + feasibility + readability) / 4) - penalties)

    issues: list[str] = []
    if not has_sources:
        issues.append("Missing source coverage for factual claims")
    if len(slides) < 15:
        issues.append("Deck is shorter than required 15-slide blueprint")
    if freshness_flags:
        issues.append(f"Detected {freshness_flags} stale sources")
    if conflict_flags:
        issues.append(f"Detected {conflict_flags} conflicting claims")
    if not compliance_covered:
        issues.append("Security/compliance coverage is incomplete")

    return QualityReport(
        clarity_score=clarity,
        evidence_score=evidence,
        feasibility_score=feasibility,
        executive_readability_score=readability,
        overall_score=overall,
        pass_gate=overall >= 75,
        issues=issues,
    )
