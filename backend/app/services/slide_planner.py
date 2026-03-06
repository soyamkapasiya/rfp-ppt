from app.models.domain import ClarifiedRequirement, QuestionItem, SlideSpec

REQUIRED_SLIDES = [
    "Title + context",
    "Executive summary",
    "Problem understanding",
    "Proposed solution overview",
    "Technical architecture",
    "Delivery methodology",
    "Timeline and milestones",
    "Team and governance",
    "Risk and mitigation",
    "Security/compliance",
    "Costing assumptions",
    "Client questions",
    "Why us / differentiators",
    "Next steps",
    "Appendix with references",
]


def build_slide_plan(
    project_name: str,
    clarified: ClarifiedRequirement,
    questions: list[QuestionItem],
) -> list[SlideSpec]:
    planned: list[SlideSpec] = []
    for title in REQUIRED_SLIDES:
        bullets = [
            f"Project focus: {project_name}",
            "Keep commitments tied to evidence",
            "Highlight delivery feasibility",
        ]
        if title == "Executive summary":
            bullets = [
                clarified.objectives[0] if clarified.objectives else "Deliver measurable business impact",
                "Sequence rollout to reduce implementation risk",
                "Align plan with budget and timeline constraints",
            ]
        elif title == "Problem understanding":
            bullets = clarified.in_scope[:5] or ["Refine problem statement and success criteria"]
        elif title == "Client questions":
            bullets = [q.question for q in questions[:5]] or ["No unresolved questions"]
        elif title == "Appendix with references":
            bullets = ["See sources.json for full evidence list", "See assumptions log for boundaries"]

        planned.append(
            SlideSpec(
                title=title,
                objective=f"Cover {title.lower()} clearly",
                bullets=bullets[:5],
                references=[],
            )
        )
    return planned
