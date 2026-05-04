import re

# Questions that touch sensitive aggregations — flag for human review
ESCALATION_KEYWORDS = [
    'churn rate', 'revenue forecast', 'projected', 'predict',
    'year over year', 'yoy', 'cohort', 'ltv', 'lifetime value'
]

# Patterns that suggest the question is unanswerable without more context
AMBIGUOUS_PATTERNS = [
    r'\bbest\b', r'\bworst\b', r'\btop performing\b',
    r'\bmost important\b', r'\bsignificant\b'
]

def route_question(question: str) -> dict:
    """
    Decide whether to answer autonomously or escalate for human validation.
    Returns a dict with: action, reason
    """
    q_lower = question.lower()

    # Check for escalation keywords
    for keyword in ESCALATION_KEYWORDS:
        if keyword in q_lower:
            return {
                "action": "escalate",
                "reason": f"Question involves '{keyword}' — requires human validation before surfacing to stakeholders."
            }

    # Check for ambiguous patterns
    for pattern in AMBIGUOUS_PATTERNS:
        if re.search(pattern, q_lower):
            return {
                "action": "escalate",
                "reason": "Question is ambiguous — needs clarification on what metric defines 'best/worst/top'."
            }

    return {
        "action": "answer",
        "reason": "Question is concrete and answerable from available schema."
    }

def ask_and_route(question, ask_and_run_fn, use_context=True):
    """Route first, then run if appropriate."""
    routing = route_question(question)

    print(f"\n🔀 Router decision: {routing['action'].upper()}")
    print(f"   Reason: {routing['reason']}")

    if routing['action'] == 'escalate':
        print("   ⏸️  Skipping Claude call — flagged for human review.")
        return None, None, "escalated"

    return ask_and_run_fn(question, use_context=use_context)