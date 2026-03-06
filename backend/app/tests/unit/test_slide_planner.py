from app.models.domain import ClarifiedRequirement
from app.services.question_miner import mine_questions
from app.services.slide_planner import REQUIRED_SLIDES, build_slide_plan


def test_slide_plan_has_required_blueprint() -> None:
    clarified = ClarifiedRequirement(
        objectives=["Increase conversion"],
        in_scope=["CRM integration", "Dashboard"],
        out_of_scope=["ERP replacement"],
        constraints=["Three-month deadline"],
        assumptions=["API access available"],
    )
    questions = mine_questions(clarified)
    slides = build_slide_plan("Test Project", clarified, questions)

    assert len(slides) == len(REQUIRED_SLIDES)
    assert slides[0].title == "Title + context"
    assert any(s.title == "Client questions" for s in slides)
