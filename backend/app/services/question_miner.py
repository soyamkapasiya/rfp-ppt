from app.models.domain import ClarifiedRequirement, QuestionItem


def mine_questions(clarified: ClarifiedRequirement) -> list[QuestionItem]:
    questions = [
        QuestionItem(
            question="What is the non-negotiable go-live date and blackout windows?",
            category="timeline",
            reason="Delivery planning depends on hard constraints.",
            priority="high",
        ),
        QuestionItem(
            question="Which systems are sources of truth for core entities?",
            category="data",
            reason="Integration and migration scope depends on data ownership.",
            priority="high",
        ),
        QuestionItem(
            question="Which compliance standards are mandatory in scope?",
            category="compliance",
            reason="Security controls and design patterns depend on regulatory scope.",
            priority="high",
        ),
    ]
    if clarified.constraints:
        questions.append(
            QuestionItem(
                question="Are there mandatory vendor or infrastructure restrictions?",
                category="operations",
                reason="Toolchain and architecture choices may be constrained.",
                priority="medium",
            )
        )
    return questions
