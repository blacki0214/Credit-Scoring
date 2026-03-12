"""
Generate fake loan application data for testing the retraining pipeline
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate 1000 fake loan applications
print("Generating 1000 fake loan applications...")
np.random.seed(42)

# Generate timestamps over the past 3 months
base_date = datetime.now() - timedelta(days=90)
timestamps = [base_date + timedelta(hours=np.random.randint(0, 90*24)) for _ in range(1000)]

data = {
    'application_id': [f'app_{i:05d}' for i in range(1000)],
    'user_id': [f'user_{i:04d}' for i in range(1000)],
    'timestamp': timestamps,
    
    # Input features
    'age': np.random.randint(20, 70, 1000),
    'monthly_income': np.random.randint(5000000, 100000000, 1000),  # 5M - 100M VND
    'employment_status': np.random.choice(['EMPLOYED', 'SELF_EMPLOYED', 'UNEMPLOYED'], 1000, p=[0.7, 0.2, 0.1]),
    'years_employed': np.random.uniform(0, 30, 1000),
    'home_ownership': np.random.choice(['RENT', 'OWN', 'MORTGAGE', 'LIVING_WITH_PARENTS'], 1000, p=[0.3, 0.3, 0.2, 0.2]),
    'loan_purpose': np.random.choice(['HOME', 'CAR', 'BUSINESS', 'EDUCATION', 'PERSONAL'], 1000, p=[0.15, 0.25, 0.2, 0.15, 0.25]),
    'years_credit_history': np.random.uniform(0, 20, 1000),
    'has_previous_defaults': np.random.choice([True, False], 1000, p=[0.1, 0.9]),
    'currently_defaulting': np.random.choice([True, False], 1000, p=[0.05, 0.95]),
    
    # Model outputs (simulated from previous model)
    'credit_score': np.random.randint(300, 850, 1000),
    'approved_limit': np.random.randint(10000000, 500000000, 1000),
    'risk_level': np.random.choice(['LOW', 'MEDIUM', 'HIGH'], 1000, p=[0.4, 0.4, 0.2]),
    'approved': np.random.choice([True, False], 1000, p=[0.7, 0.3]),
    'interest_rate': np.random.uniform(8.0, 24.0, 1000),
    'loan_term_months': np.random.choice([12, 24, 36, 48, 60], 1000),
    
    # Ground truth (not available yet in real scenario)
    'actual_default': None,
    'loan_outcome_date': None
}

df = pd.DataFrame(data)

# Round numeric values
df['years_employed'] = df['years_employed'].round(1)
df['years_credit_history'] = df['years_credit_history'].round(1)
df['interest_rate'] = df['interest_rate'].round(2)

# Save to parquet
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'loan_applications_{timestamp}.parquet'
df.to_parquet(filename, index=False)

print(f"✓ Created {filename}")
print(f"  - Total records: {len(df)}")
print(f"  - Approved: {df['approved'].sum()} ({df['approved'].mean()*100:.1f}%)")
print(f"  - Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"\nFile ready to upload to GCS!")
