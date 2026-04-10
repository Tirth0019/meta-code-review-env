from app.models import Action, Reward
from app.tasks import TASKS


def _keyword_hit(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def _comments_hit(comments: list[str], keywords: list[str]) -> bool:
    combined = " ".join(comments).lower()
    return any(kw.lower() in combined for kw in keywords)


def grade_easy(action: Action) -> Reward:
    expected = TASKS["easy_bug_detection"]["expected_issues"]
    score = 0.0
    breakdown = {}

    # 1. Bug identified (40 pts)
    bug_found = _comments_hit(action.review_comments, expected["bugs"])
    breakdown["bug_identified"] = bug_found
    if bug_found:
        score += 0.40

    # 2. Style issue identified (20 pts)
    style_found = _comments_hit(action.review_comments, expected["style"])
    breakdown["style_identified"] = style_found
    if style_found:
        score += 0.20

    # 3. Correct verdict (25 pts)
    correct_verdict = action.verdict.value == expected["verdict"]
    breakdown["correct_verdict"] = correct_verdict
    if correct_verdict:
        score += 0.25

    # 4. Correct severity flag (15 pts)
    has_bug_flag = "bug" in [f.value for f in action.severity_flags]
    breakdown["severity_flagged"] = has_bug_flag
    if has_bug_flag:
        score += 0.15

    feedback = (
        f"Bug found: {bug_found}, Style found: {style_found}, "
        f"Verdict correct: {correct_verdict}, Flag correct: {has_bug_flag}"
    )
    return Reward(score=round(score, 4), breakdown=breakdown, feedback=feedback)


def grade_medium(action: Action) -> Reward:
    expected = TASKS["medium_security_review"]["expected_issues"]
    score = 0.0
    breakdown = {}

    # 1. SQL injection found (35 pts)
    sql_found = _comments_hit(action.review_comments, expected["security"])
    breakdown["sql_injection_found"] = sql_found
    if sql_found:
        score += 0.35

    # 2. Pagination bug found (25 pts) - expanded keywords
    bug_found = _comments_hit(action.review_comments, expected["bugs"])
    breakdown["pagination_bug_found"] = bug_found
    if bug_found:
        score += 0.25

    # 3. Correct verdict (20 pts)
    correct_verdict = action.verdict.value == expected["verdict"]
    breakdown["correct_verdict"] = correct_verdict
    if correct_verdict:
        score += 0.20

    # 4. Both required flags present (20 pts, 10 each)
    flags = [f.value for f in action.severity_flags]
    has_security = "security" in flags
    has_bug = "bug" in flags
    breakdown["security_flag"] = has_security
    breakdown["bug_flag"] = has_bug
    if has_security:
        score += 0.10
    if has_bug:
        score += 0.10

    feedback = (
        f"SQL injection: {sql_found}, Pagination bug: {bug_found}, "
        f"Verdict: {correct_verdict}, Security flag: {has_security}, Bug flag: {has_bug}"
    )
    return Reward(score=round(score, 4), breakdown=breakdown, feedback=feedback)


def grade_hard(action: Action) -> Reward:
    expected = TASKS["hard_concurrency_review"]["expected_issues"]
    score = 0.0
    breakdown = {}

    # 1. Race condition identified (30 pts)
    race_found = _comments_hit(action.review_comments, expected["bugs"])
    breakdown["race_condition_found"] = race_found
    if race_found:
        score += 0.30

    # 2. Exception swallowing identified (20 pts)
    except_found = _comments_hit(action.review_comments, expected["security"])
    breakdown["exception_handling_found"] = except_found
    if except_found:
        score += 0.20

    # 3. Misleading variable or logic issue (15 pts)
    style_found = _comments_hit(action.review_comments, expected["style"])
    logic_found = _comments_hit(action.review_comments, expected["logic"])
    breakdown["style_or_logic_found"] = style_found or logic_found
    if style_found or logic_found:
        score += 0.15

    # 4. Verdict: reject = full 20pts, request_changes = partial 10pts
    verdict_val = action.verdict.value
    if verdict_val == "reject":
        breakdown["correct_verdict"] = True
        score += 0.20
    elif verdict_val == "request_changes":
        breakdown["correct_verdict"] = "partial"
        score += 0.10
    else:
        breakdown["correct_verdict"] = False

    # 5. Required flags: bug + logic (15 pts, 7.5 each)
    flags = [f.value for f in action.severity_flags]
    has_bug = "bug" in flags
    has_logic = "logic" in flags
    breakdown["bug_flag"] = has_bug
    breakdown["logic_flag"] = has_logic
    if has_bug:
        score += 0.075
    if has_logic:
        score += 0.075

    feedback = (
        f"Race condition: {race_found}, Exception handling: {except_found}, "
        f"Style/logic: {style_found or logic_found}, Verdict: {verdict_val}, "
        f"Bug flag: {has_bug}, Logic flag: {has_logic}"
    )
    return Reward(score=round(min(score, 1.0), 4), breakdown=breakdown, feedback=feedback)


GRADERS = {
    "easy_bug_detection": grade_easy,
    "medium_security_review": grade_medium,
    "hard_concurrency_review": grade_hard,
}