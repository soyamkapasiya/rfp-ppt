from typing import Any, TypedDict


class RFPState(TypedDict):
    requirement_text: str
    clarified: dict[str, Any]
    research_docs: list[dict[str, Any]]
    question_bank: list[dict[str, Any]]
    slide_specs: list[dict[str, Any]]
    quality_report: dict[str, Any]
    pptx_path: str


def build_graph() -> object:
    return {"graph": "placeholder"}
