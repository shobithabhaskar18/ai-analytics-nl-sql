import yaml

def load_glossary(path='glossary.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def build_context_string(glossary):
    """Convert glossary YAML into a structured string Claude can interpret."""
    lines = []
    lines.append("=== DATABASE SCHEMA & BUSINESS CONTEXT ===\n")

    for table, meta in glossary['tables'].items():
        lines.append(f"TABLE: {table}")
        lines.append(f"  Description: {meta['description']}")
        lines.append(f"  Columns:")
        for col, desc in meta['columns'].items():
            lines.append(f"    - {col}: {desc}")
        lines.append("")

    lines.append("=== METRIC DEFINITIONS ===")
    for metric, definition in glossary['metrics'].items():
        lines.append(f"  - {metric}: {definition}")

    return "\n".join(lines)

def build_prompt(question, use_context=True, glossary_path='glossary.yaml'):
    """
    Build a Claude prompt for NL-to-SQL.
    use_context=True injects the glossary. use_context=False is the baseline (no context).
    """
    glossary = load_glossary(glossary_path)
    context = build_context_string(glossary)

    if use_context:
        system_prompt = f"""You are an expert SQL analyst. 
A user will ask a business question. Your job is to return a single valid SQLite SQL query that answers it.

Use the following business context to write accurate SQL:

{context}

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no backticks.
- Use exact table and column names from the schema above.
- Apply metric definitions exactly as specified.
"""
    else:
        system_prompt = """You are an expert SQL analyst.
A user will ask a business question. Your job is to return a single valid SQLite SQL query that answers it.

The database has these tables: customers, subscriptions, invoices, events.

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no backticks.
- Use exact table and column names.
"""

    return system_prompt, question