from typing import Literal

from pydantic import BaseModel, Field


class RequirementInput(BaseModel):
    project_name: str
    industry: str | None = None
    region: str | None = None
    requirement_text: str = Field(min_length=40)
    role: str | None = "Solutions Architect"
    tone: Literal["professional", "visionary", "concise", "technical"] = "professional"
    attachments: list[str] = Field(default_factory=list)  # URLs or base64 paths


class ClarifiedRequirement(BaseModel):
    objectives: list[str]
    in_scope: list[str]
    out_of_scope: list[str]
    constraints: list[str]
    assumptions: list[str]
    competitive_advantage: list[str] = Field(default_factory=list)
    needs_more_info: bool = False


class QuestionItem(BaseModel):
    question: str
    category: Literal[
        "functional",
        "technical",
        "security",
        "compliance",
        "data",
        "timeline",
        "budget",
        "operations",
    ]
    reason: str
    priority: Literal["high", "medium", "low"] = "medium"


class SlideSpec(BaseModel):
    title: str
    objective: str
    bullets: list[str]
    layout: Literal["standard", "two_column", "comparison", "team", "timeline", "title", "grid", "risk_matrix"] = "standard"
    archetype: str | None = None  # e.g., "Executive Summary", "Technical Architecture"
    win_themes: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    visual_prompt: str | None = None


class QualityReport(BaseModel):
    clarity_score: int
    evidence_score: int
    feasibility_score: int
    executive_readability_score: int
    visual_density_score: int = 0
    narrative_arc_score: int = 0
    overall_score: int
    pass_gate: bool
    issues: list[str] = Field(default_factory=list)
    slide_critiques: dict[str, str] = Field(default_factory=dict)  # "Slide Title": "Specific feedback"
