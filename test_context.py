from claude_runner import ask_and_run

question = "What is the total net revenue, excluding refunds?"

print("=" * 60)
print("RUN 1: WITH CONTEXT")
print("=" * 60)
sql_with, result_with = ask_and_run(question, use_context=True)

print("\n" + "=" * 60)
print("RUN 2: WITHOUT CONTEXT")
print("=" * 60)
sql_without, result_without = ask_and_run(question, use_context=False)

print("\n" + "=" * 60)
print("COMPARISON")
print("=" * 60)
print(f"\nWith context result:    {result_with.iloc[0,0] if result_with is not None else 'ERROR'}")
print(f"Without context result: {result_without.iloc[0,0] if result_without is not None else 'ERROR'}")
