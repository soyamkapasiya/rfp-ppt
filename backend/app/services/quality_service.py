from app.models.domain import QualityReport


def score_deck(slides: list[dict], has_sources: bool) -> QualityReport:
    clarity = min(100, 60 + len(slides))
    evidence = 85 if has_sources else 45
    feasibility = 80 if len(slides) >= 15 else 55
    readability = 82
    overall = int((clarity + evidence + feasibility + readability) / 4)

    issues: list[str] = []
    if not has_sources:
        issues.append("Missing source coverage for factual claims")
    if len(slides) < 15:
        issues.append("Deck is shorter than required 15-slide blueprint")

    return QualityReport(
        clarity_score=clarity,
        evidence_score=evidence,
        feasibility_score=feasibility,
        executive_readability_score=readability,
        overall_score=overall,
        pass_gate=overall >= 75,
        issues=issues,
    )
