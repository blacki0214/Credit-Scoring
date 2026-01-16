"""
Test the FIXED credit score calculation (DTI penalty removed)
Compare before/after for various profiles
"""

def calculate_score_fixed(age, monthly_income_m, years_employed, home_ownership, 
                          years_credit_history, employment_status, has_defaults, currently_defaulting):
    """Calculate credit score with DTI penalty removed (FIXED version)"""
    
    score = 650  # Base
    
    # Age
    if age >= 35:
        score += 50
    elif age >= 25:
        score += 30
    else:
        score += 10
    
    # Income (millions)
    if monthly_income_m >= 30:
        score += 50
    elif monthly_income_m >= 20:
        score += 40
    elif monthly_income_m >= 15:
        score += 30
    elif monthly_income_m >= 10:
        score += 20
    else:
        score += 10
    
    # Employment years
    if years_employed >= 10:
        score += 40
    elif years_employed >= 5:
        score += 30
    elif years_employed >= 2:
        score += 20
    else:
        score += 10
    
    # Home ownership
    if home_ownership == "OWN":
        score += 30
    elif home_ownership == "MORTGAGE":
        score += 20
    else:
        score += 5
    
    # Credit history
    if years_credit_history >= 10:
        score += 40
    elif years_credit_history >= 5:
        score += 30
    elif years_credit_history >= 2:
        score += 20
    elif years_credit_history >= 1:
        score += 10
    else:
        score += 0
    
    # Employment status
    if employment_status == "EMPLOYED":
        score += 20
    elif employment_status == "SELF_EMPLOYED":
        score += 10
    else:
        score += -30
    
    # Defaults
    if currently_defaulting:
        score += -150
    elif has_defaults:
        score += -80
    
    # DTI REMOVED - NO PENALTY!
    
    return max(300, min(850, score))


def calculate_score_old(age, monthly_income_m, years_employed, home_ownership, 
                        years_credit_history, employment_status, has_defaults, 
                        currently_defaulting, loan_amount):
    """OLD calculation with DTI penalty"""
    
    score = 650
    
    # Same as above...
    if age >= 35:
        score += 50
    elif age >= 25:
        score += 30
    else:
        score += 10
    
    if monthly_income_m >= 30:
        score += 50
    elif monthly_income_m >= 20:
        score += 40
    elif monthly_income_m >= 15:
        score += 30
    elif monthly_income_m >= 10:
        score += 20
    else:
        score += 10
    
    if years_employed >= 10:
        score += 40
    elif years_employed >= 5:
        score += 30
    elif years_employed >= 2:
        score += 20
    else:
        score += 10
    
    if home_ownership == "OWN":
        score += 30
    elif home_ownership == "MORTGAGE":
        score += 20
    else:
        score += 5
    
    if years_credit_history >= 10:
        score += 40
    elif years_credit_history >= 5:
        score += 30
    elif years_credit_history >= 2:
        score += 20
    elif years_credit_history >= 1:
        score += 10
    
    if employment_status == "EMPLOYED":
        score += 20
    elif employment_status == "SELF_EMPLOYED":
        score += 10
    else:
        score += -30
    
    if currently_defaulting:
        score += -150
    elif has_defaults:
        score += -80
    
    # DTI Penalty
    monthly_income = monthly_income_m * 1_000_000
    monthly_payment = loan_amount / 36
    dti = monthly_payment / monthly_income if monthly_income > 0 else 999
    
    if dti > 1.5:
        score += -400
    elif dti > 1.0:
        score += -350
    elif dti > 0.8:
        score += -300
    elif dti > 0.6:
        score += -250
    elif dti > 0.5:
        score += -200
    elif dti > 0.43:
        score += -150
    elif dti > 0.36:
        score += -100
    elif dti > 0.28:
        score += -50
    elif dti > 0.20:
        score += -20
    
    return max(300, min(850, score))


def test_improvements():
    test_cases = [
        {
            "name": "Nguyen Van Quoc - Original refused profile",
            "age": 35,
            "monthly_income_m": 7.0,
            "years_employed": 5,
            "home_ownership": "RENT",
            "years_credit_history": 5,
            "employment_status": "EMPLOYED",
            "has_defaults": False,
            "currently_defaulting": False,
            "ref_loan": 168_000_000
        },
        {
            "name": "Sinh viên năm 2 - Part-time",
            "age": 20,
            "monthly_income_m": 0.417,
            "years_employed": 0.5,
            "home_ownership": "RENT",
            "years_credit_history": 1,
            "employment_status": "STUDENT",
            "has_defaults": False,
            "currently_defaulting": False,
            "ref_loan": 10_000_000
        },
        {
            "name": "Sinh viên năm 4 - Part-time stable",
            "age": 22,
            "monthly_income_m": 1.0,
            "years_employed": 2.0,
            "home_ownership": "RENT",
            "years_credit_history": 2,
            "employment_status": "STUDENT",
            "has_defaults": False,
            "currently_defaulting": False,
            "ref_loan": 20_000_000
        },
        {
            "name": "Young professional",
            "age": 28,
            "monthly_income_m": 15.0,
            "years_employed": 3,
            "home_ownership": "RENT",
            "years_credit_history": 3,
            "employment_status": "EMPLOYED",
            "has_defaults": False,
            "currently_defaulting": False,
            "ref_loan": 360_000_000
        }
    ]
    
    print("=" * 120)
    print("CREDIT SCORE IMPROVEMENT TEST - DTI Penalty Removed")
    print("=" * 120)
    print("\nComparing OLD (with DTI penalty) vs NEW (without DTI penalty)")
    print("-" * 120)
    
    for case in test_cases:
        old_score = calculate_score_old(
            case["age"], case["monthly_income_m"], case["years_employed"],
            case["home_ownership"], case["years_credit_history"], 
            case["employment_status"], case["has_defaults"], 
            case["currently_defaulting"], case["ref_loan"]
        )
        
        new_score = calculate_score_fixed(
            case["age"], case["monthly_income_m"], case["years_employed"],
            case["home_ownership"], case["years_credit_history"], 
            case["employment_status"], case["has_defaults"], 
            case["currently_defaulting"]
        )
        
        improvement = new_score - old_score
        old_status = "✅ PASS" if old_score >= 600 else "❌ FAIL"
        new_status = "✅ PASS" if new_score >= 600 else "❌ FAIL"
        
        print(f"\n{case['name']}")
        print(f"  Age: {case['age']}, Income: {case['monthly_income_m']:.1f}M, Employed: {case['years_employed']}y")
        print(f"  OLD Score: {old_score} {old_status}")
        print(f"  NEW Score: {new_score} {new_status}")
        print(f"  Improvement: {improvement:+d} points")
        if old_score < 600 and new_score >= 600:
            print(f"  🎉 NOW APPROVED!")
    
    print("\n" + "=" * 120)
    print("SUMMARY")
    print("=" * 120)
    
    old_pass = sum(1 for c in test_cases if calculate_score_old(
        c["age"], c["monthly_income_m"], c["years_employed"], c["home_ownership"],
        c["years_credit_history"], c["employment_status"], c["has_defaults"],
        c["currently_defaulting"], c["ref_loan"]) >= 600)
    
    new_pass = sum(1 for c in test_cases if calculate_score_fixed(
        c["age"], c["monthly_income_m"], c["years_employed"], c["home_ownership"],
        c["years_credit_history"], c["employment_status"], c["has_defaults"],
        c["currently_defaulting"]) >= 600)
    
    print(f"\nOLD System: {old_pass}/{len(test_cases)} approved ({old_pass/len(test_cases)*100:.0f}%)")
    print(f"NEW System: {new_pass}/{len(test_cases)} approved ({new_pass/len(test_cases)*100:.0f}%)")
    print(f"Improvement: +{new_pass - old_pass} more approvals")
    
    print("\n✅ KEY BENEFITS:")
    print("  1. Removed circular logic - no penalty for hypothetical reference loan")
    print("  2. Credit score now reflects TRUE creditworthiness:")
    print("     - Payment history (defaults)")
    print("     - Credit history length")
    print("     - Income stability (employment)")
    print("     - Demographics (age, home ownership)")
    print("  3. DTI will still be checked separately when calculating MAX LOAN amount")
    print("  4. More fair assessment - good profiles no longer rejected unfairly")
    
    print("\n⚠️  NOTE: Students still have challenges due to:")
    print("  - STUDENT employment status: -30 points")
    print("  - Young age: only +10 points")
    print("  - Consider special handling for EDUCATION loans")
    
    print("=" * 120)

if __name__ == "__main__":
    test_improvements()
