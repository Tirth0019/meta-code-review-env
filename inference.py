# Baseline inference script
import os
import json
import time
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN", "")
ENV_URL      = os.environ.get("ENV_URL", "http://localhost:7860")

client = OpenAI(api_key=HF_TOKEN or os.environ.get("OPENAI_API_KEY", ""), base_url=API_BASE_URL)

TASKS = ["easy_bug_detection", "medium_security_review", "hard_concurrency_review"]

SYSTEM_PROMPT = """You are an expert code reviewer. You will be given a pull request diff.
Your job is to identify ALL issues in the code including:
- Bugs (logic errors, off-by-one, missing operations)
- Security vulnerabilities (SQL injection, unvalidated input)
- Style issues (unused variables, misleading names)
- Concurrency problems (race conditions, missing thread joins)
- Error handling problems (bare except, swallowed exceptions)

Respond ONLY with a valid JSON object in this exact format:
{
  "review_comments": ["comment 1", "comment 2", "comment 3"],
  "verdict": "approve" | "request_changes" | "reject",
  "severity_flags": ["bug", "security", "style", "performance", "logic"]
}

Be specific and thorough. Name the exact lines or patterns you see."""


def call_env(method: str, endpoint: str, body: dict = None):
    import urllib.request
    url = f"{ENV_URL}{endpoint}"
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        url,
        data=data if method == "POST" else None,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def run_task(task_id: str) -> float:
    # Reset environment for this task
    obs = call_env("POST", "/reset", {"task_id": task_id})

    task_score = 0.0
    step_num = 0
    done = False

    print(json.dumps({
        "type": "[START]",
        "task_id": task_id,
        "pr_title": obs["pr_title"],
        "timestamp": time.time(),
    }))

    while not done:
        step_num += 1

        # Build prompt from observation
        user_prompt = f"""PR Title: {obs['pr_title']}
PR Description: {obs['pr_description']}
Files Changed: {', '.join(obs['file_names'])}

Code Diff:
{obs['code_diff']}

Review this pull request thoroughly and return your JSON response."""

        # Call LLM
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=800,
        )

        raw_content = response.choices[0].message.content.strip()

        # Parse LLM response
        try:
            # Strip markdown fences if present
            if "```" in raw_content:
                raw_content = raw_content.split("```")[1]
                if raw_content.startswith("json"):
                    raw_content = raw_content[4:]
            action_dict = json.loads(raw_content)
        except Exception as e:
            action_dict = {
                "review_comments": ["Unable to parse response"],
                "verdict": "request_changes",
                "severity_flags": [],
            }

        # Send action to environment
        step_result = call_env("POST", "/step", action_dict)

        reward = step_result["reward"]
        task_score = reward["score"]
        done = step_result["done"]

        print(json.dumps({
            "type": "[STEP]",
            "task_id": task_id,
            "step": step_num,
            "action": action_dict,
            "reward": task_score,
            "done": done,
            "breakdown": reward.get("breakdown", {}),
            "feedback": reward.get("feedback", ""),
        }))

        obs = step_result["observation"]

    return task_score


def main():
    scores = {}
    total = 0.0

    for task_id in TASKS:
        score = run_task(task_id)
        scores[task_id] = score
        total += score

    avg = total / len(TASKS)

    print(json.dumps({
        "type": "[END]",
        "scores": scores,
        "average_score": round(avg, 4),
        "model": MODEL_NAME,
        "timestamp": time.time(),
    }))


if __name__ == "__main__":
    main()