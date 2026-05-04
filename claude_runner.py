import anthropic
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from context_layer import build_prompt

load_dotenv()
client = anthropic.Anthropic()

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
    return sql

def run_sql(sql, db_path='data/saas.db'):
    """Execute SQL against the SQLite database and return a dataframe."""
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)

def ask_and_run(question, use_context=True):
    """Full pipeline: question → SQL → result."""
    print(f"\n Question: {question}")
    print(f"   Context: {'ON' if use_context else 'OFF'}")

    sql = ask_claude(question, use_context=use_context)
    print(f"\n Generated SQL:\n{sql}")

    result, error = run_sql(sql)
    if error:
        print(f"\n Error: {error}")
        return sql, None
    else:
        print(f"\n Result:\n{result}")
        return sql, result
