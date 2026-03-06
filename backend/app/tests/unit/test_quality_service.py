from app.services.quality_service import score_deck


def test_quality_gate_fails_without_sources() -> None:
    slides = [{"title": "S1", "bullets": ["a"]}] * 15
    report = score_deck(slides=slides, has_sources=False)
    assert report.evidence_score < 75


def test_quality_gate_passes_with_sources() -> None:
    slides = [{"title": "S1", "bullets": ["a"]}] * 15
    report = score_deck(slides=slides, has_sources=True)
    assert report.pass_gate is True
