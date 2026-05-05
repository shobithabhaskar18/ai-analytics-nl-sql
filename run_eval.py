from eval_engine import run_eval, score_results, save_results
import pandas as pd

# Run with context ON
results_with = run_eval(use_context=True, verbose=False)
df_with = score_results(results_with)

# Run with context OFF
results_without = run_eval(use_context=False, verbose=False)
df_without = score_results(results_without)

# Save both
save_results(df_with, 'data/eval_with_context.csv')
save_results(df_without, 'data/eval_without_context.csv')

# Side by side comparison
print("\n" + "="*60)
print("CONTEXT IMPACT SUMMARY")
print("="*60)

with_acc = round(len(df_with[df_with['status']=='pass']) / len(df_with) * 100, 1)
without_acc = round(len(df_without[df_without['status']=='pass']) / len(df_without) * 100, 1)
lift = round(with_acc - without_acc, 1)

print(f"\n  Without context:  {without_acc}%")
print(f"  With context:     {with_acc}%")
print(f"  Accuracy lift:    +{lift} percentage points")
print(f"\n  {'🟢 Context layer is working.' if lift > 0 else '🔴 Review context definitions.'}")