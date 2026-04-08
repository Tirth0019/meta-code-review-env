# Core env logic (step/reset/state)
from app.models import Observation, Action, Reward, StepResult, StateResult
from app.tasks import TASKS, get_task_observation
from app.graders import GRADERS


class CodeReviewEnvironment:
    def __init__(self):
        self.task_id: str = "easy_bug_detection"
        self.step_number: int = 0
        self.done: bool = False
        self.cumulative_score: float = 0.0
        self.current_observation: Observation = get_task_observation(self.task_id)

    def reset(self, task_id: str = "easy_bug_detection") -> Observation:
        if task_id not in TASKS:
            raise ValueError(f"Unknown task_id: {task_id}. Choose from {list(TASKS.keys())}")
        self.task_id = task_id
        self.step_number = 0
        self.done = False
        self.cumulative_score = 0.0
        self.current_observation = get_task_observation(task_id, step_number=0)
        return self.current_observation

    def step(self, action: Action) -> StepResult:
        if self.done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")

        self.step_number += 1
        max_steps = TASKS[self.task_id]["max_steps"]

        # Grade the action
        grader = GRADERS[self.task_id]
        reward: Reward = grader(action)

        # Track cumulative (take the best score across steps)
        self.cumulative_score = max(self.cumulative_score, reward.score)

        # Episode ends when max steps reached or agent gets perfect score
        self.done = (self.step_number >= max_steps) or (reward.score >= 1.0)

        # Update observation
        self.current_observation = Observation(
            pr_title=self.current_observation.pr_title,
            pr_description=self.current_observation.pr_description,
            code_diff=self.current_observation.code_diff,
            file_names=self.current_observation.file_names,
            task_id=self.task_id,
            step_number=self.step_number,
            max_steps=max_steps,
        )

        return StepResult(
            observation=self.current_observation,
            reward=reward,
            done=self.done,
            info={
                "cumulative_score": self.cumulative_score,
                "steps_remaining": max(0, max_steps - self.step_number),
            },
        )

    def state(self) -> StateResult:
        return StateResult(
            task_id=self.task_id,
            step_number=self.step_number,
            max_steps=TASKS[self.task_id]["max_steps"],
            done=self.done,
            current_observation=self.current_observation,
            cumulative_score=self.cumulative_score,
        )