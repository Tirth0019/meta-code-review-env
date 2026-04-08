from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class Verdict(str, Enum):
    approve = "approve"
    request_changes = "request_changes"
    reject = "reject"


class SeverityFlag(str, Enum):
    bug = "bug"
    security = "security"
    style = "style"
    performance = "performance"
    logic = "logic"


class Observation(BaseModel):
    pr_title: str
    pr_description: str
    code_diff: str
    file_names: List[str]
    task_id: str
    step_number: int
    max_steps: int


class Action(BaseModel):
    review_comments: List[str] = Field(
        ...,
        description="List of review comments identifying specific issues in the code"
    )
    verdict: Verdict = Field(
        ...,
        description="Final verdict: approve, request_changes, or reject"
    )
    severity_flags: List[SeverityFlag] = Field(
        default=[],
        description="Categories of issues found: bug, security, style, performance, logic"
    )


class Reward(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    breakdown: dict = Field(default_factory=dict)
    feedback: str = ""


class StepResult(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: dict = Field(default_factory=dict)


class StateResult(BaseModel):
    task_id: str
    step_number: int
    max_steps: int
    done: bool
    current_observation: Observation
    cumulative_score: float