import pandas as pd
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
USER_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'alternative_model', 'best_model_user_friendly_xgboost.pkl')
USER_FEATURE_COLS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'alternative_model', 'user_friendly_feature_cols.pkl')
LEGACY_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'alternative_model', 'best_model_xgboost.pkl')
LEGACY_FEATURE_COLS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'alternative_model', 'feature_cols.pkl')

print(colored("=======================================", "cyan"))
print(colored("   Student Loan Risk Prediction CLI    ", "cyan", attrs=["bold"]))
print(colored("=======================================\n", "cyan"))

if os.path.exists(USER_MODEL_PATH) and os.path.exists(USER_FEATURE_COLS_PATH):
    MODEL_PATH = USER_MODEL_PATH
    FEATURE_COLS_PATH = USER_FEATURE_COLS_PATH
    print(colored("Using production user-friendly model artifacts.", "green"))
elif os.path.exists(LEGACY_MODEL_PATH) and os.path.exists(LEGACY_FEATURE_COLS_PATH):
    MODEL_PATH = LEGACY_MODEL_PATH
    FEATURE_COLS_PATH = LEGACY_FEATURE_COLS_PATH
    print(colored("User-friendly model not found. Falling back to legacy model.", "yellow"))
else:
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

print(colored("Required profile fields:", "cyan"))
print("- Living Status")
print("- Academic Year")
print("- Maturity Score")
print("- Latest GPA")
print("- Major Income Potential")
print("- Loan Amount Requested")
print()

data = {}

# User-requested profile inputs only.
raw_living = get_input("Living Status (family/dorm/rent)", str, "dorm", choices=living_map)
data['living_status'] = living_map[raw_living]
data['academic_year'] = get_input("Academic Year (1-4)", int, 2)
data['maturity_score'] = get_input("Maturity Score (0.0 - 1.0)", float, 0.5)
data['gpa_latest'] = get_input("Latest GPA (0.0 - 4.0)", float, 3.2)

raw_income = get_input("Major Income Potential (low/medium/high)", str, "medium", choices=potential_map)
data['major_income_potential'] = potential_map[raw_income]
data['loan_amount'] = get_input("Loan Amount Requested (VND)", float, 25000000.0)

# Auto-engineer features used by the production-friendly retrained model.
data['loan_to_maturity_ratio'] = data['loan_amount'] / (data['maturity_score'] + 0.1)
data['academic_maturity'] = data['academic_year'] * data['maturity_score']
data['gpa_x_maturity'] = data['gpa_latest'] * data['maturity_score']
data['gpa_gap_from_4'] = 4.0 - data['gpa_latest']
data['living_x_income_potential'] = data['living_status'] * data['major_income_potential']
data['loan_x_income_potential'] = data['loan_amount'] * data['major_income_potential']

# Build dataframe matching exactly the feature columns
# Use a dictionary of lists to create a single-row DataFrame
df_input = pd.DataFrame([{col: data.get(col, 0) for col in feature_cols}])[feature_cols]

print(colored("\nAnalyzing profile...", "cyan"))

# Prediction
proba = model.predict_proba(df_input)[0][1]

print(colored("\n=======================================", "cyan"))
print("Prediction Results:")
if proba >= 0.4:
    print(colored(f"Risk Status: HIGH RISK (Likely Default)", "red", attrs=["bold"]))
else:
    print(colored(f"Risk Status: LOW RISK (Approved)", "green", attrs=["bold"]))
print(f"Default Probability: {proba*100:.1f}%")
print(colored("=======================================\n", "cyan"))
