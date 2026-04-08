# FastAPI app
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.environment import CodeReviewEnvironment
from app.models import Action, Observation, StepResult, StateResult
from pydantic import BaseModel

app = FastAPI(
    title="CodeReviewEnv",
    description="OpenEnv environment for AI-powered pull request code review.",
    version="1.0.0",
)

# Single shared environment instance (stateful per-session)
env = CodeReviewEnvironment()


class ResetRequest(BaseModel):
    task_id: str = "easy_bug_detection"


@app.get("/")
def root():
    return {
        "name": "CodeReviewEnv",
        "version": "1.0.0",
        "tasks": ["easy_bug_detection", "medium_security_review", "hard_concurrency_review"],
        "endpoints": ["/reset", "/step", "/state", "/health"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reset", response_model=Observation)
def reset(request: ResetRequest = None):
    try:
        task_id = "easy_bug_detection"
        if request and request.task_id:
            task_id = request.task_id
        obs = env.reset(task_id=task_id)
        return obs
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step", response_model=StepResult)
def step(action: Action):
    try:
        result = env.step(action)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state", response_model=StateResult)
def state():
    return env.state()


@app.get("/tasks")
def list_tasks():
    from app.tasks import TASKS
    return {
        task_id: {
            "pr_title": task["pr_title"],
            "difficulty": task_id.split("_")[0],
            "max_steps": task["max_steps"],
        }
        for task_id, task in TASKS.items()
    }