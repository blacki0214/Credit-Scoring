"""
Credit Scoring API - Demo CLI
Demonstrates the new 2-step loan application flow
"""
import requests
import json
from typing import Dict, Any
import os
import sys

# Try to use colorama for Windows compatibility
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    USE_COLORAMA = True
except ImportError:
    USE_COLORAMA = False
    print("Note: Install colorama for colored output: pip install colorama")

# API endpoints - Using cloud-hosted API
API_BASE = "https://credit-scoring-h7mv.onrender.com/api"
CALCULATE_LIMIT_URL = f"{API_BASE}/calculate-limit"
CALCULATE_TERMS_URL = f"{API_BASE}/calculate-terms"

# Color codes
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
    else:
        HEADER = OKBLUE = OKCYAN = OKGREEN = WARNING = FAIL = ENDC = BOLD = ''

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print demo header"""
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print("    CREDIT SCORING API - 2-STEP LOAN APPLICATION DEMO")
    print("=" * 70)
    print(f"{Colors.ENDC}\n")

def print_tier_emoji(tier: str) -> str:
    """Get emoji for tier"""
    emojis = {
        "BRONZE": "🥉",
        "SILVER": "🥈",
        "GOLD": "🥇",
        "PLATINUM": "🌟"
    }
    return emojis.get(tier, "")

def format_currency(amount: float) -> str:
    """Format amount in VND"""
    if amount >= 1_000_000_000:
        return f"{amount/1_000_000_000:.2f} ty VND"
    elif amount >= 1_000_000:
        return f"{amount/1_000_000:.0f} trieu VND"
    else:
        return f"{amount:,.0f} VND"

def get_customer_input() -> Dict[str, Any]:
    """Get customer information from user"""
    print(f"{Colors.OKBLUE}Enter Customer Information:{Colors.ENDC}\n")
    
    full_name = input("Full Name: ").strip() or "Nguyen Van A"
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
    home_choice = input("Select (1-4): ").strip() or "1"
    home_ownership = ["RENT", "OWN", "MORTGAGE", "LIVING_WITH_PARENTS"][int(home_choice) - 1]
    
    print("\nLoan Purpose:")
    print("  1. HOME")
    print("  2. CAR")
    print("  3. BUSINESS")
    print("  4. EDUCATION")
    print("  5. PERSONAL")
    purpose_choice = input("Select (1-5): ").strip() or "2"
    loan_purpose = ["HOME", "CAR", "BUSINESS", "EDUCATION", "PERSONAL"][int(purpose_choice) - 1]
    
    years_credit_history = float(input("\nYears of Credit History: ").strip() or "3")
    
    print("\nDefaults:")
    has_previous_defaults = input("Has Previous Defaults? (y/n): ").strip().lower() == 'y'
    currently_defaulting = input("Currently Defaulting? (y/n): ").strip().lower() == 'y'
    
    return {
        "full_name": full_name,
        "age": age,
        "monthly_income": monthly_income,
        "employment_status": employment_status,
        "years_employed": years_employed,
        "home_ownership": home_ownership,
        "loan_purpose": loan_purpose,
        "years_credit_history": years_credit_history,
        "has_previous_defaults": has_previous_defaults,
        "currently_defaulting": currently_defaulting
    }

def display_step1_result(data: Dict[str, Any]):
    """Display Step 1 results (loan limit)"""
    print(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}STEP 1 RESULTS - LOAN LIMIT CALCULATION{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")
    
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
        print(f"💵 Maximum Loan Amount:")
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
        print(f"💬 Message:")
        print(f"   {result.get('approval_message', 'N/A')}")
        
    else:
        print(f"  {Colors.FAIL}0 VND (Not Approved){Colors.ENDC}")
    
    # Risk Level
    risk = data['risk_level']
    risk_colors = {
        "Low": Colors.OKGREEN,
        "Medium": Colors.WARNING,
        "High": Colors.FAIL,
        "Very High": Colors.FAIL
    }   
    print(f"\n{Colors.BOLD}Risk Level:{Colors.ENDC}")
    print(f"  {risk_colors.get(risk, Colors.ENDC)}{risk}{Colors.ENDC}")
    
    # Message
    print(f"\n{Colors.BOLD}Message:{Colors.ENDC}")
    print(f"  {data['message']}")

def display_step2_result(data: Dict[str, Any], loan_amount: float):
    """Display Step 2 results (loan terms)"""
    print(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}STEP 2 RESULTS - LOAN TERMS{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Loan Details:{Colors.ENDC}")
    print(f"  Amount: {Colors.OKGREEN}{format_currency(loan_amount)}{Colors.ENDC}")
    print(f"  Purpose: {Colors.OKCYAN}{data['loan_purpose']}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Interest Rate:{Colors.ENDC}")
    print(f"  {Colors.OKBLUE}{data['interest_rate']}% per year{Colors.ENDC}")
    print(f"  {data['rate_explanation']}")
    
    print(f"\n{Colors.BOLD}Loan Term:{Colors.ENDC}")
    years = data['loan_term_months'] // 12
    months = data['loan_term_months'] % 12
    term_str = f"{years} years" if months == 0 else f"{years} years {months} months"
    print(f"  {Colors.OKCYAN}{data['loan_term_months']} months ({term_str}){Colors.ENDC}")
    print(f"  {data['term_explanation']}")
    
    print(f"\n{Colors.BOLD}Monthly Payment:{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}{format_currency(data['monthly_payment_vnd'])}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Total Payment:{Colors.ENDC}")
    print(f"  Total: {format_currency(data['total_payment_vnd'])}")
    print(f"  Interest: {format_currency(data['total_interest_vnd'])}")

def run_demo():
    """Run the demo"""
    print_header()
    
    # Check API connection
    try:
        response = requests.get(f"{API_BASE.replace('/api', '')}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"{Colors.FAIL}Error: API is not responding properly{Colors.ENDC}")
            return
        print(f"{Colors.OKGREEN}API is running!{Colors.ENDC}\n")
    except requests.exceptions.RequestException:
        print(f"{Colors.FAIL}Error: Cannot connect to API at {API_BASE}{Colors.ENDC}")
        print(f"{Colors.WARNING}Make sure the API is running: uvicorn app.main:app --reload{Colors.ENDC}")
        return
    
    # Get customer input
    customer_data = get_customer_input()
    
    print("\n🔄 Processing...")
    
    # STEP 1: Calculate Loan Limit
    try:
        response = requests.post(CALCULATE_LIMIT_URL, json=customer_data)
        response.raise_for_status()
        step1_data = response.json()
        
        display_step1_result(step1_data)
        
        if not step1_data['approved']:
            print(f"\n{Colors.FAIL}Application rejected. Cannot proceed to Step 2.{Colors.ENDC}")
            return
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        print(f"\nMake sure the API is running at {API_URL}")

def show_comparison():
    """Show same customer, different purposes"""
    print_header()
    print("📊 COMPARISON DEMO - Same Customer, Different Purposes\n")
    
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
            print(f"  💵 Max Loan: {format_currency(loan_amount)}")
            print(f"  ⏱️  Term: {term} months ({term//12} years)")
            
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
            print(f"\nThank you for using the demo! 👋\n")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    print(f"\n⚠️ Make sure the API is running first!")
    print(f"Run: docker-compose up -d\n")
    
    try:
        # Test connection
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"✅ API is running!\n")
        input("Press Enter to start demo...")
        main()
    except:
        print(f"❌ Cannot connect to API at {API_URL}")
        print(f"\nPlease start the API first:")
        print("  cd credit-scoring-api")
        print("  docker-compose up -d\n")
