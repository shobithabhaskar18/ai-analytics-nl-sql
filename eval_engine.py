import pandas as pd
from claude_runner import ask_and_run
from test_cases import TEST_CASES
from datetime import datetime
import json

def evaluate_result(result, error, test_case):
    """
    Score a pipeline result against the ground truth.
    Returns: pass, fail, or error
    """
    if error:
        return "fail", f"SQL error: {error}"

    if result is None or result.empty:
        return "fail", "Query returned no results"

    validation = test_case["validation"]
    ground_truth = test_case["ground_truth"]

    if validation == "single_value":
        actual = result.iloc[0, 0]
        try:
            actual_num = float(actual)
            expected_num = float(ground_truth)
            if actual_num == expected_num:
                return "pass", f"✅ exact match: {actual_num}"
            else:
                return "fail", f"Expected {expected_num}, got {actual_num}"
        except:
            return "fail", f"Could not compare values: {actual} vs {ground_truth}"

    elif validation == "row_count":
        actual_rows = len(result)
        if actual_rows == ground_truth:
            return "pass", f"✅ correct row count: {actual_rows}"
        else:
            return "fail", f"Expected {ground_truth} rows, got {actual_rows}"

    elif validation == "non_empty":
        return "pass", f"✅ returned {len(result)} rows (non-empty check)"

    return "fail", "Unknown validation type"

def run_eval(use_context=True, verbose=False):
    """Run all test cases and return scored results."""
    label = "WITH CONTEXT" if use_context else "WITHOUT CONTEXT"
    print(f"\n{'='*60}")
    print(f"EVAL RUN: {label}")
    print(f"{'='*60}")

    results = []
    for tc in TEST_CASES:
        sql, result, error = ask_and_run(
            tc["question"],
            use_context=use_context,
            verbose=verbose
        )
        status, reason = evaluate_result(result, error, tc)

        results.append({
            "id": tc["id"],
            "category": tc["category"],
            "question": tc["question"],
            "use_context": use_context,
            "status": status,
            "reason": reason,
            "sql": sql
        })

        icon = "✅" if status == "pass" else "❌"
        print(f"{icon} [{tc['id']}] {tc['question'][:55]}")
        if status == "fail":
            print(f"      → {reason}")

    return results

def score_results(results):
    """Calculate accuracy scores by category."""
    df = pd.DataFrame(results)
    total = len(df)
    passed = len(df[df['status'] == 'pass'])

    print(f"\n{'='*60}")
    print(f"OVERALL ACCURACY: {passed}/{total} = {round(passed/total*100, 1)}%")
    print(f"{'='*60}")

    print("\nBy category:")
    for cat in df['category'].unique():
        cat_df = df[df['category'] == cat]
        cat_pass = len(cat_df[cat_df['status'] == 'pass'])
        cat_total = len(cat_df)
        print(f"  {cat:15} {cat_pass}/{cat_total} = {round(cat_pass/cat_total*100)}%")

    return df

def save_results(df, filename):
    df.to_csv(filename, index=False)
    print(f"\n💾 Results saved to {filename}")