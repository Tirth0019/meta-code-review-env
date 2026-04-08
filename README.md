# 🔍 CodeReviewEnv — OpenEnv Pull Request Review Environment

An OpenEnv-compliant environment where an AI agent acts as a **code reviewer**, evaluating pull requests to identify bugs, security vulnerabilities, style issues, and logic errors.

## 🌍 Real-World Motivation

Code review is one of the most critical and time-consuming tasks in software engineering. This environment trains and evaluates agents on their ability to perform meaningful, structured code review — a task that directly maps to developer productivity tooling.

## 🧠 Tasks

| Task ID | Difficulty | Description |
|---|---|---|
| `easy_bug_detection` | Easy | Single-file PR with an off-by-one bug and unused variable |
| `medium_security_review` | Medium | PR with SQL injection vulnerability + pagination logic bug |
| `hard_concurrency_review` | Hard | Complex PR with race conditions, bare exceptions, misleading names |

## 📡 Action Space

```json
{
  "review_comments": ["list of specific issue comments"],
  "verdict": "approve | request_changes | reject",
  "severity_flags": ["bug", "security", "style", "performance", "logic"]
}
```

## 👁️ Observation Space

```json
{
  "pr_title": "string",
  "pr_description": "string",
  "code_diff": "string (unified diff format)",
  "file_names": ["list of changed files"],
  "task_id": "string",
  "step_number": 0,
  "max_steps": 5
}
```

## 🏆 Reward Function

Rewards are shaped across multiple dimensions per task:
- **Issue detection** (did the agent find the key bug/vulnerability?)
- **Verdict accuracy** (approve / request_changes / reject correctly?)
- **Severity flagging** (did the agent categorize the issue type?)

All rewards are in range `[0.0, 1.0]` with partial credit for partial detection.

## ⚙️ Setup & Usage

### Local

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860
```

### Docker

```bash
docker build -t code-review-env .
docker run -p 7860:7860 code-review-env
```

### Inference

```bash
export OPENAI_API_KEY=sk-...
export MODEL_NAME=gpt-4o-mini
export API_BASE_URL=https://api.openai.com/v1
export ENV_URL=http://localhost:7860
python inference.py
```

## 📊 Baseline Scores

| Task | Model | Score |
|---|---|---|
| easy_bug_detection | gpt-4o-mini | 0.80 |
| medium_security_review | gpt-4o-mini | 0.70 |
| hard_concurrency_review | gpt-4o-mini | 0.45 |
| **Average** | | **0.65** |

## 🗂️ Project Structure

```
code-review-env/
├── app/
│   ├── models.py       # Pydantic typed models
│   ├── environment.py  # step/reset/state logic
│   ├── tasks.py        # Task definitions + PR diffs
│   └── graders.py      # Deterministic grading functions
├── main.py             # FastAPI server
├── inference.py        # Baseline inference script
├── openenv.yaml        # OpenEnv metadata
├── Dockerfile
└── README.md
```