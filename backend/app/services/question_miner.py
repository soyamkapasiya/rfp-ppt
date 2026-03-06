"""
question_miner.py – Mines clarification questions from the RFP.

Generates RFP-domain-specific questions based on the official RFP framework:
  - Timeline / go-live constraints
  - Data ownership and source-of-truth systems
  - Compliance standards in scope
  - Evaluation criteria weightings
  - Budget structure (fixed-price vs T&M)
  - Vendor qualification requirements
"""

from __future__ import annotations

from app.models.domain import ClarifiedRequirement, QuestionItem


_BASE_QUESTIONS: list[QuestionItem] = [
    QuestionItem(
        question="What is the mandatory go-live date and any blackout windows we must respect?",
        category="timeline",
        reason="Delivery planning and milestone dates depend on hard deadline constraints.",
        priority="high",
    ),
    QuestionItem(
        question="Which systems are the authoritative sources of truth for core business entities?",
        category="data",
        reason="Integration architecture and migration scope hinge on data ownership.",
        priority="high",
    ),
    QuestionItem(
        question="Which compliance and regulatory standards (ISO 27001, GDPR, SOC 2, etc.) are mandatory in scope?",
        category="compliance",
        reason="Security controls, architecture patterns, and audit requirements depend on regulatory scope.",
        priority="high",
    ),
    QuestionItem(
        question="What are the evaluation criteria weightings (technical vs price vs past performance)?",
        category="functional",
        reason="Knowing the evaluation model helps us optimise the proposal structure and emphasis.",
        priority="high",
    ),
    QuestionItem(
        question="Is the engagement structured as fixed-price, time-and-materials, or a hybrid?",
        category="budget",
        reason="Commercial model affects how we scope contingency and change control.",
        priority="high",
    ),
    QuestionItem(
        question="What vendor qualifications and certifications are required to be eligible?",
        category="functional",
        reason="Ensures our proposal meets all mandatory qualification thresholds before evaluation.",
        priority="medium",
    ),
    QuestionItem(
        question="Are there mandatory infrastructure or vendor restrictions we must work within?",
        category="operations",
        reason="Toolchain, cloud provider, and architecture choices may be pre-constrained.",
        priority="medium",
    ),
    QuestionItem(
        question="What post-go-live support and SLA obligations are expected under the contract?",
        category="operations",
        reason="Hypercare, support tiers, and SLA levels must be costed and resourced.",
        priority="medium",
    ),
    QuestionItem(
        question="Will a Best and Final Offer (BAFO) round be conducted before contract award?",
        category="timeline",
        reason="BAFO preparation requires additional resources and timing; we need to plan for it.",
        priority="low",
    ),
    QuestionItem(
        question="What is the process for raising and adjudicating change requests post-award?",
        category="functional",
        reason="Change control governance must be agreed upfront to prevent scope disputes.",
        priority="low",
    ),
]


def mine_questions(clarified: ClarifiedRequirement) -> list[QuestionItem]:
    """Return the full set of RFP clarification questions, augmented by constraint context."""
    questions = list(_BASE_QUESTIONS)

    # Add constraint-driven question if constraints are populated
    if clarified.constraints:
        questions.append(
            QuestionItem(
                question=f"Regarding the constraint '{clarified.constraints[0][:100]}' – is this a hard limit or a negotiable preference?",
                category="functional",
                reason="Hard vs soft constraints directly affect solution design and commercial risk.",
                priority="high",
            )
        )

    # Add assumption-validation question
    if clarified.assumptions:
        questions.append(
            QuestionItem(
                question=f"Can you confirm that '{clarified.assumptions[0][:100]}' is an accurate assumption for this engagement?",
                category="functional",
                reason="Validating key assumptions reduces delivery risk and scope ambiguity.",
                priority="medium",
            )
        )

    return questions
