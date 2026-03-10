import pandas as pd
import numpy as np
import pickle
import os
import sys

# Optional termcolor for better CLI experience, fallback to no-color if not installed
try:
    from termcolor import colored
except ImportError:
    def colored(text, color=None, on_color=None, attrs=None):
        return text

# Configure paths
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'alternative_model', 'best_model_xgboost.pkl')
FEATURE_COLS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'alternative_model', 'feature_cols.pkl')

print(colored("=======================================", "cyan"))
print(colored("   Student Loan Risk Prediction CLI    ", "cyan", attrs=["bold"]))
print(colored("=======================================\n", "cyan"))

if not os.path.exists(MODEL_PATH) or not os.path.exists(FEATURE_COLS_PATH):
    print(colored("Error: Model or feature list not found. Please train the model first.", "red"))
    sys.exit(1)

with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)
with open(FEATURE_COLS_PATH, 'rb') as f:
    feature_cols = pickle.load(f)

# Hardcode ordinal encoding maps for categorical features as established in feature engineering
program_map    = {'college': 0, 'university': 1}
living_map     = {'family': 0, 'dorm': 1, 'rent': 2}
potential_map  = {'low': 0, 'medium': 1, 'high': 2}

def get_input(prompt, cast_type=float, default=None, choices=None):
    prompt_str = f"{prompt}"
    if default is not None:
        prompt_str += f" [default: {default}]"
    prompt_str += ": "
    
    while True:
        try:
            val = input(prompt_str).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            sys.exit(0)
            
        if not val and default is not None:
            return cast_type(default)
            
        # For strings keep choices as string list/dict
        if choices and cast_type == str and val not in choices:
            allowed = list(choices.keys()) if isinstance(choices, dict) else choices
            print(colored(f"  -> Please choose from {allowed}", "yellow"))
            continue
            
        try:
            parsed_val = cast_type(val)
            if choices and cast_type != str and parsed_val not in choices:
                allowed = list(choices.keys()) if isinstance(choices, dict) else choices
                print(colored(f"  -> Please choose from {allowed}", "yellow"))
                continue
            return parsed_val
        except ValueError:
            print(colored(f"  -> Please enter a valid {cast_type.__name__}.", "yellow"))

print(colored("Please enter student applicant profile (Press ENTER to use defaults):\n", "green"))

data = {}
data['age'] = get_input("Age", int, 20)

raw_prog = get_input("Program Level (college/university)", str, "university", choices=program_map)
data['program_level'] = program_map[raw_prog]

raw_living = get_input("Living Status (family/dorm/rent)", str, "dorm", choices=living_map)
data['living_status'] = living_map[raw_living]

data['academic_year'] = get_input("Academic Year (1-4)", int, 2)
data['gpa_latest'] = get_input("Latest GPA (0.0 - 4.0)", float, 3.2)

raw_income = get_input("Major Income Potential (low/medium/high)", str, "medium", choices=potential_map)
data['major_income_potential'] = potential_map[raw_income]

data['loan_amount'] = get_input("Loan Amount Requested (VND)", float, 25000000.0)

# --- ADVANCED / DERIVED FEATURES ---
# Dynamically estimating advanced behavioral metrics based on sensible proxy heuristics
print(colored("\n[Info] Auto-estimating advanced behavioral metrics based on profile...", "yellow"))

# 1. Maturity Score (Proxy: Age and GPA)
base_maturity = 0.5
if data['age'] < 19:
    base_maturity -= 0.2
elif data['age'] > 22:
    base_maturity += 0.2
if data['gpa_latest'] > 3.0:
    base_maturity += 0.1
elif data['gpa_latest'] < 2.0:
    base_maturity -= 0.2
data['maturity_score'] = max(0.0, min(1.0, base_maturity))

# 2. Debt Ratio (Proxy: Loan Amount vs Expected Income based on Potential)
if raw_income == 'low':
    expected_income = 80000000.0  # 80M VND
elif raw_income == 'medium':
    expected_income = 120000000.0 # 120M VND
else:
    expected_income = 200000000.0 # 200M VND
data['debt_ratio'] = data['loan_amount'] / expected_income
data['high_pressure_flag'] = 1 if data['debt_ratio'] > 0.5 else 0

# 3. Behavior Risk Score & Volatility (Proxy: GPA, Program, Living Status)
risk = 0.3
if data['gpa_latest'] < 2.0:
    risk += 0.4
elif data['gpa_latest'] < 2.8:
    risk += 0.1
if raw_living == 'rent':
    risk += 0.2
data['behavior_risk_score'] = min(1.5, risk)
data['severe_behavior_flag'] = 1 if risk > 0.6 else 0
data['behavior_volatility'] = 0.5 if risk > 0.4 else 0.2

# 4. Support System (Proxy: Living Status)
if raw_living == 'family':
    data['support_numeric'] = 0.8
    data['has_buffer'] = 1
elif raw_living == 'dorm':
    data['support_numeric'] = 0.0
    data['has_buffer'] = 0
else:
    data['support_numeric'] = -0.5
    data['has_buffer'] = 1 if raw_income == 'high' else 0

data['thin_support_flag'] = 1 if data['support_numeric'] < 0 else 0

# 5. Pre-calculated interaction features
data['debt_x_behavior'] = data['debt_ratio'] * data['behavior_risk_score']
data['debt_x_support'] = data['debt_ratio'] * data['support_numeric']
data['debt_x_living'] = data['debt_ratio'] * data['living_status']
data['behavior_under_pressure'] = data['behavior_risk_score'] * (1 + data['high_pressure_flag'])
data['shock_vulnerability'] = int((data['debt_ratio'] > 0.4) and (data['has_buffer'] == 0))

# Build dataframe matching exactly the feature columns
# Use a dictionary of lists to create a single-row DataFrame
df_input = pd.DataFrame([{col: data.get(col, 0) for col in feature_cols}])[feature_cols]

print(colored("\nAnalyzing profile...", "cyan"))

# Prediction
proba = model.predict_proba(df_input)[0][1]

print(colored("\n=======================================", "cyan"))
print("Prediction Results:")
if proba >= 0.5:
    print(colored(f"Risk Status: HIGH RISK (Likely Default)", "red", attrs=["bold"]))
else:
    print(colored(f"Risk Status: LOW RISK (Approved)", "green", attrs=["bold"]))
print(f"Default Probability: {proba*100:.1f}%")
print(colored("=======================================\n", "cyan"))
