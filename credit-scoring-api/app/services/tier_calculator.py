import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class TierCalculator:
    """Calculate customer tier and loan limits based on profile."""
    
    def calculate_credit_bonus(self, credit_score: int) -> Tuple[float, str]:
        """
        Calculate credit score bonus multiplier.
        
        Credit Score Ranges (based on actual risk):
        - 600-649: +0.0x (baseline - minimum acceptable)
        - 650-699: +0.5x (moderate risk)
        - 700-739: +1.0x (good credit)
        - 740-779: +1.5x (very good credit)
        - 780+: +2.0x (excellent credit)
        
        Returns: (bonus_multiplier, reason)
        """
        if credit_score >= 780:
            return 2.0, "excellent credit (780+)"
        elif credit_score >= 740:
            return 1.5, "very good credit (740-779)"
        elif credit_score >= 700:
            return 1.0, "good credit (700-739)"
        elif credit_score >= 650:
            return 0.5, "moderate credit (650-699)"
        else:
            return 0.0, "baseline credit (600-649)"
    
    def calculate_tier(
        self,
        age: int,
        years_employed: float,
        employment_status: str,
        home_ownership: str,
        loan_purpose: str,
        credit_score: int
    ) -> Tuple[str, float, str]:
        """
        Calculate customer tier and income multiplier.
        
        Formula: (base_multiplier + credit_bonus) × purpose_multiplier
        
        Returns: (tier_name, income_multiplier, tier_reason)
        
        Base Tiers (from employment/age/home factors):
        - PLATINUM: Strongest profile (base 6.5x)
        - GOLD: Strong profile (base 5.0x)  
        - SILVER: Good profile (base 3.5x)
        - BRONZE: New/unstable profile (base 2.0x)
        
        Credit Score Bonus (added to base):
        - 780+: +2.0x
        - 740-779: +1.5x
        - 700-739: +1.0x
        - 650-699: +0.5x
        - 600-649: +0.0x
        """
        score = 0
        reasons = []
        
        # Age factor (30-50 is prime earning years)
        if 30 <= age <= 50:
            score += 3
            reasons.append("prime earning age (30-50)")
        elif 25 <= age < 30 or 50 < age <= 60:
            score += 2
            reasons.append("established age")
        elif age < 25:
            score += 0
            reasons.append("young age - building credit")
        else:  # > 60
            score += 1
            reasons.append("senior age - conservative limit")
            
        # Employment stability (most important factor)
        if years_employed >= 5:
            score += 3
            reasons.append("5+ years employment - very stable")
        elif years_employed >= 2:
            score += 2
            reasons.append("2-5 years employment - stable")
        elif years_employed >= 1:
            score += 1
            reasons.append("1-2 years employment")
        else:
            score += 0
            reasons.append("new employment - limited history")
            
        # Employment status
        if employment_status == "EMPLOYED":
            score += 2
            reasons.append("employed - steady income")
        elif employment_status == "SELF_EMPLOYED":
            score += 1
            reasons.append("self-employed - variable income")
        else:
            score += 0
            reasons.append("unemployed - no income verification")
            
        # Home ownership (strong stability indicator)
        if home_ownership == "MORTGAGE":
            score += 2
            reasons.append("mortgage - proven repayment ability")
        elif home_ownership == "OWN":
            score += 1
            reasons.append("homeowner - stable")
        else:
            score += 0
            reasons.append("renter - lower stability")
            
        # Loan purpose multipliers
        purpose_config = {
            "HOME": {
                "multiplier": 1.5,
                "reason": "home loan - secured by property",
                "max_years": 20  # Can use up to 20x annual for home
            },
            "CAR": {
                "multiplier": 1.3,
                "reason": "car loan - secured by vehicle",
                "max_years": 5
            },
            "BUSINESS": {
                "multiplier": 1.2,
                "reason": "business investment - growth potential",
                "max_years": 7
            },
            "EDUCATION": {
                "multiplier": 1.0,
                "reason": "education - investment in future",
                "max_years": 4
            },
            "DEBT_CONSOLIDATION": {
                "multiplier": 0.9,
                "reason": "debt consolidation - restructuring",
                "max_years": 3
            },
            "HOME_IMPROVEMENT": {
                "multiplier": 0.8,
                "reason": "home improvement",
                "max_years": 3
            },
            "MEDICAL": {
                "multiplier": 0.7,
                "reason": "medical expenses",
                "max_years": 2
            },
            "PERSONAL": {
                "multiplier": 0.6,
                "reason": "personal use - unsecured",
                "max_years": 3
            }
        }
        
        purpose_data = purpose_config.get(loan_purpose, purpose_config["PERSONAL"])
        purpose_mult = purpose_data["multiplier"]
        purpose_reason = purpose_data["reason"]
        reasons.append(purpose_reason)
        
        # Determine tier based on total score (0-10 points)
        if score >= 9:
            tier = "PLATINUM"
            base_multiplier = 6.5  # Base 6.5x annual income
        elif score >= 6:
            tier = "GOLD"
            base_multiplier = 5.0  # Base 5.0x annual income
        elif score >= 3:
            tier = "SILVER"
            base_multiplier = 3.5  # Base 3.5x annual income
        else:
            tier = "BRONZE"
            base_multiplier = 2.0  # Base 2.0x annual income
        
        # Calculate credit score bonus
        credit_bonus, credit_reason = self.calculate_credit_bonus(credit_score)
        reasons.append(credit_reason)
        
        # Combine base + credit bonus, then apply purpose multiplier
        # Formula: (base + bonus) × purpose_multiplier
        combined_multiplier = base_multiplier + credit_bonus
        final_multiplier = combined_multiplier * purpose_mult
        
        # Build reason string (show top factors)
        tier_reason = f"{tier} tier: " + ", ".join(reasons[:5])
        
        logger.info(
            f"Tier calculation - Score: {score}, Tier: {tier}, "
            f"Base: {base_multiplier:.1f}x, Credit bonus: +{credit_bonus:.1f}x, "
            f"Final: {final_multiplier:.2f}x (credit score: {credit_score})"
        )
        
        return tier, final_multiplier, tier_reason
    
    def calculate_max_loan(
        self,
        annual_income_vnd: float,
        monthly_income_vnd: float,
        income_multiplier: float,
        loan_purpose: str
    ) -> float:
        """
        Calculate maximum loan amount based on tier and DTI constraints.
        
        Uses the LOWER of:
        1. Income-based limit (tier multiplier × annual income)
        2. DTI-based limit (43% of monthly income × 36 months)
        
        For home loans, extends term to 240 months (20 years).
        """
        # Calculate income-based maximum
        income_based_max = annual_income_vnd * income_multiplier
        
        # Calculate DTI-based maximum (43% standard, 28% for personal/medical)
        if loan_purpose in ["HOME", "CAR", "BUSINESS"]:
            # Secured loans can go up to 43% DTI
            dti_limit = 0.43
            loan_term = 240 if loan_purpose == "HOME" else 60  # 20 years for home, 5 for car
        elif loan_purpose in ["EDUCATION", "DEBT_CONSOLIDATION"]:
            # Medium-term loans
            dti_limit = 0.36
            loan_term = 60  # 5 years
        else:
            # Personal/medical: conservative limit
            dti_limit = 0.28
            loan_term = 36  # 3 years
            
        dti_based_max = monthly_income_vnd * dti_limit * loan_term
        
        # Take the lower limit (more conservative)
        max_loan = min(income_based_max, dti_based_max)
        
        logger.info(
            f"Max loan calculation - Income-based: {income_based_max:,.0f}, "
            f"DTI-based: {dti_based_max:,.0f}, Final: {max_loan:,.0f}"
        )
        
        return max_loan
