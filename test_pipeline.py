from claude_runner import ask_and_run
from router import ask_and_route

test_questions = [
    # Should answer autonomously
    "How many active customers do we have?",
    "What is the MRR broken down by plan?",
    "Which industry has the most customers?",
    "How many invoices were refunds?",

    # Should escalate
    "What is our churn rate trend year over year?",
    "Which customers are the best performers?",
    "Can you predict next month's revenue?",
]

print("=" * 60)
print("PIPELINE TEST — ROUTING + NL-TO-SQL")
print("=" * 60)

results = []
for q in test_questions:
    sql, result, error = ask_and_route(q, ask_and_run, use_context=True)
    results.append({
        "question": q,
        "status": "escalated" if error == "escalated" else ("error" if error else "success"),
        "sql": sql
    })

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
for r in results:
    icon = "⏸️ " if r['status'] == 'escalated' else ("✅" if r['status'] == 'success' else "❌")
    print(f"{icon} [{r['status'].upper():10}] {r['question']}")