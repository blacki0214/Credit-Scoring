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

top_shap_features = [
    'debt_x_behavior',
    'financial_stress_index',
    'debt_x_support',
    'behavior_under_pressure'
]

print(colored("Required profile fields:", "cyan"))
print("- Living Status")
print("- Academic Year")
print("- Maturity Score")
print("- Latest GPA")
print("- Major Income Potential")
print("- Loan Amount Requested")
print(colored("\nTop 4 SHAP features (manual input):", "cyan"))
for feat in top_shap_features:
    print(f"- {feat}")
print()

data = {}

# Keep stable defaults for non-requested base fields to make the CLI shorter.
data['age'] = 20
data['program_level'] = program_map['university']
data['debt_ratio'] = 0.30
data['high_pressure_flag'] = 0
data['behavior_risk_score'] = 0.40
data['behavior_volatility'] = 0.20
data['severe_behavior_flag'] = 0
data['support_numeric'] = 0.00
data['has_buffer'] = 1
data['thin_support_flag'] = 0

# User-requested profile inputs.
raw_living = get_input("Living Status (family/dorm/rent)", str, "dorm", choices=living_map)
data['living_status'] = living_map[raw_living]
data['academic_year'] = get_input("Academic Year (1-4)", int, 2)
data['maturity_score'] = get_input("Maturity Score (0.0 - 1.0)", float, 0.5)
data['gpa_latest'] = get_input("Latest GPA (0.0 - 4.0)", float, 3.2)

raw_income = get_input("Major Income Potential (low/medium/high)", str, "medium", choices=potential_map)
data['major_income_potential'] = potential_map[raw_income]
data['loan_amount'] = get_input("Loan Amount Requested (VND)", float, 25000000.0)

# User-requested top SHAP feature inputs.
data['debt_x_behavior'] = get_input("debt_x_behavior", float, data['debt_ratio'] * data['behavior_risk_score'])
data['financial_stress_index'] = get_input("financial_stress_index", float, data['debt_ratio'] * data['behavior_volatility'])
data['debt_x_support'] = get_input("debt_x_support", float, data['debt_ratio'] * data['support_numeric'])
data['behavior_under_pressure'] = get_input("behavior_under_pressure", float, data['behavior_risk_score'] * (1 + data['high_pressure_flag']))

# Auto-fill remaining engineered features for model completeness.
data['debt_x_living'] = data['debt_ratio'] * data['living_status']
data['shock_vulnerability'] = int((data['debt_ratio'] > 0.4) and (data['has_buffer'] == 0))
data['academic_resilience'] = data['gpa_latest'] * data['support_numeric']
data['risk_compounding'] = data['severe_behavior_flag'] + data['thin_support_flag'] + data['high_pressure_flag']
data['loan_to_maturity_ratio'] = data['loan_amount'] / (data['maturity_score'] + 0.1)

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
