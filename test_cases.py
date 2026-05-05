TEST_CASES = [
    # --- AGGREGATION (5 questions) ---
    {
        "id": "AGG_01",
        "category": "aggregation",
        "question": "How many active customers do we have?",
        "ground_truth": 153,
        "validation": "single_value"
    },
    {
        "id": "AGG_02",
        "category": "aggregation",
        "question": "How many invoices were refunds?",
        "ground_truth": 81,
        "validation": "single_value"
    },
    {
        "id": "AGG_03",
        "category": "aggregation",
        "question": "What is the total number of customers?",
        "ground_truth": 200,
        "validation": "single_value"
    },
    {
        "id": "AGG_04",
        "category": "aggregation",
        "question": "How many churned customers do we have?",
        "ground_truth": 47,
        "validation": "single_value"
    },
    {
        "id": "AGG_05",
        "category": "aggregation",
        "question": "How many total product events are in the database?",
        "ground_truth": 8035,
        "validation": "single_value"
    },

    # --- REVENUE (5 questions) ---
    {
        "id": "REV_01",
        "category": "revenue",
        "question": "What is the total net revenue excluding refunds?",
        "ground_truth": 586098,
        "validation": "single_value"
    },
    {
        "id": "REV_02",
        "category": "revenue",
        "question": "What is the total MRR across all active subscriptions?",
        "ground_truth": 54147,
        "validation": "single_value"
    },
    {
        "id": "REV_03",
        "category": "revenue",
        "question": "What is the MRR for enterprise plan customers only?",
        "ground_truth": 42347,
        "validation": "single_value"
    },
    {
        "id": "REV_04",
        "category": "revenue",
        "question": "What is the total amount lost to refunds?",
        "ground_truth": None,
        "validation": "non_empty"  # just check refund count, amt varies
    },
    {
        "id": "REV_05",
        "category": "revenue",
        "question": "How many payment invoices exist?",
        "ground_truth": 1752,
        "validation": "single_value"
    },

    # --- FILTERING (5 questions) ---
    {
        "id": "FIL_01",
        "category": "filtering",
        "question": "How many customers are on the starter plan?",
        "ground_truth": None,
        "validation": "non_empty"
    },
    {
        "id": "FIL_02",
        "category": "filtering",
        "question": "How many customers work in the fintech industry?",
        "ground_truth": None,
        "validation": "non_empty"
    },
    {
        "id": "FIL_03",
        "category": "filtering",
        "question": "List all churned customers and their plan type.",
        "ground_truth": 47,
        "validation": "row_count"
    },
    {
        "id": "FIL_04",
        "category": "filtering",
        "question": "Which customers have more than 500 employees?",
        "ground_truth": None,
        "validation": "non_empty"
    },
    {
        "id": "FIL_05",
        "category": "filtering",
        "question": "How many active enterprise customers do we have?",
        "ground_truth": None,
        "validation": "non_empty"
    },

    # --- JOINS (5 questions) ---
    {
        "id": "JOI_01",
        "category": "joins",
        "question": "What is the MRR broken down by plan?",
        "ground_truth": 3,  # 3 plans = 3 rows
        "validation": "row_count"
    },
    {
        "id": "JOI_02",
        "category": "joins",
        "question": "Which industry has the most customers?",
        "ground_truth": 1,
        "validation": "row_count"
    },
    {
        "id": "JOI_03",
        "category": "joins",
        "question": "How many events has each customer triggered on average?",
        "ground_truth": None,
        "validation": "non_empty"
    },
    {
        "id": "JOI_04",
        "category": "joins",
        "question": "What is the total revenue generated per plan type?",
        "ground_truth": 3,
        "validation": "row_count"
    },
    {
        "id": "JOI_05",
        "category": "joins",
        "question": "How many customers have never triggered any product event?",
        "ground_truth": None,
        "validation": "non_empty"
    },
]