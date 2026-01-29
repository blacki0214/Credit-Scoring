"""
Smart Loan Recommendation CLI Demo
Interactive command-line demo for tomorrow's presentation
Windows-optimized version with colorama
"""
import requests
import json
from typing import Dict, Any
import os
import sys

# Try to use colorama for Windows compatibility
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  # Auto-reset colors after each print
    USE_COLORAMA = True
except ImportError:
    USE_COLORAMA = False
    print("Note: Install colorama for colored output: pip install colorama")

# API endpoint
API_URL = "http://localhost:8000/api/apply"

# Color codes - Windows compatible
class Colors:
    if USE_COLORAMA:
        HEADER = Fore.MAGENTA + Style.BRIGHT
        OKBLUE = Fore.BLUE + Style.BRIGHT
        OKCYAN = Fore.CYAN
        OKGREEN = Fore.GREEN + Style.BRIGHT
        WARNING = Fore.YELLOW
        FAIL = Fore.RED + Style.BRIGHT
        ENDC = Style.RESET_ALL
        BOLD = Style.BRIGHT
        UNDERLINE = ''
    else:
        HEADER = ''
        OKBLUE = ''
        OKCYAN = ''
        OKGREEN = ''
        WARNING = ''
        FAIL = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''

def clear_screen():
    """Clear terminal screen - Windows compatible"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print demo header"""
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print("    SMART LOAN RECOMMENDATION SYSTEM - TIER-BASED DEMO")
    print("=" * 70)
    print(f"{Colors.ENDC}\n")

def print_tier_emoji(tier: str) -> str:
    """Get emoji for tier"""
    emojis = {
        "BRONZE": "",
        "SILVER": "",
        "GOLD": "",
        "PLATINUM": ""
    }
    return emojis.get(tier, "")

def format_currency(amount: float) -> str:
    """Format amount in VND"""
    if amount >= 1_000_000_000:
        return f"{amount/1_000_000_000:.2f} tỷ VND"
    elif amount >= 1_000_000:
        return f"{amount/1_000_000:.0f} triệu VND"
    else:
        return f"{amount:,.0f} VND"

def get_customer_input() -> Dict[str, Any]:
    """Get customer information from user"""
    print("Enter Customer Information:\n")
    
    full_name = input("Full Name: ").strip() or "Demo Customer"
    age = int(input("Age (18-100): ").strip() or "30")
    monthly_income = float(input("Monthly Income (VND, e.g., 20000000): ").strip() or "20000000")
    
    print("\nEmployment Status:")
    print("  1. EMPLOYED")
    print("  2. SELF_EMPLOYED")
    print("  3. UNEMPLOYED")
    emp_choice = input("Select (1-3): ").strip() or "1"
    employment_status = ["EMPLOYED", "SELF_EMPLOYED", "UNEMPLOYED"][int(emp_choice) - 1]
    
    years_employed = float(input("Years Employed: ").strip() or "5.0")
    
    print("\nHome Ownership:")
    print("  1. RENT")
    print("  2. OWN")
    print("  3. MORTGAGE")
    print("  4. LIVING_WITH_PARENTS")
    home_choice = input("Select (1-4): ").strip() or "3"
    home_ownership = ["RENT", "OWN", "MORTGAGE", "LIVING_WITH_PARENTS"][int(home_choice) - 1]
    
    print("\nLoan Purpose:")
    print("  1. HOME (Highest amount!)")
    print("  2. CAR")
    print("  3. BUSINESS")
    print("  4. EDUCATION")
    print("  5. DEBT_CONSOLIDATION")
    print("  6. HOME_IMPROVEMENT")
    print("  7. MEDICAL")
    print("  8. PERSONAL (Lowest amount)")
    purpose_choice = input("Select (1-8): ").strip() or "1"
    purposes = ["HOME", "CAR", "BUSINESS", "EDUCATION", "DEBT_CONSOLIDATION", 
                "HOME_IMPROVEMENT", "MEDICAL", "PERSONAL"]
    loan_purpose = purposes[int(purpose_choice) - 1]
    
    years_credit = int(input("Years of Credit History: ").strip() or "5")
    
    has_defaults = input("Ever defaulted on a loan? (y/n): ").strip().lower() == 'y'
    currently_defaulting = input("Currently in default? (y/n): ").strip().lower() == 'y'
    
    return {
        "full_name": full_name,
        "age": age,
        "monthly_income": monthly_income,
        "employment_status": employment_status,
        "years_employed": years_employed,
        "home_ownership": home_ownership,
        "loan_purpose": loan_purpose,
        "years_credit_history": years_credit,
        "has_previous_defaults": has_defaults,
        "currently_defaulting": currently_defaulting
    }

def display_result(result: Dict[str, Any], customer_data: Dict[str, Any]):
    """Display loan recommendation result"""
    print("\n" + "=" * 70)
    print("LOAN RECOMMENDATION RESULT")
    print("=" * 70 + "\n")
    
    # Customer info
    print(f"Customer: {customer_data['full_name']}")
    print(f"Monthly Income: {format_currency(customer_data['monthly_income'])}")
    print(f"Loan Purpose: {customer_data['loan_purpose']}\n")
    
    # Tier
    tier = result.get('loan_tier', 'N/A')
    tier_emoji = print_tier_emoji(tier)
    print(f"{tier_emoji} TIER: {tier}")
    print(f"   {result.get('tier_reason', 'N/A')}\n")
    
    # Approval status
    if result.get('approved'):
        print(f"LOAN APPROVED!")
        
        # Loan details
        loan_amount = result.get('loan_amount_vnd', 0)
        print(f" Maximum Loan Amount:")
        print(f"   {format_currency(loan_amount)}")
        print(f"   ({loan_amount:,.0f} VND)\n")
        
        monthly_payment = result.get('monthly_payment_vnd', 0)
        print(f"Monthly Payment:")
        print(f"   {format_currency(monthly_payment)}")
        print(f"   ({monthly_payment:,.0f} VND/month)\n")
        
        loan_term = result.get('loan_term_months', 0)
        print(f"Loan Term: {loan_term} months ({loan_term//12} years)")
        
        interest_rate = result.get('interest_rate', 0)
        print(f"Interest Rate: {interest_rate}% per year\n")
        
        credit_score = result.get('credit_score', 0)
        print(f"Credit Score: {credit_score}/850")
        
        risk_level = result.get('risk_level', 'N/A')
        risk_color = Colors.OKGREEN if risk_level == "Low" else Colors.WARNING
        print(f"Risk Level: {risk_level}\n")
        
        # Summary
        print(f" Message:")
        print(f"   {result.get('approval_message', 'N/A')}")
        
    else:
        print(f"LOAN REJECTED")
        
        credit_score = result.get('credit_score', 0)
        print(f"Credit Score: {credit_score}/850")
        
        risk_level = result.get('risk_level', 'N/A')
        print(f"Risk Level: {risk_level}")
        
        print(f"Reason:")
        print(f"   {result.get('approval_message', 'N/A')}")
    
    print("\n" + "=" * 70 + "\n")

def run_quick_demo():
    """Run quick demo with pre-defined scenarios"""
    scenarios = [
        {
            "name": "REJECTED - Poor Credit Profile",
            "data": {
                "full_name": "Nguyen Van X",
                "age": 20,
                "monthly_income": 5000000,
                "employment_status": "UNEMPLOYED",
                "years_employed": 0.0,
                "home_ownership": "RENT",
                "loan_purpose": "PERSONAL",
                "years_credit_history": 0,
                "has_previous_defaults": True,
                "currently_defaulting": True
            }
        },
        {
            "name": "BRONZE - Young Personal Borrower",
            "data": {
                "full_name": "Nguyen Van A",
                "age": 22,
                "monthly_income": 8000000,
                "employment_status": "EMPLOYED",
                "years_employed": 0.5,
                "home_ownership": "RENT",
                "loan_purpose": "PERSONAL",
                "years_credit_history": 0,
                "has_previous_defaults": False,
                "currently_defaulting": False
            }
        },
        {
            "name": "SILVER - Mid-Career Education",
            "data": {
                "full_name": "Tran Thi B",
                "age": 28,
                "monthly_income": 15000000,
                "employment_status": "EMPLOYED",
                "years_employed": 3.0,
                "home_ownership": "OWN",
                "loan_purpose": "EDUCATION",
                "years_credit_history": 4,
                "has_previous_defaults": False,
                "currently_defaulting": False
            }
        },
        {
            "name": "GOLD - Prime Car Buyer",
            "data": {
                "full_name": "Le Van C",
                "age": 35,
                "monthly_income": 20000000,
                "employment_status": "EMPLOYED",
                "years_employed": 7.0,
                "home_ownership": "MORTGAGE",
                "loan_purpose": "CAR",
                "years_credit_history": 8,
                "has_previous_defaults": False,
                "currently_defaulting": False
            }
        },
        {
            "name": "PLATINUM - Premium Home Buyer",
            "data": {
                "full_name": "Pham Thi D",
                "age": 40,
                "monthly_income": 30000000,
                "employment_status": "EMPLOYED",
                "years_employed": 10.0,
                "home_ownership": "MORTGAGE",
                "loan_purpose": "HOME",
                "years_credit_history": 12,
                "has_previous_defaults": False,
                "currently_defaulting": False
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print_header()
        print(f"{Colors.BOLD}Demo {i}/5: {scenario['name']}{Colors.ENDC}\n")
        
        try:
            response = requests.post(API_URL, json=scenario['data'], timeout=10)
            response.raise_for_status()
            result = response.json()
            display_result(result, scenario['data'])
            
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to API: {e}")
            print(f"\nMake sure the API is running at {API_URL}")
            return
        
        if i < len(scenarios):
            input(f"\nPress Enter for next demo...")

def run_custom_demo():
    """Run custom demo with user input"""
    print_header()
    customer_data = get_customer_input()
    
    print("\n Processing...")
    
    try:
        response = requests.post(API_URL, json=customer_data, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        print_header()
        display_result(result, customer_data)
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        print(f"\nMake sure the API is running at {API_URL}")

def show_comparison():
    """Show same customer, different purposes"""
    print_header()
    print(" COMPARISON DEMO - Same Customer, Different Purposes\n")
    
    base_customer = {
        "full_name": "Demo Customer - Premium Profile",
        "age": 35,
        "monthly_income": 25000000,
        "employment_status": "EMPLOYED",
        "years_employed": 8.0,
        "home_ownership": "MORTGAGE",
        "years_credit_history": 10,
        "has_previous_defaults": False,
        "currently_defaulting": False
    }
    
    purposes = ["PERSONAL", "EDUCATION", "CAR", "HOME"]
    
    print("Customer Profile:")
    print(f"  Age: {base_customer['age']}")
    print(f"  Monthly Income: {format_currency(base_customer['monthly_income'])}")
    print(f"  Employment: {base_customer['years_employed']} years")
    print(f"  Home: {base_customer['home_ownership']}\n")
    
    print("=" * 70)
    
    for purpose in purposes:
        customer_data = {**base_customer, "loan_purpose": purpose}
        
        try:
            response = requests.post(API_URL, json=customer_data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            tier_emoji = print_tier_emoji(result.get('loan_tier', ''))
            tier = result.get('loan_tier', 'N/A')
            loan_amount = result.get('loan_amount_vnd', 0)
            term = result.get('loan_term_months', 0)
            
            print(f"\n{purpose}")
            print(f"  {tier_emoji} Tier: {tier}")
            print(f"   Max Loan: {format_currency(loan_amount)}")
            print(f"  ⏱  Term: {term} months ({term//12} years)")
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 70 + "\n")
    input(f"Press Enter to continue...")

def main():
    """Main menu"""
    while True:
        print_header()
        print("Select Demo Mode:\n")
        print("  1. Quick Demo (4 pre-defined scenarios)")
        print("  2. Custom Input (enter your own data)")
        print("  3. Comparison Demo (same customer, different purposes)")
        print("  4. Exit\n")
        
        choice = input("Your choice (1-4): ").strip()
        
        if choice == "1":
            run_quick_demo()
            input(f"\nPress Enter to return to menu...")
        elif choice == "2":
            run_custom_demo()
            input(f"\nPress Enter to return to menu...")
        elif choice == "3":
            show_comparison()
        elif choice == "4":
            print(f"\nThank you for using the demo! \n")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    print(f"\n Make sure the API is running first!")
    print(f"Run: docker-compose up -d\n")
    
    try:
        # Test connection
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f" API is running!\n")
        input("Press Enter to start demo...")
        main()
    except:
        print(f" Cannot connect to API at {API_URL}")
        print(f"\nPlease start the API first:")
        print("  cd credit-scoring-api")
        print("  docker-compose up -d\n")
