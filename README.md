---
title: Code Review Env
emoji: 🔍
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
tags:
  - openenv
---

# 🔍 CodeReviewEnv — OpenEnv Pull Request Review Environment

An OpenEnv-compliant environment where an AI agent acts as a **code reviewer**, evaluating pull requests to identify bugs, security vulnerabilities, style issues, and logic errors.

## 🌍 Real-World Motivation

Code review is one of the most critical and time-consuming tasks in software engineering. This environment trains and evaluates agents on their ability to perform meaningful, structured code review.

## 🧠 Tasks

| Task ID | Difficulty | Description |
|---|---|---|
| `easy_bug_detection` | Easy | Single-file PR with an off-by-one bug and unused variable |
| `medium_security_review` | Medium | PR with SQL injection vulnerability + pagination logic bug |
| `hard_concurrency_review` | Hard | Complex PR with race conditions, bare exceptions, misleading names |

## 📡 Action Space

- `review_comments`: list of specific issue comments
- `verdict`: approve, request_changes, or reject
- `severity_flags`: bug, security, style, performance, logic

## 👁️ Observation Space

- `pr_title`: string
- `pr_description`: string
- `code_diff`: string in unified diff format
- `file_names`: list of changed files
- `task_id`: string
- `step_number`: integer
- `max_steps`: integer

## 🏆 Reward Function

Rewards are shaped across multiple dimensions per task:
- Issue detection (did the agent find the key bug/vulnerability?)
- Verdict accuracy (approve / request_changes / reject correctly?)
- Severity flagging (did the agent categorize the issue type?)

All rewards are in range 0.0 to 1.0 with partial credit for partial detection.

## ⚙️ Setup & Usage

### Local

    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 7860

### Docker

    docker build -t code-review-env .
    docker run -p 7860:7860 code-review-env

### Inference

    export OPENAI_API_KEY=your-key
    export MODEL_NAME=llama-3.3-70b-versatile
    export API_BASE_URL=https://api.groq.com/openai/v1
    export ENV_URL=http://localhost:7860
    python inference.py

## 📊 Baseline Scores

| Task | Model | Score |
|---|---|---|
| easy_bug_detection | llama-3.3-70b-versatile | 1.00 |
| medium_security_review | llama-3.3-70b-versatile | 0.65 |
| hard_concurrency_review | llama-3.3-70b-versatile | 0.80 |
| **Average** | | **0.82** |

## 🗂️ Project Structure

    code-review-env/
    ├── app/
    │   ├── models.py
    │   ├── environment.py
    │   ├── tasks.py
    │   └── graders.py
    ├── main.py
    ├── inference.py
    ├── openenv.yaml
    ├── Dockerfile
    └── README.md