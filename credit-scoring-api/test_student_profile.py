"""
Test to check if ML model can predict credit scores > 600 for student profiles.
This is critical for determining if students are even eligible for loans.
"""

import pandas as pd
import numpy as np
from app.services.feature_engineering import FeatureEngineer
from app.services.model_loader import model_loader
from app.services.request_converter import RequestConverter

def test_student_predictions():
    """Test different student profiles to see predicted credit scores."""
    
    feature_engineer = FeatureEngineer()
    converter = RequestConverter()
    
    # Test cases: Different student profiles
    student_cases = [
        {
            "name": "Sinh viên năm 2 - Part-time job",
            "person_age": 20,
            "person_income": 5_000_000,  # 5M VND/year part-time (very low)
            "person_emp_length": 0.5,  # 6 months part-time
            "loan_amnt": 10_000_000,  # 10M VND for school fees
            "loan_int_rate": 12.0,
            "loan_percent_income": 2.0,  # Loan is 2x annual income (very high DTI)
            "credit_score": 620,  # New credit history
            "cb_person_cred_hist_length": 1,  # 1 year credit history
            "cb_person_default_on_file": "N",
            "loan_grade": "C",
            "loan_intent": "EDUCATION"
        },
        {
            "name": "Sinh viên năm 4 - Part-time stable",
            "person_age": 22,
            "person_income": 12_000_000,  # 12M VND/year part-time
            "person_emp_length": 2.0,  # 2 years part-time
            "loan_amnt": 20_000_000,  # 20M VND
            "loan_int_rate": 10.0,
            "loan_percent_income": 1.67,
            "credit_score": 650,
            "cb_person_cred_hist_length": 2,
            "cb_person_default_on_file": "N",
            "loan_grade": "B",
            "loan_intent": "EDUCATION"
        },
        {
            "name": "Sinh viên mới - Không việc làm",
            "person_age": 18,
            "person_income": 1_000_000,  # 1M VND/year (pocket money only)
            "person_emp_length": 0,  # No employment
            "loan_amnt": 15_000_000,  # 15M VND
            "loan_int_rate": 15.0,
            "loan_percent_income": 15.0,  # Loan is 15x income!
            "credit_score": 600,  # Minimum score
            "cb_person_cred_hist_length": 0,  # No credit history
            "cb_person_default_on_file": "N",
            "loan_grade": "D",
            "loan_intent": "EDUCATION"
        },
        {
            "name": "Sinh viên giỏi - Scholarship + part-time",
            "person_age": 23,
            "person_income": 30_000_000,  # 30M VND/year (scholarship + part-time)
            "person_emp_length": 3.0,  # 3 years part-time
            "loan_amnt": 30_000_000,  # 30M VND
            "loan_int_rate": 8.0,
            "loan_percent_income": 1.0,
            "credit_score": 700,
            "cb_person_cred_hist_length": 3,
            "cb_person_default_on_file": "N",
            "loan_grade": "A",
            "loan_intent": "EDUCATION"
        }
    ]
    
    print("=" * 120)
    print("STUDENT LOAN PREDICTION TEST - Can students get credit score > 600?")
    print("=" * 120)
    print("\nMinimum credit score required for approval: 600")
    print("Testing if ML model predicts students as eligible borrowers...")
    print("-" * 120)
    
    results = []
    
    for case in student_cases:
        # Create dataframe
        df = pd.DataFrame([case])
        
        # Engineer features
        features_df = feature_engineer.transform(df)
        
        # Get ML prediction
        prediction_proba = model_loader.lgbm_model.predict_proba(features_df)[0]
        default_probability = float(prediction_proba[1])  # Probability of default
        
        # Convert to internal request format to get derived credit score
        request_dict = converter.convert_to_internal_format(
            customer_id=f"STUDENT_{case['person_age']}",
            age=int(case['person_age']),
            years_employed=case['person_emp_length'],
            annual_income_vnd=case['person_income'],
            loan_amount_vnd=case['loan_amnt'],
            loan_purpose='EDUCATION',
            employment_status='STUDENT',
            home_ownership='RENT',
            previous_defaults='N'
        )
        
        derived_credit_score = request_dict.get('credit_score', 0)
        
        # Determine if eligible
        is_eligible = derived_credit_score >= 600
        
        result = {
            "name": case['name'],
            "age": case['person_age'],
            "income": case['person_income'],
            "emp_length": case['person_emp_length'],
            "loan_amount": case['loan_amnt'],
            "input_score": case['credit_score'],
            "derived_score": derived_credit_score,
            "default_prob": default_probability,
            "eligible": is_eligible
        }
        results.append(result)
        
        print(f"\n{case['name']}")
        print(f"  Profile:")
        print(f"    - Age: {case['person_age']}")
        print(f"    - Income: {case['person_income']:,.0f} VND/year")
        print(f"    - Employment: {case['person_emp_length']} years")
        print(f"    - Loan request: {case['loan_amnt']:,.0f} VND")
        print(f"    - Debt-to-Income: {case['loan_percent_income']:.1f}x")
        print(f"    - Input credit score: {case['credit_score']}")
        print(f"  Model Results:")
        print(f"    - Default probability: {default_probability:.2%}")
        print(f"    - Derived credit score: {derived_credit_score}")
        print(f"    - {'✅ ELIGIBLE' if is_eligible else '❌ REJECTED'} (score {'≥' if is_eligible else '<'} 600)")
    
    print("\n" + "=" * 120)
    print("SUMMARY")
    print("=" * 120)
    
    eligible_count = sum(1 for r in results if r['eligible'])
    total_count = len(results)
    
    print(f"\nEligible students: {eligible_count}/{total_count} ({eligible_count/total_count*100:.0f}%)")
    
    if eligible_count == 0:
        print("\n⚠️  CRITICAL ISSUE: NO STUDENTS ARE ELIGIBLE!")
        print("   The 600 minimum credit score threshold is too high for student profiles.")
        print("   Students typically have:")
        print("   - Low/no income")
        print("   - Short/no employment history")
        print("   - Short/no credit history")
        print("\n💡 RECOMMENDATIONS:")
        print("   1. Lower minimum credit score to 550 for EDUCATION loans")
        print("   2. Create special student tier with alternative assessment")
        print("   3. Allow co-signer/guarantor for students")
        print("   4. Base limits on tuition amount, not income multiplier")
    elif eligible_count < total_count:
        print(f"\n⚠️  WARNING: Only {eligible_count}/{total_count} students eligible")
        print("   Many student profiles are rejected by 600 minimum score.")
    else:
        print("\n✅ All student profiles meet 600 minimum threshold")
    
    print("=" * 120)
    
    return results

if __name__ == "__main__":
    test_student_predictions()
