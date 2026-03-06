from typing import Literal

from pydantic import BaseModel, Field


class RequirementInput(BaseModel):
    project_name: str
    industry: str | None = None
    region: str | None = None
    requirement_text: str = Field(min_length=40)


class ClarifiedRequirement(BaseModel):
    objectives: list[str]
    in_scope: list[str]
    out_of_scope: list[str]
    constraints: list[str]
    assumptions: list[str]


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
    references: list[str] = Field(default_factory=list)


class QualityReport(BaseModel):
    clarity_score: int
    evidence_score: int
    feasibility_score: int
    executive_readability_score: int
    overall_score: int
    pass_gate: bool
    issues: list[str] = Field(default_factory=list)
