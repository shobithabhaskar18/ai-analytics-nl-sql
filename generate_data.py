import sqlite3
import pandas as pd
import random
from faker import Faker
from datetime import timedelta, date

fake = Faker()
random.seed(42)

# --- Generate customers ---
plans = ['starter', 'growth', 'enterprise']
plan_mrr = {'starter': 49, 'growth': 199, 'enterprise': 799}

customers = []
for i in range(1, 201):
    plan = random.choice(plans)
    signup = fake.date_between(start_date=date(2022, 1, 1), end_date=date(2024, 6, 1))
    customers.append({
        'customer_id': i,
        'company_name': fake.company(),
        'plan': plan,
        'signup_date': signup,
        'industry': random.choice(['fintech', 'healthcare', 'ecommerce', 'saas', 'media']),
        'employee_count': random.choice([10, 50, 200, 500, 1000])
    })

df_customers = pd.DataFrame(customers)

# --- Generate subscriptions ---
subscriptions = []
sub_id = 1
for c in customers:
    start = c['signup_date']
    churned = random.random() < 0.25
    end = start + timedelta(days=random.randint(60, 730)) if churned else None
    subscriptions.append({
        'subscription_id': sub_id,
        'customer_id': c['customer_id'],
        'plan': c['plan'],
        'mrr': plan_mrr[c['plan']],
        'status': 'churned' if churned else 'active',
        'start_date': start,
        'end_date': end
    })
    sub_id += 1

df_subscriptions = pd.DataFrame(subscriptions)

# --- Generate invoices ---
invoices = []
inv_id = 1
for _, sub in df_subscriptions.iterrows():
    months = random.randint(1, 18)
    for m in range(months):
        inv_date = pd.to_datetime(sub['start_date']) + pd.DateOffset(months=m)
        is_refund = random.random() < 0.05
        invoices.append({
            'invoice_id': inv_id,
            'customer_id': sub['customer_id'],
            'subscription_id': sub['subscription_id'],
            'invoice_date': inv_date.date(),
            'amt': -sub['mrr'] if is_refund else sub['mrr'],
            'type': 'refund' if is_refund else 'payment',
            'status': 'paid'
        })
        inv_id += 1

df_invoices = pd.DataFrame(invoices)

# --- Generate events ---
event_types = ['login', 'created_record', 'shared_view', 'invited_user', 'exported_data']
events = []
ev_id = 1
for c in customers:
    num_events = random.randint(5, 80)
    for _ in range(num_events):
        events.append({
            'event_id': ev_id,
            'customer_id': c['customer_id'],
            'event_type': random.choice(event_types),
            'event_date': fake.date_between(start_date=c['signup_date'], end_date=date(2024, 12, 31))
        })
        ev_id += 1

df_events = pd.DataFrame(events)

# --- Write to SQLite ---
conn = sqlite3.connect('data/saas.db')
df_customers.to_sql('customers', conn, if_exists='replace', index=False)
df_subscriptions.to_sql('subscriptions', conn, if_exists='replace', index=False)
df_invoices.to_sql('invoices', conn, if_exists='replace', index=False)
df_events.to_sql('events', conn, if_exists='replace', index=False)
conn.close()

print("✅ Database created: data/saas.db")
print(f"   customers: {len(df_customers)} rows")
print(f"   subscriptions: {len(df_subscriptions)} rows")
print(f"   invoices: {len(df_invoices)} rows")
print(f"   events: {len(df_events)} rows")
