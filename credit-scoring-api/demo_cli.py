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

def display_step1_result(data: Dict[str, Any], customer_data: Dict[str, Any]):
    """Display Step 1 results (loan limit)"""
    print(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}STEP 1 RESULTS - LOAN LIMIT CALCULATION{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")
    
    # Customer info
    print(f"Customer: {customer_data['full_name']}")
    print(f"Monthly Income: {format_currency(customer_data['monthly_income'])}")
    print(f"Loan Purpose: {customer_data['loan_purpose']}\n")
    
    # Approval status
    if data.get('approved'):
        print(f"{Colors.OKGREEN}✅ LOAN APPROVED!{Colors.ENDC}\n")
        
        # Loan details
        loan_amount = data.get('max_loan_amount_vnd', 0)
        print(f"{Colors.BOLD}💵 Maximum Loan Amount:{Colors.ENDC}")
        print(f"   {Colors.OKGREEN}{format_currency(loan_amount)}{Colors.ENDC}")
        print(f"   ({loan_amount:,.0f} VND)\n")
        
        credit_score = data.get('credit_score', 0)
        print(f"{Colors.BOLD}Credit Score:{Colors.ENDC} {credit_score}/850")
        
        risk_level = data.get('risk_level', 'N/A')
        risk_colors = {
            "Low": Colors.OKGREEN,
            "Medium": Colors.WARNING,
            "High": Colors.FAIL,
            "Very High": Colors.FAIL
        }
        risk_color = risk_colors.get(risk_level, Colors.ENDC)
        print(f"{Colors.BOLD}Risk Level:{Colors.ENDC} {risk_color}{risk_level}{Colors.ENDC}\n")
        
        # Message
        print(f"{Colors.BOLD}💬 Message:{Colors.ENDC}")
        print(f"   {data.get('message', 'N/A')}")
        
    else:
        print(f"{Colors.FAIL}❌ LOAN NOT APPROVED{Colors.ENDC}\n")
        print(f"{Colors.BOLD}Reason:{Colors.ENDC}")
        print(f"   {data.get('message', 'Application does not meet minimum requirements')}")

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
        print(f"{Colors.OKCYAN}⏳ Connecting to cloud API (this may take 30-60 seconds on first request)...{Colors.ENDC}")
        response = requests.get(f"{API_BASE.replace('/api', '')}/api/health", timeout=60)
        if response.status_code != 200:
            print(f"{Colors.FAIL}Error: API is not responding properly{Colors.ENDC}")
            return
        print(f"{Colors.OKGREEN}✅ API is running!{Colors.ENDC}\n")
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}Error: Cannot connect to API at {API_BASE}{Colors.ENDC}")
        print(f"{Colors.WARNING}Error details: {str(e)}{Colors.ENDC}")
        return
    
    # Get customer input
    customer_data = get_customer_input()
    
    print("\n🔄 Processing...")
    
    # STEP 1: Calculate Loan Limit
    try:
        print(f"{Colors.OKCYAN}⏳ Calculating loan limit...{Colors.ENDC}")
        response = requests.post(CALCULATE_LIMIT_URL, json=customer_data, timeout=60)
        response.raise_for_status()
        step1_data = response.json()
        
        display_step1_result(step1_data, customer_data)
        
        if not step1_data['approved']:
            print(f"\n{Colors.FAIL}Application rejected. Cannot proceed to Step 2.{Colors.ENDC}")
            return
        
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}Error connecting to API: {e}{Colors.ENDC}")
        return

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
            response = requests.post(CALCULATE_LIMIT_URL, json=customer_data, timeout=10)
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
        print("  1. Custom Input (enter your own data)")
        print("  2. Comparison Demo (same customer, different purposes)")
        print("  3. Exit\n")
        
        choice = input("Your choice (1-3): ").strip()
        
        if choice == "1":
            run_demo()
            input(f"\nPress Enter to return to menu...")
        elif choice == "2":
            show_comparison()
        elif choice == "3":
            print(f"\nThank you for using the demo! 👋\n")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    print(f"\n🌐 Connecting to Cloud API...")
    print(f"API Endpoint: {API_BASE}\n")
    
    try:
        # Test connection to cloud API
        print(f"{Colors.OKCYAN}⏳ Testing connection (this may take 30-60 seconds on first request)...{Colors.ENDC}")
        response = requests.get(f"{API_BASE.replace('/api', '')}/api/health", timeout=60)
        print(f"{Colors.OKGREEN}✅ Connected to cloud API: {API_BASE}{Colors.ENDC}\n")
        input("Press Enter to start demo...")
        main()
    except Exception as e:
        print(f"{Colors.FAIL}❌ Cannot connect to API at {API_BASE}{Colors.ENDC}")
        print(f"{Colors.WARNING}Error: {str(e)}{Colors.ENDC}")
        print(f"\nPlease check your internet connection or try again later.\n")
