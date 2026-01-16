"""
Demo script to show the improvement in tier calculation with credit score integration.
Tests the new formula: (base_multiplier + credit_bonus) × purpose_multiplier
"""

from app.services.tier_calculator import TierCalculator

def test_tier_calculation():
    """Test different credit scores with same profile."""
    
    calculator = TierCalculator()
    
    # Test profile: Good employment, prime age, renter, personal loan
    test_cases = [
        {
            "name": "Minimum acceptable credit (600)",
            "age": 35,
            "years_employed": 5.0,
            "employment_status": "EMPLOYED",
            "home_ownership": "RENT",
            "loan_purpose": "PERSONAL",
            "credit_score": 600
        },
        {
            "name": "Moderate credit (675)",
            "age": 35,
            "years_employed": 5.0,
            "employment_status": "EMPLOYED",
            "home_ownership": "RENT",
            "loan_purpose": "PERSONAL",
            "credit_score": 675
        },
        {
            "name": "Good credit (720)",
            "age": 35,
            "years_employed": 5.0,
            "employment_status": "EMPLOYED",
            "home_ownership": "RENT",
            "loan_purpose": "PERSONAL",
            "credit_score": 720
        },
        {
            "name": "Very good credit (760)",
            "age": 35,
            "years_employed": 5.0,
            "employment_status": "EMPLOYED",
            "home_ownership": "RENT",
            "loan_purpose": "PERSONAL",
            "credit_score": 760
        },
        {
            "name": "Excellent credit (800)",
            "age": 35,
            "years_employed": 5.0,
            "employment_status": "EMPLOYED",
            "home_ownership": "RENT",
            "loan_purpose": "PERSONAL",
            "credit_score": 800
        }
    ]
    
    print("=" * 100)
    print("TIER CALCULATION TEST - Credit Score Impact")
    print("=" * 100)
    print("\nProfile: Age 35, 5+ years employed, Renter, Personal loan")
    print("-" * 100)
    
    for case in test_cases:
        tier, multiplier, reason = calculator.calculate_tier(
            age=case["age"],
            years_employed=case["years_employed"],
            employment_status=case["employment_status"],
            home_ownership=case["home_ownership"],
            loan_purpose=case["loan_purpose"],
            credit_score=case["credit_score"]
        )
        
        # Calculate loan amount with 50M annual income example
        annual_income = 50_000_000  # 50M VND per year
        max_loan = annual_income * multiplier
        
        print(f"\n{case['name']} (Score: {case['credit_score']})")
        print(f"  → Tier: {tier}")
        print(f"  → Multiplier: {multiplier:.2f}x")
        print(f"  → Max Loan (50M income): {max_loan:,.0f} VND ({max_loan/1_000_000:.1f}M)")
        print(f"  → Reason: {reason}")
    
    print("\n" + "=" * 100)
    print("COMPARISON: HOME LOAN (higher purpose multiplier)")
    print("=" * 100)
    
    # Test with HOME loan to show higher limits
    home_cases = [
        {"credit_score": 600, "name": "Minimum credit"},
        {"credit_score": 750, "name": "Very good credit"}
    ]
    
    print("\nProfile: Age 35, 5+ years employed, Homeowner (Mortgage), HOME loan")
    print("-" * 100)
    
    for case in home_cases:
        tier, multiplier, reason = calculator.calculate_tier(
            age=35,
            years_employed=5.0,
            employment_status="EMPLOYED",
            home_ownership="MORTGAGE",
            loan_purpose="HOME",
            credit_score=case["credit_score"]
        )
        
        annual_income = 200_000_000  # 200M VND per year (higher for home loan)
        max_loan = annual_income * multiplier
        
        print(f"\n{case['name']} (Score: {case['credit_score']})")
        print(f"  → Tier: {tier}")
        print(f"  → Multiplier: {multiplier:.2f}x")
        print(f"  → Max Loan (200M income): {max_loan:,.0f} VND ({max_loan/1_000_000_000:.2f}B)")
    
    print("\n" + "=" * 100)
    print("KEY IMPROVEMENTS:")
    print("=" * 100)
    print("✅ Credit score 600 vs 800 now has CLEAR difference (3.6x vs 5.1x for personal loan)")
    print("✅ Higher base multipliers (2.0x-6.5x instead of 1.5x-4.5x)")
    print("✅ Credit bonus rewards better credit history (+0.0x to +2.0x)")
    print("✅ Combined with employment/age/home factors for holistic assessment")
    print("=" * 100)

if __name__ == "__main__":
    test_tier_calculation()
