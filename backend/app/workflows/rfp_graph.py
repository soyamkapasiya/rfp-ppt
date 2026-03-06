from __future__ import annotations

from typing import Any, TypedDict

from app.models.domain import ClarifiedRequirement, RequirementInput
from app.services.claim_verifier import verify_claims
from app.services.crawler_service import CrawlerService
from app.services.graphrag_service import GraphRAGService
from app.services.question_miner import mine_questions
from app.services.quality_service import score_deck
from app.services.slide_planner import build_slide_plan
from app.services.slide_writer import write_slides
from app.services.source_quality_service import enrich_sources
from app.services.tavily_service import TavilyService


class RFPState(TypedDict):
    payload: dict[str, Any]
    clarified: dict[str, Any]
    research_docs: list[dict[str, Any]]
    question_bank: list[dict[str, Any]]
    slide_specs: list[dict[str, Any]]
    rendered_slides: list[dict[str, Any]]
    claim_report: dict[str, Any]
    quality_report: dict[str, Any]


def clarify_requirement_node(state: RFPState) -> RFPState:
    payload = RequirementInput(**state["payload"])
    clarified = ClarifiedRequirement(
        objectives=[f"Deliver measurable value for {payload.project_name}"],
        in_scope=[payload.requirement_text[:140]],
        out_of_scope=["Undocumented third-party integrations"],
        constraints=["Budget and timeline to be validated"],
        assumptions=["Stakeholder access available during delivery"],
    )
    state["clarified"] = clarified.model_dump()
    return state


def web_research_node(state: RFPState, tavily_api_key: str, graphrag: GraphRAGService) -> RFPState:
    payload = RequirementInput(**state["payload"])
    query = f"{payload.industry or ''} {payload.project_name} implementation best practices"
    discovery = TavilyService(tavily_api_key).search(query)

    crawler = CrawlerService()
    crawled = crawler.fetch_many([d.get("url", "") for d in discovery if d.get("url")])

    docs = []
    for idx, row in enumerate(discovery):
        text = ""
        for crawled_row in crawled:
            if crawled_row.get("url") == row.get("url"):
                text = crawled_row.get("text", "")
                row["fetched_at"] = crawled_row.get("fetched_at")
                break
        docs.append(
            {
                "id": f"src-{idx+1}",
                "title": row.get("title", ""),
                "url": row.get("url", ""),
                "content": row.get("content", ""),
                "text": text or row.get("content", ""),
                "fetched_at": row.get("fetched_at"),
            }
        )

    enriched = enrich_sources(docs)
    graphrag.ingest_documents(enriched)
    state["research_docs"] = enriched
    return state


def question_miner_node(state: RFPState) -> RFPState:
    clarified = ClarifiedRequirement(**state["clarified"])
    questions = mine_questions(clarified)
    state["question_bank"] = [q.model_dump() for q in questions]
    return state


def slide_planner_node(state: RFPState) -> RFPState:
    payload = RequirementInput(**state["payload"])
    clarified = ClarifiedRequirement(**state["clarified"])
    from app.models.domain import QuestionItem

    questions = [QuestionItem(**q) for q in state["question_bank"]]
    slides = build_slide_plan(payload.project_name, clarified, questions)
    state["slide_specs"] = [s.model_dump() for s in slides]
    return state


def slide_writer_node(state: RFPState) -> RFPState:
    from app.models.domain import SlideSpec

    slides = [SlideSpec(**s) for s in state["slide_specs"]]
    state["rendered_slides"] = write_slides(slides)
    return state


def quality_gate_node(state: RFPState) -> RFPState:
    claim_report = verify_claims(state.get("rendered_slides", []), state.get("research_docs", []))
    stale_count = len([s for s in state.get("research_docs", []) if s.get("freshness_days", 0) > 365])
    conflict_count = len(claim_report.get("conflicts", []))
    compliance_covered = any(
        "compliance" in (slide.get("title", "").lower())
        for slide in state.get("rendered_slides", [])
    )

    quality = score_deck(
        slides=state.get("rendered_slides", []),
        has_sources=claim_report["evidence_ok"],
        freshness_flags=stale_count,
        conflict_flags=conflict_count,
        compliance_covered=compliance_covered,
    )

    state["claim_report"] = claim_report
    state["quality_report"] = quality.model_dump()
    return state


def run_pipeline(payload: RequirementInput, tavily_api_key: str, graphrag: GraphRAGService) -> RFPState:
    state: RFPState = {
        "payload": payload.model_dump(),
        "clarified": {},
        "research_docs": [],
        "question_bank": [],
        "slide_specs": [],
        "rendered_slides": [],
        "claim_report": {},
        "quality_report": {},
    }

    try:
        from langgraph.graph import END, StateGraph

        graph = StateGraph(RFPState)
        graph.add_node("clarify", clarify_requirement_node)
        graph.add_node("research", lambda s: web_research_node(s, tavily_api_key, graphrag))
        graph.add_node("mine_questions", question_miner_node)
        graph.add_node("plan_slides", slide_planner_node)
        graph.add_node("write_slides", slide_writer_node)
        graph.add_node("qa", quality_gate_node)

        graph.set_entry_point("clarify")
        graph.add_edge("clarify", "research")
        graph.add_edge("research", "mine_questions")
        graph.add_edge("mine_questions", "plan_slides")
        graph.add_edge("plan_slides", "write_slides")
        graph.add_edge("write_slides", "qa")
        graph.add_edge("qa", END)

        return graph.compile().invoke(state)
    except Exception:
        state = clarify_requirement_node(state)
        state = web_research_node(state, tavily_api_key, graphrag)
        state = question_miner_node(state)
        state = slide_planner_node(state)
        state = slide_writer_node(state)
        state = quality_gate_node(state)
        return state
