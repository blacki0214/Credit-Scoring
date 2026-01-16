"""
Test credit score calculation for student profiles.
This tests if students can even reach the 600 minimum score threshold.
"""

def calculate_student_credit_scores():
    """
    Manually calculate credit scores for student profiles based on the formula in request_converter.py
    
    Formula breakdown:
    - Base: 650
    - Age: +10 to +50
    - Income: +10 to +50
    - Employment years: +10 to +40
    - Home ownership: +5 to +30
    - Credit history: +0 to +40
    - Employment status: -30 to +20
    - Defaults: -150 to 0
    - DTI ratio: -400 to 0
    """
    
    student_cases = [
        {
            "name": "Sinh viên năm 2 - Part-time job",
            "age": 20,
            "monthly_income_m": 0.417,  # 5M VND/year = 0.417M/month
            "years_employed": 0.5,
            "home_ownership": "RENT",
            "years_credit_history": 1,
            "employment_status": "STUDENT",
            "has_defaults": False,
            "currently_defaulting": False,
            "loan_amount": 10_000_000
        },
        {
            "name": "Sinh viên năm 4 - Part-time stable",
            "age": 22,
            "monthly_income_m": 1.0,  # 12M VND/year = 1M/month
            "years_employed": 2.0,
            "home_ownership": "RENT",
            "years_credit_history": 2,
            "employment_status": "STUDENT",
            "has_defaults": False,
            "currently_defaulting": False,
            "loan_amount": 20_000_000
        },
        {
            "name": "Sinh viên mới - Không việc làm",
            "age": 18,
            "monthly_income_m": 0.083,  # 1M VND/year = 0.083M/month
            "years_employed": 0,
            "home_ownership": "RENT",
            "years_credit_history": 0,
            "employment_status": "STUDENT",
            "has_defaults": False,
            "currently_defaulting": False,
            "loan_amount": 15_000_000
        },
        {
            "name": "Sinh viên giỏi - Scholarship + part-time",
            "age": 23,
            "monthly_income_m": 2.5,  # 30M VND/year = 2.5M/month
            "years_employed": 3.0,
            "home_ownership": "RENT",
            "years_credit_history": 3,
            "employment_status": "STUDENT",
            "has_defaults": False,
            "currently_defaulting": False,
            "loan_amount": 30_000_000
        }
    ]
    
    print("=" * 120)
    print("STUDENT CREDIT SCORE CALCULATION - Manual Test")
    print("=" * 120)
    print("\nMinimum score for approval: 600")
    print("Testing if students can reach this threshold...\n")
    print("-" * 120)
    
    results = []
    
    for case in student_cases:
        score = 650  # Base score
        breakdown = {"base": 650}
        
        # Age factor
        if case["age"] >= 35:
            age_adj = 50
        elif case["age"] >= 25:
            age_adj = 30
        else:
            age_adj = 10
        breakdown["age"] = age_adj
        score += age_adj
        
        # Income factor (in millions)
        if case["monthly_income_m"] >= 30:
            income_adj = 50
        elif case["monthly_income_m"] >= 20:
            income_adj = 40
        elif case["monthly_income_m"] >= 15:
            income_adj = 30
        elif case["monthly_income_m"] >= 10:
            income_adj = 20
        else:
            income_adj = 10
        breakdown["income"] = income_adj
        score += income_adj
        
        # Employment years factor
        if case["years_employed"] >= 10:
            emp_adj = 40
        elif case["years_employed"] >= 5:
            emp_adj = 30
        elif case["years_employed"] >= 2:
            emp_adj = 20
        else:
            emp_adj = 10
        breakdown["employment_years"] = emp_adj
        score += emp_adj
        
        # Home ownership factor
        if case["home_ownership"] == "OWN":
            home_adj = 30
        elif case["home_ownership"] == "MORTGAGE":
            home_adj = 20
        else:
            home_adj = 5
        breakdown["home_ownership"] = home_adj
        score += home_adj
        
        # Credit history factor
        if case["years_credit_history"] >= 10:
            hist_adj = 40
        elif case["years_credit_history"] >= 5:
            hist_adj = 30
        elif case["years_credit_history"] >= 2:
            hist_adj = 20
        elif case["years_credit_history"] >= 1:
            hist_adj = 10
        else:
            hist_adj = 0
        breakdown["credit_history"] = hist_adj
        score += hist_adj
        
        # Employment status factor
        if case["employment_status"] == "EMPLOYED":
            status_adj = 20
        elif case["employment_status"] == "SELF_EMPLOYED":
            status_adj = 10
        else:  # STUDENT, UNEMPLOYED, RETIRED
            status_adj = -30
        breakdown["employment_status"] = status_adj
        score += status_adj
        
        # Defaults
        if case["currently_defaulting"]:
            default_adj = -150
        elif case["has_defaults"]:
            default_adj = -80
        else:
            default_adj = 0
        breakdown["defaults"] = default_adj
        score += default_adj
        
        # DTI ratio (CRITICAL)
        monthly_income = case["monthly_income_m"] * 1_000_000
        if monthly_income > 0:
            monthly_payment_estimate = case["loan_amount"] / 36
            dti_ratio = monthly_payment_estimate / monthly_income
            
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
            breakdown["dti_ratio"] = dti_ratio
            score += dti_adj
        else:
            breakdown["dti"] = -400
            breakdown["dti_ratio"] = float('inf')
            score -= 400
        
        # Final score (capped at 300-850)
        final_score = max(300, min(850, score))
        breakdown["final"] = final_score
        
        is_eligible = final_score >= 600
        
        results.append({
            "name": case["name"],
            "score": final_score,
            "eligible": is_eligible,
            "breakdown": breakdown
        })
        
        print(f"\n{case['name']}")
        print(f"  Profile:")
        print(f"    - Age: {case['age']} years")
        print(f"    - Monthly income: {case['monthly_income_m']:.2f}M VND")
        print(f"    - Employment: {case['years_employed']} years")
        print(f"    - Credit history: {case['years_credit_history']} years")
        print(f"    - Loan request: {case['loan_amount']:,.0f} VND")
        if "dti_ratio" in breakdown:
            print(f"    - DTI ratio: {breakdown['dti_ratio']:.2%}")
        print(f"\n  Score Breakdown:")
        print(f"    Base score:              {breakdown['base']:+4d}")
        print(f"    Age adjustment:          {breakdown['age']:+4d}")
        print(f"    Income adjustment:       {breakdown['income']:+4d}")
        print(f"    Employment years:        {breakdown['employment_years']:+4d}")
        print(f"    Home ownership:          {breakdown['home_ownership']:+4d}")
        print(f"    Credit history:          {breakdown['credit_history']:+4d}")
        print(f"    Employment status:       {breakdown['employment_status']:+4d}")
        print(f"    Defaults:                {breakdown['defaults']:+4d}")
        print(f"    DTI ratio penalty:       {breakdown['dti']:+4d}")
        print(f"    {'─' * 40}")
        print(f"    FINAL SCORE:             {breakdown['final']}")
        print(f"\n    Result: {'✅ ELIGIBLE' if is_eligible else '❌ REJECTED'} (threshold: 600)")
    
    print("\n" + "=" * 120)
    print("SUMMARY & ANALYSIS")
    print("=" * 120)
    
    eligible_count = sum(1 for r in results if r['eligible'])
    total_count = len(results)
    
    print(f"\nEligible students: {eligible_count}/{total_count} ({eligible_count/total_count*100:.0f}%)")
    
    print("\n🔍 KEY FINDINGS:")
    
    for r in results:
        if not r['eligible']:
            print(f"\n  ❌ {r['name']}: Score {r['score']} (need 600)")
            print(f"     Main problems:")
            if r['breakdown']['employment_status'] < 0:
                print(f"       - STUDENT status: {r['breakdown']['employment_status']} points")
            if r['breakdown']['dti'] < -100:
                print(f"       - DTI ratio too high: {r['breakdown']['dti']} points")
            if r['breakdown']['age'] < 30:
                print(f"       - Young age: only {r['breakdown']['age']} points")
    
    if eligible_count == 0:
        print("\n" + "🚨" * 40)
        print("  CRITICAL ISSUE: NO STUDENTS CAN GET APPROVED!")
        print("🚨" * 40)
        print("\n  The current credit scoring formula is INCOMPATIBLE with student loans:")
        print("\n  Problems:")
        print("    1. STUDENT employment status: -30 points (huge penalty)")
        print("    2. High DTI ratio for education loans: -150 to -400 points")
        print("    3. Low income: only +10 points")
        print("    4. Young age (<25): only +10 points")
        print("    5. Short credit history: +0 to +20 points")
        print("\n  💡 SOLUTION OPTIONS:")
        print("\n  Option 1: Special rules for EDUCATION loans")
        print("    - Don't apply STUDENT employment penalty for EDUCATION loans")
        print("    - Use more lenient DTI calculation for education (ignore or reduce)")
        print("    - Lower minimum score to 550 for EDUCATION loans")
        print("\n  Option 2: Co-signer system")
        print("    - Allow parents/guardians to co-sign")
        print("    - Use co-signer's income and credit for assessment")
        print("\n  Option 3: Tuition-based assessment")
        print("    - Don't use income multiplier for students")
        print("    - Set max loan = tuition + living expenses (verified amount)")
        print("    - Ignore DTI ratio for verified education expenses")
        
    print("\n" + "=" * 120)

if __name__ == "__main__":
    calculate_student_credit_scores()
