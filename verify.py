import sqlite3
import pandas as pd

conn = sqlite3.connect('data/saas.db')

for table in ['customers', 'subscriptions', 'invoices', 'events']:
    df = pd.read_sql(f"SELECT * FROM {table} LIMIT 3", conn)
    print(f"\n--- {table} ---")
    print(df)

conn.close()