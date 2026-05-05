import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from claude_runner import ask_and_run
from router import ask_and_route
from eval_engine import run_eval, score_results
from insight_engine import run_insights
from test_cases import TEST_CASES

st.set_page_config(
    page_title="AI Analytics Eval Engine",
    page_icon="🧠",
    layout="wide"
)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────

st.sidebar.title("🧠 AI Analytics Engine")
st.sidebar.markdown("*Built to show context layer impact on NL-to-SQL accuracy*")
page = st.sidebar.radio(
    "Navigate",
    ["💬 Ask a Question", "📊 Eval Scorecard", "🚨 Insight Scanner", "📖 Glossary"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Project:** NL-to-SQL Accuracy Evaluator")
st.sidebar.markdown("**Dataset:** 200 SaaS customers, 1,833 invoices, 8,035 events")
st.sidebar.markdown("**Model:** Claude Sonnet 4.5")

# ─────────────────────────────────────────
# PAGE 1: ASK A QUESTION
# ─────────────────────────────────────────

if page == "💬 Ask a Question":
    st.title("💬 Ask a Business Question")
    st.markdown("Type a natural language question. The router decides whether to answer or escalate. Toggle context to see the difference.")

    col1, col2 = st.columns([3, 1])
    with col1:
        question = st.text_input(
            "Your question",
            placeholder="e.g. What is the MRR broken down by plan?"
        )
    with col2:
        use_context = st.toggle("Context Layer ON", value=True)

    if st.button("Run", type="primary") and question:
        with st.spinner("Routing and running..."):
            from router import route_question
            routing = route_question(question)

            if routing["action"] == "escalate":
                st.warning(f"⏸️ **Escalated — not answered autonomously**")
                st.info(f"Reason: {routing['reason']}")
            else:
                st.success(f"✅ **Routed to: Answer autonomously**")
                sql, result, error = ask_and_run(
                    question,
                    use_context=use_context,
                    verbose=False
                )

                col_sql, col_result = st.columns(2)
                with col_sql:
                    st.markdown("**Generated SQL**")
                    st.code(sql, language="sql")
                with col_result:
                    st.markdown("**Result**")
                    if error:
                        st.error(f"Error: {error}")
                    elif result is not None:
                        st.dataframe(result, use_container_width=True)

    st.markdown("---")
    st.markdown("**Try these:**")
    examples = [
        "How many active customers do we have?",
        "What is the MRR broken down by plan?",
        "Which industry has the highest churn rate?",
        "What is our churn rate trend year over year?",
    ]
    for ex in examples:
        st.markdown(f"- *{ex}*")

# ─────────────────────────────────────────
# PAGE 2: EVAL SCORECARD
# ─────────────────────────────────────────

elif page == "📊 Eval Scorecard":
    st.title("📊 Eval Scorecard")
    st.markdown("Accuracy of NL-to-SQL across 20 test cases — with and without the context layer.")

    # Load saved results if available
    try:
        df_with = pd.read_csv('data/eval_with_context.csv')
        df_without = pd.read_csv('data/eval_without_context.csv')
        data_loaded = True
    except:
        data_loaded = False

    if not data_loaded:
        st.warning("No eval results found. Run `python run_eval.py` first, or click below.")
        if st.button("Run Eval Now (takes ~3 mins)"):
            with st.spinner("Running 40 eval cases..."):
                results_with = run_eval(use_context=True, verbose=False)
                df_with = score_results(results_with)
                results_without = run_eval(use_context=False, verbose=False)
                df_without = score_results(results_without)
                df_with.to_csv('data/eval_with_context.csv', index=False)
                df_without.to_csv('data/eval_without_context.csv', index=False)
                st.rerun()
    else:
        # Top metrics
        with_acc = round(len(df_with[df_with['status'] == 'pass']) / len(df_with) * 100, 1)
        without_acc = round(len(df_without[df_without['status'] == 'pass']) / len(df_without) * 100, 1)
        lift = round(with_acc - without_acc, 1)

        col1, col2, col3 = st.columns(3)
        col1.metric("Without Context", f"{without_acc}%", help="Baseline accuracy")
        col2.metric("With Context", f"{with_acc}%", f"+{lift}pp lift")
        col3.metric("Accuracy Lift", f"+{lift}pp", "from context layer")

        st.markdown("---")

        # Accuracy by category chart
        st.subheader("Accuracy by Question Category")

        categories = df_with['category'].unique()
        cat_data = []
        for cat in categories:
            w = df_with[df_with['category'] == cat]
            wo = df_without[df_without['category'] == cat]
            cat_data.append({
                "Category": cat.title(),
                "With Context": round(len(w[w['status'] == 'pass']) / len(w) * 100),
                "Without Context": round(len(wo[wo['status'] == 'pass']) / len(wo) * 100)
            })

        df_chart = pd.DataFrame(cat_data)
        fig = go.Figure()
        fig.add_bar(name="Without Context", x=df_chart["Category"], y=df_chart["Without Context"],
                    marker_color="#ef4444")
        fig.add_bar(name="With Context", x=df_chart["Category"], y=df_chart["With Context"],
                    marker_color="#22c55e")
        fig.update_layout(
            barmode='group',
            yaxis_title="Accuracy %",
            yaxis_range=[0, 110],
            legend=dict(orientation="h", y=1.1),
            height=350,
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Test case detail table
        st.subheader("Test Case Results")
        col_with, col_without = st.columns(2)

        def render_results(df, label):
            st.markdown(f"**{label}**")
            for _, row in df.iterrows():
                icon = "✅" if row['status'] == 'pass' else "❌"
                st.markdown(f"{icon} `{row['id']}` {row['question'][:50]}...")

        with col_with:
            render_results(df_with, "With Context")
        with col_without:
            render_results(df_without, "Without Context")

# ─────────────────────────────────────────
# PAGE 3: INSIGHT SCANNER
# ─────────────────────────────────────────

elif page == "🚨 Insight Scanner":
    st.title("🚨 Automated Insight Scanner")
    st.markdown("Proactively surfaces anomalies, risks, and patterns — without being asked.")

    # Load existing insights
    insights = []
    try:
        with open('data/insights_log.jsonl', 'r') as f:
            lines = f.readlines()
            # Get last run (last N insights by timestamp)
            all_insights = [json.loads(l) for l in lines]
            if all_insights:
                last_ts = all_insights[-1]['timestamp']
                insights = [i for i in all_insights if i['timestamp'] == last_ts]
    except:
        pass

    if not insights:
        st.info("No insights found. Run a scan.")

    if st.button("🔍 Run Insight Scan", type="primary"):
        with st.spinner("Scanning data for anomalies and patterns..."):
            insights = run_insights(verbose=False)
            st.rerun()

    severity_colors = {"high": "🔴", "medium": "🟡", "low": "🔵"}
    type_icons = {"anomaly": "🚨", "risk": "⚠️", "pattern": "📊"}

    for insight in insights:
        icon = type_icons.get(insight['type'], "📌")
        sev = severity_colors.get(insight['severity'], "⚪")

        with st.expander(f"{icon} {sev} {insight['title']}", expanded=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("**Raw Data**")
                st.info(insight['summary'])
                st.markdown(f"**Type:** `{insight['type']}`")
                st.markdown(f"**Severity:** `{insight['severity']}`")
            with col2:
                st.markdown("**📢 Stakeholder Insight**")
                st.success(insight['narrative'])

    # MRR chart
    st.markdown("---")
    st.subheader("MRR by Plan")
    conn = sqlite3.connect('data/saas.db')
    df_mrr = pd.read_sql("""
        SELECT plan, SUM(mrr) as total_mrr
        FROM subscriptions WHERE status='active'
        GROUP BY plan ORDER BY total_mrr DESC
    """, conn)
    conn.close()
    fig = px.pie(df_mrr, values='total_mrr', names='plan',
                 color_discrete_sequence=["#6366f1", "#22c55e", "#f59e0b"])
    fig.update_layout(height=300, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────
# PAGE 4: GLOSSARY
# ─────────────────────────────────────────

elif page == "📖 Glossary":
    st.title("📖 Business Glossary")
    st.markdown("The context layer — structured definitions injected into every Claude prompt.")

    import yaml
    with open('glossary.yaml', 'r') as f:
        glossary = yaml.safe_load(f)

    st.subheader("Tables & Columns")
    for table, meta in glossary['tables'].items():
        with st.expander(f"**{table}**  —  {meta['description']}", expanded=False):
            for col, desc in meta['columns'].items():
                st.markdown(f"- **`{col}`** — {desc}")

    st.markdown("---")
    st.subheader("Metric Definitions")
    for metric, definition in glossary['metrics'].items():
        st.markdown(f"**{metric}**")
        st.code(definition, language=None)

    st.markdown("---")
    st.info("💡 These definitions are what drive the 100% vs 40% accuracy gap. "
            "Without them, Claude hallucinates column names and applies wrong metric logic.")