"""
Test why the specific profile is refused
Profile from API request:
- age: 35
- employment_status: EMPLOYED
- monthly_income: 7,000,000 VND
- years_employed: 5
- years_credit_history: 5
- home_ownership: RENT
- loan_purpose: PERSONAL
- no defaults
"""

def calculate_refused_profile_score():
    # Profile details
    age = 35
    monthly_income_vnd = 7_000_000
    years_employed = 5
    years_credit_history = 5
    home_ownership = "RENT"
    employment_status = "EMPLOYED"
    has_defaults = False
    currently_defaulting = False
    
    # Reference loan calculation (from request_converter.py)
    # Uses 2x annual income as reference
    annual_income = monthly_income_vnd * 12
    reference_loan = annual_income * 2  # 168M VND
    
    print("=" * 100)
    print("CREDIT SCORE CALCULATION - Nguyen Van Quoc Profile")
    print("=" * 100)
    
    print("\nProfile:")
    print(f"  Age: {age}")
    print(f"  Monthly income: {monthly_income_vnd:,.0f} VND")
    print(f"  Annual income: {annual_income:,.0f} VND")
    print(f"  Years employed: {years_employed}")
    print(f"  Years credit history: {years_credit_history}")
    print(f"  Home ownership: {home_ownership}")
    print(f"  Employment status: {employment_status}")
    print(f"  Defaults: None")
    print(f"\n  Reference loan amount: {reference_loan:,.0f} VND (2x annual income)")
    
    print("\n" + "-" * 100)
    print("SCORE CALCULATION:")
    print("-" * 100)
    
    score = 650
    breakdown = {}
    
    # Age factor
    if age >= 35:
        age_adj = 50
    elif age >= 25:
        age_adj = 30
    else:
        age_adj = 10
    breakdown["age"] = age_adj
    score += age_adj
    print(f"Base score:               650")
    print(f"Age (35):                 +{age_adj} (prime age ≥35)")
    
    # Income factor (in millions)
    monthly_income_m = monthly_income_vnd / 1_000_000
    if monthly_income_m >= 30:
        income_adj = 50
    elif monthly_income_m >= 20:
        income_adj = 40
    elif monthly_income_m >= 15:
        income_adj = 30
    elif monthly_income_m >= 10:
        income_adj = 20
    else:
        income_adj = 10
    breakdown["income"] = income_adj
    score += income_adj
    print(f"Income (7M/month):        +{income_adj} (< 10M threshold)")
    
    # Employment years
    if years_employed >= 10:
        emp_adj = 40
    elif years_employed >= 5:
        emp_adj = 30
    elif years_employed >= 2:
        emp_adj = 20
    else:
        emp_adj = 10
    breakdown["employment"] = emp_adj
    score += emp_adj
    print(f"Employment (5 years):     +{emp_adj} (≥5 years)")
    
    # Home ownership
    if home_ownership == "OWN":
        home_adj = 30
    elif home_ownership == "MORTGAGE":
        home_adj = 20
    else:
        home_adj = 5
    breakdown["home"] = home_adj
    score += home_adj
    print(f"Home ownership (RENT):    +{home_adj} (renter)")
    
    # Credit history
    if years_credit_history >= 10:
        hist_adj = 40
    elif years_credit_history >= 5:
        hist_adj = 30
    elif years_credit_history >= 2:
        hist_adj = 20
    elif years_credit_history >= 1:
        hist_adj = 10
    else:
        hist_adj = 0
    breakdown["credit_history"] = hist_adj
    score += hist_adj
    print(f"Credit history (5 years): +{hist_adj} (≥5 years)")
    
    # Employment status
    if employment_status == "EMPLOYED":
        status_adj = 20
    elif employment_status == "SELF_EMPLOYED":
        status_adj = 10
    else:
        status_adj = -30
    breakdown["employment_status"] = status_adj
    score += status_adj
    print(f"Employment status:        +{status_adj} (EMPLOYED)")
    
    # Defaults
    if currently_defaulting:
        default_adj = -150
    elif has_defaults:
        default_adj = -80
    else:
        default_adj = 0
    breakdown["defaults"] = default_adj
    score += default_adj
    print(f"Defaults:                 {default_adj:+d} (no defaults)")
    
    # DTI ratio - THE PROBLEM!
    monthly_payment_estimate = reference_loan / 36
    dti_ratio = monthly_payment_estimate / monthly_income_vnd
    
    if dti_ratio > 1.5:
        dti_adj = -400
    elif dti_ratio > 1.0:
        dti_adj = -350
    elif dti_ratio > 0.8:
        dti_adj = -300
    elif dti_ratio > 0.6:
        dti_adj = -250
    elif dti_ratio > 0.5:
        dti_adj = -200
    elif dti_ratio > 0.43:
        dti_adj = -150
    elif dti_ratio > 0.36:
        dti_adj = -100
    elif dti_ratio > 0.28:
        dti_adj = -50
    elif dti_ratio > 0.20:
        dti_adj = -20
    else:
        dti_adj = 0
    breakdown["dti"] = dti_adj
    score += dti_adj
    
    print(f"\n🚨 DTI RATIO PENALTY:")
    print(f"  Reference loan: {reference_loan:,.0f} VND")
    print(f"  Estimated monthly payment: {monthly_payment_estimate:,.0f} VND (loan ÷ 36 months)")
    print(f"  Monthly income: {monthly_income_vnd:,.0f} VND")
    print(f"  DTI Ratio: {dti_ratio:.2%} (payment ÷ income)")
    print(f"  Penalty: {dti_adj} points (DTI > 60% is very high!)")
    
    # Final score
    final_score = max(300, min(850, score))
    
    print("\n" + "=" * 100)
    print(f"FINAL CREDIT SCORE: {final_score}")
    print("=" * 100)
    
    print(f"\nMinimum required: 600")
    if final_score >= 600:
        print(f"Result: ✅ APPROVED")
    else:
        print(f"Result: ❌ REJECTED (short by {600 - final_score} points)")
    
    print("\n" + "=" * 100)
    print("WHY IS THIS PROFILE REJECTED?")
    print("=" * 100)
    
    print("\n🔍 ROOT CAUSE: DTI Ratio Calculation Problem")
    print("\nThe system calculates a 'reference loan' = 2x annual income")
    print(f"  → {annual_income:,.0f} × 2 = {reference_loan:,.0f} VND")
    print("\nThis creates an unrealistic DTI ratio:")
    print(f"  → Monthly payment: {monthly_payment_estimate:,.0f} VND")
    print(f"  → Monthly income:  {monthly_income_vnd:,.0f} VND")
    print(f"  → DTI: {dti_ratio:.1%} (payment would consume {dti_ratio:.1%} of income!)")
    print("\nA {:.1%} DTI is considered VERY HIGH RISK:".format(dti_ratio))
    print("  - Banks typically reject loans with DTI > 43%")
    print("  - This profile has DTI of {:.1%}!".format(dti_ratio))
    print("  - Result: -250 point penalty → Score drops to 545")
    
    print("\n💡 THE PROBLEM:")
    print("  This is a CIRCULAR LOGIC issue:")
    print("  1. System uses 2x income as 'reference loan' to calculate credit score")
    print("  2. But this artificial 2x loan creates high DTI penalty")
    print("  3. The DTI penalty LOWERS the credit score")
    print("  4. Lower credit score → rejected or lower tier")
    print("  5. But the customer hasn't even requested a loan yet!")
    
    print("\n🔧 SOLUTIONS:")
    print("\n  Option 1: Don't penalize DTI for reference loan calculation")
    print("    - Only apply DTI penalty for ACTUAL requested loan amount")
    print("    - Reference loan is just for tier calculation, not risk assessment")
    
    print("\n  Option 2: Use lower reference multiplier")
    print("    - Instead of 2x, use 1x or 1.5x annual income")
    print("    - Lower reference → lower DTI → less penalty")
    
    print("\n  Option 3: Remove DTI from credit score calculation entirely")
    print("    - DTI should be checked AFTER tier calculation")
    print("    - Use DTI to limit max loan amount, not to calculate credit score")
    
    print("\n  ⭐ RECOMMENDED: Option 3")
    print("    Credit score should reflect:")
    print("    - Payment history (defaults)")
    print("    - Credit history length")
    print("    - Income stability (employment)")
    print("    - Demographics (age, home ownership)")
    print("\n    DTI should be a SEPARATE check for loan affordability!")
    
    print("\n" + "=" * 100)

if __name__ == "__main__":
    calculate_refused_profile_score()
