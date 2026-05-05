# AI Analytics Eval Engine
### NL-to-SQL Accuracy Evaluator with Context Layer

**40% → 100% accuracy lift from a structured business context layer — measured across 20 test cases.**

🔗 [Live Demo](https://ai-analytics-nl-sql-hgacyhvjk7mokurb4lhzhf.streamlit.app)

---

## What This Is

A working proof-of-concept for the core problem in AI-powered analytics: **LLMs generate confident SQL that is often wrong — unless they have precise business context.**

This project builds the full stack:
- A structured **business glossary** (the context layer) with metric definitions, column descriptions, and table relationships
- A **NL-to-SQL pipeline** powered by Claude that injects context into every prompt
- A **query router** that decides when to answer autonomously vs. escalate for human review
- An **evaluation framework** with 20 predefined test cases and ground truth answers
- An **automated insight engine** that proactively surfaces anomalies and patterns
- A **Streamlit dashboard** that ties it all together

---

## The Result

| | Without Context | With Context |
|---|---|---|
| **Overall accuracy** | 40% | 100% |
| **Aggregation** | 60% | 100% |
| **Revenue** | 20% | 100% |
| **Filtering** | 20% | 100% |
| **Joins** | 60% | 100% |

Without context, Claude hallucinated column names like `amount_paid`, `plan_name`, `billing_reason`, and `employees` — none of which exist in the schema. With context, every query was correct across all 20 cases.

---

## Why This Matters

This is the exact problem an AI Analytics Engineer at a SaaS company has to solve. The bottleneck isn't the LLM — it's the **context layer**. Without structured business definitions:
- AI tools answer confidently but incorrectly
- Stakeholders lose trust and revert to manual requests
- Analysts become the bottleneck again

This project demonstrates that a well-designed context layer — business glossaries, metric definitions, column semantics — is the difference between a trustworthy AI analytics tool and a broken one.

---

## Dataset

Synthetic SaaS dataset generated with realistic business economics:

| Table | Rows | Description |
|---|---|---|
| `customers` | 200 | Company accounts with plan, industry, employee count |
| `subscriptions` | 200 | MRR, status (active/churned), start/end dates |
| `invoices` | 1,833 | Payments and refunds with `amt` and `type` columns |
| `events` | 8,035 | Product usage events per customer |

Key design choices:
- Column names are intentionally ambiguous (`amt` not `revenue`, `type` not `is_refund`) to stress-test the context layer
- 25% churn rate, realistic MRR distribution across starter/growth/enterprise plans
- Enterprise drives 78.2% of MRR — mirrors real SaaS revenue concentration

---

## Architecture

```
User Question
     │
     ▼
┌─────────────┐
│   Router    │  ── escalate if ambiguous/risky
└─────────────┘
     │ answer
     ▼
┌─────────────────────────────┐
│     Context Layer           │
│  glossary.yaml → prompt     │
└─────────────────────────────┘
     │
     ▼
┌─────────────┐
│   Claude    │  claude-sonnet-4-5
│  (NL→SQL)   │
└─────────────┘
     │
     ▼
┌─────────────┐
│   SQLite    │  execute + return dataframe
└─────────────┘
     │
     ▼
┌─────────────┐
│  Evaluator  │  compare vs ground truth → pass/fail
└─────────────┘
     │
     ▼
┌─────────────┐
│   Logger    │  query_log.jsonl → usage patterns
└─────────────┘
```

---

## Project Structure

```
ai-analytics-eval/
├── app.py                  # Streamlit dashboard (4 views)
├── claude_runner.py        # Claude API caller + SQL executor + logger
├── context_layer.py        # Glossary loader + prompt builder
├── router.py               # Question router (answer vs escalate)
├── eval_engine.py          # Eval loop + scoring + accuracy metrics
├── insight_engine.py       # Automated anomaly + pattern detection
├── test_cases.py           # 20 test cases with ground truth
├── run_eval.py             # Full eval runner (with + without context)
├── generate_data.py        # Synthetic dataset generator
├── glossary.yaml           # Business context layer
├── data/
│   ├── saas.db             # SQLite database
│   ├── query_log.jsonl     # Per-run logs
│   ├── insights_log.jsonl  # Insight scan history
│   ├── eval_with_context.csv
│   └── eval_without_context.csv
└── requirements.txt
```

---

## Key Components

### 1. Business Glossary (`glossary.yaml`)
Structured definitions for every table, column, and metric. Written to be interpreted by both humans and LLMs. Example:

```yaml
metrics:
  MRR: Sum of mrr from subscriptions WHERE status = 'active'. Never use invoices.amt for MRR.
  Net Revenue: Sum of amt from invoices WHERE type = 'payment', minus sum WHERE type = 'refund'.
  Churn Rate: Count of customers WHERE status = 'churned' divided by total customers.
```

### 2. Query Router (`router.py`)
Intercepts questions before hitting Claude. Escalates if the question involves forecasting, ambiguous superlatives, or metrics requiring human validation. Designed to mirror when AI should answer autonomously vs. defer to an analyst.

### 3. Evaluation Framework (`eval_engine.py`)
20 test cases across 4 categories with three validation types:
- `single_value` — exact numeric match
- `row_count` — correct number of rows returned
- `non_empty` — query returns results (for open-ended questions)

### 4. Automated Insight Engine (`insight_engine.py`)
Runs unprompted scans across the dataset and surfaces:
- **Anomalies** — industries with churn rate 30%+ above average
- **Risks** — revenue concentration above 75% in a single plan
- **Patterns** — engagement gaps across plan tiers

Each insight includes a Claude-generated plain-English narrative for non-technical stakeholders.

---

## Insights Detected (Sample Run)

**🚨 Churn Anomaly:** Healthcare customers churn at 32.4% vs 23.5% average — 9pp above baseline. Recommended: exit interviews + specialized onboarding for healthcare vertical.

**⚠️ Revenue Concentration Risk:** Enterprise plan drives 78.2% of MRR. A single enterprise churn event materially impacts revenue. Recommended: accelerate mid-market acquisition.

**📊 Engagement Gap:** Enterprise users average 43.1 events/user vs Growth at 38.0. Recommended: identify which enterprise features drive engagement and expose selectively to Growth tier.

---

## How to Run Locally

```bash
# Clone and install
git clone <your-repo-url>
cd ai-analytics-eval
pip install -r requirements.txt

# Add your API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Generate the dataset
python generate_data.py

# Run the full eval (40 Claude calls, ~3 mins)
python run_eval.py

# Run the insight scanner
python insight_engine.py

# Launch the dashboard
streamlit run app.py
```

---

## Stack

- **LLM:** Claude Sonnet 4.5 via Anthropic API
- **Database:** SQLite (local), structured like a Snowflake/dbt warehouse
- **Data modeling:** dbt-style layer conventions (staging → marts)
- **Eval framework:** Custom Python, ground truth test cases
- **Dashboard:** Streamlit + Plotly
- **Context layer:** YAML-based business glossary

---

## What I'd Build Next

- **dbt integration** — pull metric definitions directly from dbt model YAML docs instead of maintaining a separate glossary
- **Query log analysis** — mine `query_log.jsonl` to find recurring questions with no context coverage → auto-suggest new glossary entries
- **Slack integration** — push automated insights to the right channel based on severity and topic
- **Multi-model eval** — benchmark context layer impact across Claude, GPT-4o, and Gemini
- **Feedback loop UI** — let stakeholders thumbs-up/down results to improve context definitions over time
