import anthropic
import sqlite3
import pandas as pd
import json
import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from context_layer import build_prompt

load_dotenv()

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass

client = anthropic.Anthropic(api_key=api_key)

LOG_FILE = 'data/query_log.jsonl'

def log_run(question, use_context, sql, result_preview, error, duration_ms):
    """Log every pipeline run to a JSONL file for later analysis."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "use_context": use_context,
        "sql_generated": sql,
        "result_preview": result_preview,
        "error": error,
        "duration_ms": duration_ms,
        "status": "error" if error else "success"
    }
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(record) + '\n')

def ask_claude(question, use_context=True):
    """Send a question to Claude, get back a SQL query."""
    system_prompt, user_message = build_prompt(question, use_context=use_context)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    sql = response.content[0].text.strip()

    # Strip markdown if Claude wraps it anyway
    if sql.startswith("```"):
        sql = sql.split("```")[1]
        if sql.startswith("sql"):
            sql = sql[3:]
    sql = sql.strip()

    return sql

def run_sql(sql, db_path='data/saas.db'):
    """Execute SQL against SQLite and return a dataframe."""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)

def ask_and_run(question, use_context=True, verbose=True):
    """Full pipeline: question → SQL → result → log."""
    start = datetime.now()

    if verbose:
        print(f"\n Question: {question}")
        print(f"   Context: {'ON' if use_context else 'OFF'}")

    sql = ask_claude(question, use_context=use_context)

    if verbose:
        print(f"\n Generated SQL:\n{sql}")

    result, error = run_sql(sql)

    duration_ms = int((datetime.now() - start).total_seconds() * 1000)

    result_preview = None
    if result is not None:
        result_preview = result.head(3).to_dict(orient='records')
        if verbose:
            print(f"\n Result:\n{result}")
    else:
        if verbose:
            print(f"\n Error: {error}")

    log_run(question, use_context, sql, result_preview, error, duration_ms)

    return sql, result, error