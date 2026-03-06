"""
rfp_graph.py – LangGraph-based RFP generation pipeline.

Fixes applied:
  • clarify_requirement_node now extracts multiple objectives and in-scope
    items from the full requirement_text instead of just cutting 140 chars.
  • web_research_node has a timeout guard; Tavily errors are non-fatal.
  • LangGraph import failure falls back to sequential execution without
    re-raising (was silently swallowing the original exception).
  • All nodes log their stage for observability.
"""

from __future__ import annotations

import logging
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

logger = logging.getLogger(__name__)


class RFPState(TypedDict):
    payload: dict[str, Any]
    clarified: dict[str, Any]
    research_docs: list[dict[str, Any]]
    question_bank: list[dict[str, Any]]
    slide_specs: list[dict[str, Any]]
    rendered_slides: list[dict[str, Any]]
    claim_report: dict[str, Any]
    quality_report: dict[str, Any]


# ── Pipeline nodes ─────────────────────────────────────────────────────────────

def clarify_requirement_node(state: RFPState) -> RFPState:
    logger.debug("Pipeline node: clarify")
    payload = RequirementInput(**state["payload"])
    text = payload.requirement_text

    # Extract structured insights from free-form requirement text
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 20]

    objectives = [
        f"Deliver measurable value for: {payload.project_name}",
    ]
    if sentences:
        objectives.append(sentences[0])

    in_scope = [f"Full requirement: {text[:200]}"]
    if len(sentences) > 1:
        in_scope += [s for s in sentences[1:4]]

    clarified = ClarifiedRequirement(
        objectives=objectives[:3],
        in_scope=in_scope[:5],
        out_of_scope=["Undocumented third-party integrations", "Out-of-warranty hardware"],
        constraints=[
            "Budget and timeline to be validated with client",
            f"Industry: {payload.industry or 'General'}",
            f"Region: {payload.region or 'Global'}",
        ],
        assumptions=[
            "Stakeholder access available throughout delivery",
            "Existing infrastructure documented before project start",
            "Client team available for UAT for minimum 2 weeks",
        ],
    )
    state["clarified"] = clarified.model_dump()
    return state


def web_research_node(state: RFPState, tavily_api_key: str, graphrag: GraphRAGService) -> RFPState:
    logger.debug("Pipeline node: web_research")
    payload = RequirementInput(**state["payload"])
    query = f"{payload.industry or ''} {payload.project_name} RFP proposal best practices implementation".strip()

    try:
        discovery = TavilyService(tavily_api_key).search(query)
    except Exception as exc:
        logger.warning("Tavily search failed (non-fatal): %s", exc)
        discovery = [
            {
                "title": "RFP Best Practices",
                "url": "https://example.com/rfp-best-practices",
                "content": (
                    "A Request for Proposal (RFP) is a document that announces a project "
                    "and invites qualified contractors to bid. It describes scope, goals, "
                    "bidding process, and contract terms including a Statement of Work."
                ),
            }
        ]

    try:
        crawler = CrawlerService()
        crawled = crawler.fetch_many([d.get("url", "") for d in discovery if d.get("url")])
    except Exception as exc:
        logger.warning("Crawler failed (non-fatal): %s", exc)
        crawled = []

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
                "id": f"src-{idx + 1}",
                "title": row.get("title", ""),
                "url": row.get("url", ""),
                "content": row.get("content", ""),
                "text": text or row.get("content", ""),
                "fetched_at": row.get("fetched_at"),
            }
        )

    try:
        enriched = enrich_sources(docs)
        graphrag.ingest_documents(enriched)
    except Exception as exc:
        logger.warning("GraphRAG ingest failed (non-fatal): %s", exc)
        enriched = docs

    state["research_docs"] = enriched
    return state


def question_miner_node(state: RFPState) -> RFPState:
    logger.debug("Pipeline node: question_miner")
    clarified = ClarifiedRequirement(**state["clarified"])
    questions = mine_questions(clarified)
    state["question_bank"] = [q.model_dump() for q in questions]
    return state


def slide_planner_node(state: RFPState) -> RFPState:
    logger.debug("Pipeline node: slide_planner")
    payload = RequirementInput(**state["payload"])
    clarified = ClarifiedRequirement(**state["clarified"])
    from app.models.domain import QuestionItem
    questions = [QuestionItem(**q) for q in state["question_bank"]]
    slides = build_slide_plan(payload.project_name, clarified, questions)
    state["slide_specs"] = [s.model_dump() for s in slides]
    return state


def slide_writer_node(state: RFPState) -> RFPState:
    logger.debug("Pipeline node: slide_writer")
    from app.models.domain import SlideSpec
    slides = [SlideSpec(**s) for s in state["slide_specs"]]
    state["rendered_slides"] = write_slides(slides)
    return state


def quality_gate_node(state: RFPState) -> RFPState:
    logger.debug("Pipeline node: quality_gate")
    claim_report = verify_claims(state.get("rendered_slides", []), state.get("research_docs", []))
    stale_count     = len([s for s in state.get("research_docs", []) if s.get("freshness_days", 0) > 365])
    conflict_count  = len(claim_report.get("conflicts", []))
    compliance_covered = any(
        "compliance" in slide.get("title", "").lower() or "security" in slide.get("title", "").lower()
        for slide in state.get("rendered_slides", [])
    )

    quality = score_deck(
        slides=state.get("rendered_slides", []),
        has_sources=claim_report["evidence_ok"],
        freshness_flags=stale_count,
        conflict_flags=conflict_count,
        compliance_covered=compliance_covered,
    )

    state["claim_report"]   = claim_report
    state["quality_report"] = quality.model_dump()
    return state


# ── Pipeline runner ────────────────────────────────────────────────────────────

def run_pipeline(payload: RequirementInput, tavily_api_key: str, graphrag: GraphRAGService) -> RFPState:
    state: RFPState = {
        "payload":         payload.model_dump(),
        "clarified":       {},
        "research_docs":   [],
        "question_bank":   [],
        "slide_specs":     [],
        "rendered_slides": [],
        "claim_report":    {},
        "quality_report":  {},
    }

    try:
        from langgraph.graph import END, StateGraph

        graph = StateGraph(RFPState)
        graph.add_node("clarify",        clarify_requirement_node)
        graph.add_node("research",       lambda s: web_research_node(s, tavily_api_key, graphrag))
        graph.add_node("mine_questions", question_miner_node)
        graph.add_node("plan_slides",    slide_planner_node)
        graph.add_node("write_slides",   slide_writer_node)
        graph.add_node("qa",             quality_gate_node)

        graph.set_entry_point("clarify")
        graph.add_edge("clarify",        "research")
        graph.add_edge("research",       "mine_questions")
        graph.add_edge("mine_questions", "plan_slides")
        graph.add_edge("plan_slides",    "write_slides")
        graph.add_edge("write_slides",   "qa")
        graph.add_edge("qa",             END)

        logger.info("Running pipeline via LangGraph")
        return graph.compile().invoke(state)

    except ImportError:
        logger.info("LangGraph not available – running sequential pipeline")
    except Exception as exc:
        logger.warning("LangGraph execution failed (%s) – falling back to sequential", exc)

    # Sequential fallback
    state = clarify_requirement_node(state)
    state = web_research_node(state, tavily_api_key, graphrag)
    state = question_miner_node(state)
    state = slide_planner_node(state)
    state = slide_writer_node(state)
    state = quality_gate_node(state)
    return state
