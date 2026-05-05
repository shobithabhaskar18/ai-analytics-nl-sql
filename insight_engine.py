import sqlite3
import pandas as pd
from claude_runner import ask_claude
from datetime import datetime
import json

DB_PATH = 'data/saas.db'

def get_db():
    return sqlite3.connect(DB_PATH)

# ─────────────────────────────────────────
# DATA FETCHERS
# ─────────────────────────────────────────

def fetch_mrr_by_plan():
    conn = get_db()
    df = pd.read_sql("""
        SELECT plan, SUM(mrr) as total_mrr, COUNT(*) as customer_count
        FROM subscriptions
        WHERE status = 'active'
        GROUP BY plan
    """, conn)
    conn.close()
    return df

def fetch_churn_by_industry():
    conn = get_db()
    df = pd.read_sql("""
        SELECT c.industry,
               COUNT(*) as total_customers,
               SUM(CASE WHEN s.status = 'churned' THEN 1 ELSE 0 END) as churned,
               ROUND(100.0 * SUM(CASE WHEN s.status = 'churned' THEN 1 ELSE 0 END) / COUNT(*), 1) as churn_rate_pct
        FROM customers c
        JOIN subscriptions s ON c.customer_id = s.customer_id
        GROUP BY c.industry
        ORDER BY churn_rate_pct DESC
    """, conn)
    conn.close()
    return df

def fetch_refund_rate():
    conn = get_db()
    df = pd.read_sql("""
        SELECT
            type,
            COUNT(*) as count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) as pct
        FROM invoices
        GROUP BY type
    """, conn)
    conn.close()
    return df

def fetch_event_activity_by_plan():
    conn = get_db()
    df = pd.read_sql("""
        SELECT s.plan,
               COUNT(e.event_id) as total_events,
               COUNT(DISTINCT e.customer_id) as active_users,
               ROUND(1.0 * COUNT(e.event_id) / COUNT(DISTINCT e.customer_id), 1) as events_per_user
        FROM events e
        JOIN subscriptions s ON e.customer_id = s.customer_id
        WHERE s.status = 'active'
        GROUP BY s.plan
        ORDER BY events_per_user DESC
    """, conn)
    conn.close()
    return df

def fetch_revenue_concentration():
    conn = get_db()
    df = pd.read_sql("""
        SELECT c.plan,
               ROUND(100.0 * SUM(s.mrr) / (SELECT SUM(mrr) FROM subscriptions WHERE status='active'), 1) as mrr_share_pct
        FROM subscriptions s
        JOIN customers c ON s.customer_id = c.customer_id
        WHERE s.status = 'active'
        GROUP BY c.plan
        ORDER BY mrr_share_pct DESC
    """, conn)
    conn.close()
    return df

# ─────────────────────────────────────────
# ANOMALY DETECTORS
# ─────────────────────────────────────────

def detect_churn_anomaly(df_churn):
    """Flag industries with churn rate significantly above average."""
    avg_churn = df_churn['churn_rate_pct'].mean()
    threshold = avg_churn * 1.3  # 30% above average = anomaly
    anomalies = df_churn[df_churn['churn_rate_pct'] > threshold]
    return anomalies, avg_churn

def detect_refund_anomaly(df_refunds):
    """Flag if refund rate exceeds 6%."""
    refund_row = df_refunds[df_refunds['type'] == 'refund']
    if refund_row.empty:
        return False, 0
    refund_pct = refund_row.iloc[0]['pct']
    return refund_pct > 6.0, refund_pct

def detect_revenue_concentration(df_concentration):
    """Flag if one plan drives more than 75% of MRR — concentration risk."""
    top = df_concentration.iloc[0]
    return top['mrr_share_pct'] > 75, top

# ─────────────────────────────────────────
# CLAUDE NARRATIVE GENERATOR
# ─────────────────────────────────────────

def generate_narrative(insight_type, data_summary):
    """Ask Claude to turn raw numbers into a plain-english insight for a stakeholder."""
    system_prompt = """You are a senior data analyst writing a brief insight for a business stakeholder.
Your job: turn the data summary into 2-3 sentences of plain English that a non-technical leader can act on.
Be specific with numbers. End with one recommended action.
No bullet points. No headers. Just clear prose."""

    user_message = f"""
Insight type: {insight_type}
Data summary: {data_summary}

Write the stakeholder insight now.
"""
    response_text = ask_claude(user_message, use_context=False)
    # Override — we're passing custom system prompt directly
    import anthropic
    from dotenv import load_dotenv
    load_dotenv()
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text.strip()

# ─────────────────────────────────────────
# INSIGHT RUNNER
# ─────────────────────────────────────────

def run_insights(verbose=True):
    """Run all insight checks and return flagged insights."""
    insights = []
    timestamp = datetime.now().isoformat()

    if verbose:
        print("\n" + "="*60)
        print("AUTOMATED INSIGHT SCAN")
        print("="*60)

    # ── Insight 1: Churn anomaly by industry ──
    df_churn = fetch_churn_by_industry()
    anomalies, avg_churn = detect_churn_anomaly(df_churn)

    if not anomalies.empty:
        summary = f"Average churn rate: {round(avg_churn, 1)}%. High-churn industries: " + \
                  ", ".join([f"{r['industry']} ({r['churn_rate_pct']}%)" for _, r in anomalies.iterrows()])
        narrative = generate_narrative("Churn anomaly by industry", summary)
        insights.append({
            "type": "anomaly",
            "title": "High churn detected in specific industries",
            "summary": summary,
            "narrative": narrative,
            "severity": "high",
            "timestamp": timestamp
        })
        if verbose:
            print(f"\n🚨 ANOMALY: High churn industries detected")
            print(f"   {summary}")
            print(f"\n   📢 Stakeholder insight:")
            print(f"   {narrative}")

    # ── Insight 2: Refund rate ──
    df_refunds = fetch_refund_rate()
    is_high, refund_pct = detect_refund_anomaly(df_refunds)

    status_icon = "🚨" if is_high else "✅"
    status_label = "ANOMALY" if is_high else "NORMAL"
    summary = f"Refund rate is {refund_pct}% of all invoices."

    if verbose:
        print(f"\n{status_icon} {status_label}: Refund rate — {refund_pct}%")

    if is_high:
        narrative = generate_narrative("Elevated refund rate", summary)
        insights.append({
            "type": "anomaly",
            "title": "Refund rate above threshold",
            "summary": summary,
            "narrative": narrative,
            "severity": "medium",
            "timestamp": timestamp
        })
        if verbose:
            print(f"   📢 Stakeholder insight:\n   {narrative}")

    # ── Insight 3: Revenue concentration risk ──
    df_concentration = fetch_revenue_concentration()
    is_concentrated, top_plan = detect_revenue_concentration(df_concentration)

    summary = f"{top_plan['plan'].title()} plan drives {top_plan['mrr_share_pct']}% of total MRR."

    if is_concentrated:
        narrative = generate_narrative("Revenue concentration risk", summary)
        insights.append({
            "type": "risk",
            "title": "Revenue concentration risk",
            "summary": summary,
            "narrative": narrative,
            "severity": "medium",
            "timestamp": timestamp
        })
        if verbose:
            print(f"\n⚠️  RISK: Revenue concentration — {summary}")
            print(f"   📢 Stakeholder insight:\n   {narrative}")
    else:
        if verbose:
            print(f"\n✅ NORMAL: Revenue concentration — {summary}")

    # ── Insight 4: Product engagement by plan ──
    df_events = fetch_event_activity_by_plan()
    lowest = df_events.iloc[-1]
    highest = df_events.iloc[0]

    summary = (f"Engagement gap: {highest['plan']} customers average {highest['events_per_user']} events/user "
               f"vs {lowest['plan']} at {lowest['events_per_user']} events/user.")
    narrative = generate_narrative("Product engagement gap by plan", summary)

    insights.append({
        "type": "pattern",
        "title": "Product engagement gap across plans",
        "summary": summary,
        "narrative": narrative,
        "severity": "low",
        "timestamp": timestamp
    })

    if verbose:
        print(f"\n📊 PATTERN: Engagement gap detected")
        print(f"   {summary}")
        print(f"   📢 Stakeholder insight:\n   {narrative}")

    # ── Save all insights ──
    with open('data/insights_log.jsonl', 'a') as f:
        for insight in insights:
            f.write(json.dumps(insight) + '\n')

    if verbose:
        print(f"\n{'='*60}")
        print(f"SCAN COMPLETE — {len(insights)} insights flagged")
        print(f"💾 Saved to data/insights_log.jsonl")
        print(f"{'='*60}")

    return insights

if __name__ == "__main__":
    run_insights(verbose=True)