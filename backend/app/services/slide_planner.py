"""
slide_planner.py – Builds the full 15-slide RFP deck plan.

Every slide is informed by the RFP domain knowledge defined in the
official Investopedia/Genspark definition:

  A Request for Proposal (RFP) is a document that announces a project,
  describes it, invites qualified contractors to bid, outlines the bidding
  process and contract terms, and includes a statement of work describing
  tasks and timelines.

Slides cover: title context, executive summary, problem understanding,
proposed solution, technical architecture, delivery methodology,
timeline/milestones, team/governance, risk/mitigation, security/compliance,
costing assumptions, client questions answered, differentiators, next steps,
and appendix.
"""

from __future__ import annotations

from typing import Any
from app.models.domain import ClarifiedRequirement, QuestionItem, SlideSpec

# ── RFP domain knowledge (from Investopedia / Genspark AI Slides source) ─────
RFP_DEFINITION_BULLETS = [
    "An RFP announces a specific project and invites qualified contractors to bid",
    "Defines project scope, goals, bidding process, and contract terms",
    "Includes a Statement of Work (SoW) with tasks and delivery timeline",
    "Used by government agencies and private organisations to ensure open competition",
    "Enables the issuer to evaluate financial health, feasibility, and capability of bidders",
]

RFP_PROCESS_BULLETS = [
    "RFP issued → Bidders review & submit questions → Final RFP published",
    "Proposals submitted → Short-listed → Negotiations on price & technical detail",
    "Best & Final Offer (BAFO) requested → Contract awarded to best-value bidder",
    "Contract start date confirmed; Statement of Work becomes binding",
    "Post-award governance and reporting structure established",
]

RFP_REQUIREMENTS_BULLETS = [
    "Project description with clear scope, objectives, and deliverables",
    "Budget range and funding sources disclosed",
    "Proposed timeline with key milestones and acceptance criteria",
    "Evaluation criteria: technical merit, price, past performance, compliance",
    "Vendor qualification requirements: certifications, references, financial stability",
]

RFP_BENEFITS_BULLETS = [
    "Open competition drives down project cost by 15–30% on average",
    "Structured evaluation removes bias and cronyism from vendor selection",
    "Multiple alternative proposals introduce creative, innovative solutions",
    "Defined contract terms protect both issuer and winning contractor",
    "Transparent process builds stakeholder confidence and auditability",
]

RFP_VS_RFQ_RFI_BULLETS = [
    "RFP – Open-ended; project defined but contractor creativity is encouraged",
    "RFQ (Request for Quote) – Exact specs known; seeking best-price supplier",
    "RFI (Request for Information) – Market scan; no commitment to award",
    "Use RFP when scope is complex and solutions are not pre-determined",
    "Use RFQ when buying commodities or well-defined services at scale",
]

REQUIRED_SLIDES: list[dict] = [
    {
        "title": "Title + Context",
        "default_bullets": [
            "Project name, issuing organisation, and submission date",
            "This response is prepared in direct answer to your published RFP",
            "We have read and accepted all terms in the Request for Proposal",
            "Our proposal covers all mandatory requirements set out in the SoW",
            "Contact: [Account Executive] | [email] | [phone]",
        ],
    },
    {
        "title": "Executive Summary",
        "default_bullets": [
            "We deliver measurable business value aligned with your stated objectives",
            "Our solution reduces implementation risk through phased, agile rollout",
            "Budget and timeline are validated against your RFP constraints",
            "Proven track record with 50+ similar projects in this industry",
            "Committed to full compliance with regulatory and security requirements",
        ],
    },
    {
        "title": "Problem Understanding",
        "default_bullets": RFP_DEFINITION_BULLETS,
    },
    {
        "title": "Proposed Solution Overview",
        "default_bullets": [
            "End-to-end solution addressing all in-scope RFP requirements",
            "Modular architecture allowing phased delivery with early value realisation",
            "Integration with existing systems via open APIs and standard connectors",
            "Cloud-native design ensuring scalability and high availability",
            "Vendor-agnostic tooling to avoid lock-in and protect long-term investment",
        ],
    },
    {
        "title": "Technical Architecture",
        "default_bullets": [
            "Microservices architecture deployed on Kubernetes for resilience",
            "Event-driven messaging layer (Kafka/RabbitMQ) for real-time processing",
            "Data lake + warehouse pattern separating raw ingestion from analytics",
            "Zero-trust security model with mTLS between all internal services",
            "CI/CD pipeline with automated testing, SAST, and DAST gates",
        ],
    },
    {
        "title": "Delivery Methodology",
        "default_bullets": [
            "Agile Scrum with 2-week sprints; stakeholder demos every sprint",
            "Dedicated delivery squad: Project Manager, Tech Lead, QA, BA, DevOps",
            "Weekly steering committee with RAG status dashboard",
            "Definition of Done enforced: code review, test coverage ≥ 80%, doc sign-off",
            "Continuous risk register maintained; escalation path defined on Day 1",
        ],
    },
    {
        "title": "Timeline and Milestones",
        "default_bullets": [
            "Week 1–2: Project kick-off, environment setup, SoW finalisation",
            "Week 3–8: Discovery, architecture review, Sprint 1–3 delivery",
            "Week 9–16: Core feature build, integration, UAT (Sprints 4–8)",
            "Week 17–20: Performance testing, security audit, go-live rehearsal",
            "Week 21–22: Production go-live, hypercare, handover to operations",
        ],
    },
    {
        "title": "Team and Governance",
        "default_bullets": [
            "Executive Sponsor + Programme Director: single point of escalation",
            "Delivery Squad: 6 FTEs with domain-certified practitioners",
            "Change Control Board meeting bi-weekly; decisions documented",
            "RACI matrix shared on Day 1; updated at each phase gate",
            "Dedicated Client Success Manager for the first 90 days post go-live",
        ],
    },
    {
        "title": "Risk and Mitigation",
        "archetype": "Governance",
        "layout": "risk_matrix",
        "default_bullets": [
            "Risk 1 – Scope creep: Managed via formal Change Request process",
            "Risk 2 – Third-party delays: Buffer weeks built into critical path",
            "Risk 3 – Key-person dependency: Cross-training and documented playbooks",
            "Risk 4 – Data migration complexity: Parallel-run strategy for 4 weeks",
            "Risk 5 – Regulatory changes: Quarterly compliance review cadence",
        ],
    },
    {
        "title": "Security & Compliance",
        "default_bullets": [
            "ISO 27001 / SOC 2 Type II certified; audit reports available on request",
            "GDPR / DPDP compliant data handling; DPA signed before project start",
            "Penetration test conducted every 6 months by accredited third-party",
            "Encryption at rest (AES-256) and in transit (TLS 1.3) enforced everywhere",
            "Vulnerability disclosure policy with 72-hour critical patch SLA",
        ],
    },
    {
        "title": "Costing Assumptions",
        "default_bullets": [
            "Fixed-price engagement for Phases 1–2; T&M for Phase 3 change requests",
            "Travel and expenses billed at cost with monthly cap agreed upfront",
            "Software licences and cloud infrastructure quoted separately (pass-through)",
            "10% contingency included in the base estimate for unforeseen complexity",
            "Payment schedule: 25% on start, 50% at UAT sign-off, 25% at go-live",
        ],
    },
    {
        "title": "Client Questions Answered",
        "default_bullets": [
            "Q: What is the non-negotiable go-live date? A: We align to your stated deadline",
            "Q: Which compliance standards apply? A: All mandatory standards are in scope",
            "Q: What are data ownership rights? A: Client retains full data ownership",
            "Q: How are change requests handled? A: Formal CR process with impact analysis",
            "Q: What happens post go-live? A: 90-day hypercare + optional managed service",
        ],
    },
    {
        "title": "Why Us / Competitive Analysis",
        "archetype": "Competition",
        "default_bullets": [
            "Our solution vs. key market alternatives",
            "Direct comparison of industry accelerators",
            "Unique ROI drivers and cost-efficiency metrics",
            "Proprietary methodology derived from successful bids",
            "Why our specific approach beats generic competitors",
        ],
    },
    {
        "title": "Clarification Report",
        "archetype": "Governance",
        "layout": "grid",
        "default_bullets": [
            "High-priority questions identified for project success",
            "Gaps in requirement documentation requiring workshop",
            "Security and compliance clarifications",
            "Operational assumptions flagged for validation",
            "Next steps for requirement finalization",
        ],
    },
    {
        "title": "Next Steps",
        "archetype": "Conclusion",
        "default_bullets": RFP_PROCESS_BULLETS,
    },
    {
        "title": "Appendix with References",
        "archetype": "Conclusion",
        "default_bullets": [
            "Investopedia: 'Request for Proposal (RFP): What It Is, Requirements, and Tips'",
            "Chesapeake Bay Trust sample RFP – best-practice formatting reference",
            "RTI International RFP template – section structure reference",
            "TechSoup RFP Library – nonprofit and public-sector RFP examples",
            "ISO 27001:2022 – Information Security Management standard",
        ],
    },
]


def build_slide_plan(
    project_name: str,
    clarified: ClarifiedRequirement,
    questions: list[QuestionItem],
    competition_report: dict[str, Any] | None = None,
) -> list[SlideSpec]:
    """Return the full 15-slide plan, enriched with clarified requirement data and win-rate signals."""
    planned: list[SlideSpec] = []
    
    # ── Point 6: Win-rate signals (Fictional Meta-steering) ──────────────
    # If win-rate is high for Pricing focused bids, we prioritize that archetype
    win_signal = competition_report.get("win_rate", 0.7) if competition_report else 0.7
    priority_archetype = "Economics" if win_signal > 0.8 else "Technical"

    for tpl in REQUIRED_SLIDES:
        title: str = tpl["title"]
        archetype: str = tpl.get("archetype", "General")
        bullets: list[str] = list(tpl["default_bullets"])
        layout: str = tpl.get("layout", "standard")
        visual_prompt: str | None = None
        win_themes: list[str] = []

        if competition_report:
            win_themes = [competition_report.get("our_edge", "")]

        # ── Personalise selected slides & layouts ──────────────────────────
        if title == "Title + Context":
            bullets[0] = f"Project: {project_name}  |  Responding to your published RFP"
            layout = "title"

        elif title == "Executive Summary":
            if clarified.objectives:
                bullets[0] = clarified.objectives[0]
            if clarified.constraints:
                bullets[1] = f"Constraints acknowledged: {clarified.constraints[0]}"
            # Adjust layout based on win-rate priority
            layout = "two_column" if priority_archetype == "Technical" else "comparison"

        elif title == "Problem Understanding":
            if clarified.in_scope:
                bullets = [f"In scope: {s}" for s in clarified.in_scope[:3]] + bullets[3:]
            if clarified.out_of_scope:
                bullets.append(f"Out of scope: {clarified.out_of_scope[0]}")
            layout = "standard"

        elif title == "Proposed Solution Overview":
            layout = "two_column"
            visual_prompt = f"Futuristic technical solution architecture for {project_name}, 3D flat design"

        elif title == "Technical Architecture":
            layout = "standard"
            visual_prompt = "Complex systems diagram, clean corporate aesthetic, blueprint style"

        elif title == "Timeline and Milestones":
            layout = "timeline"

        elif title == "Team and Governance":
            layout = "team"

        elif title == "Security & Compliance":
            layout = "two_column"

        elif title == "Client Questions Answered":
            if questions:
                q_bullets = [f"Q: {q.question}" for q in questions[:5]]
                bullets = q_bullets or bullets
            layout = "standard"

        elif title == "Why Us / Differentiators":
            if competition_report:
                bullets = [f"Differentiator: {competition_report.get('our_edge', 'Proprietary accelerators')}"] + bullets[1:4]
                if competition_report.get("competitors"):
                    bullets.append(f"Analysis vs: {', '.join(competition_report['competitors'])}")
            layout = "comparison"
            visual_prompt = "Scale icon representing balance and competitive advantage, premium 3D"

        elif title == "Appendix with References":
            if clarified.assumptions:
                bullets.insert(0, f"Key assumption: {clarified.assumptions[0]}")
                bullets = bullets[:5]
            layout = "standard"

        planned.append(
            SlideSpec(
                title=title,
                objective=f"Cover '{title}' comprehensively and persuasively",
                bullets=bullets[:7],
                layout=layout,
                archetype=archetype,
                win_themes=win_themes,
                references=[],
                visual_prompt=visual_prompt,
            )
        )

    return planned
