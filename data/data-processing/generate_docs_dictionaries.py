import pandas as pd
from pathlib import Path
from datetime import datetime

# Feature descriptions mapping
FEATURE_DESCRIPTIONS = {
    # Application Features
    'SK_ID_CURR': 'Unique identifier for each customer/loan application',
    'TARGET': 'Target variable indicating loan default (True = default, False = no default)',
    'age_years': 'Customer age in years',
    'raw_days_employed': 'Number of days employed (negative values, 0 = current)',
    'employment_years': 'Years of employment (derived from raw_days_employed)',
    'raw_income_total': 'Total annual income of the customer',
    'raw_credit_amt': 'Credit amount requested for the loan',
    'raw_annuity_amt': 'Loan annuity (monthly payment amount)',
    'raw_goods_price': 'Price of goods for which the loan is given',
    'raw_cnt_fam_members': 'Number of family members',
    'annuity_income_ratio': 'Ratio of annuity to income (payment burden)',
    'annuity_income_outlier_flag': 'Flag indicating if annuity/income ratio is an outlier',
    'credit_income_ratio': 'Ratio of credit amount to income',
    'credit_income_outlier_flag': 'Flag indicating if credit/income ratio is an outlier',
    'goods_income_ratio': 'Ratio of goods price to income',
    'goods_income_outlier_flag': 'Flag indicating if goods/income ratio is an outlier',
    'income_per_person': 'Income per family member',
    'has_job_flag': 'Flag indicating if customer has employment (1 = yes, 0 = no)',
    'missing_feature_flag_income': 'Flag for missing income data',
    'missing_feature_flag_credit': 'Flag for missing credit amount data',
    'missing_feature_flag_annuity': 'Flag for missing annuity data',
    'missing_feature_flag_goods_price': 'Flag for missing goods price data',
    'missing_feature_flag_family': 'Flag for missing family member count',
    'missing_feature_flag_employment': 'Flag for missing employment data',
    'raw_income_nonpositive_flag': 'Flag for non-positive income values',
    'raw_credit_negative_flag': 'Flag for negative credit amounts',
    'raw_annuity_negative_flag': 'Flag for negative annuity amounts',
    'raw_goods_nonpositive_flag': 'Flag for non-positive goods prices',
    'raw_family_nonpositive_flag': 'Flag for non-positive family member count',
    'raw_employment_placeholder_flag': 'Flag for placeholder employment values',
    
    # Bureau Features
    'total_credit_sum': 'Total credit amount from all bureau records',
    'total_credit_debt': 'Total current debt from bureau records',
    'active_loans_count': 'Number of active loans in bureau',
    'closed_loans_count': 'Number of closed loans in bureau',
    'credit_active_flag': 'Flag indicating if customer has active credit',
    'total_utilization': 'Overall credit utilization ratio',
    'oldest_account_m': 'Age of oldest credit account in months',
    'newest_account_m': 'Age of newest credit account in months',
    'aaoa_m': 'Average age of accounts in months',
    'max_overdue_ratio': 'Maximum overdue amount ratio across all accounts',
    'bureau_missing_flag': 'Flag for missing bureau data',
    'raw_bureau_records': 'Number of bureau records for customer',
    'raw_total_credit_sum': 'Raw total credit sum before processing',
    'raw_total_credit_debt': 'Raw total credit debt before processing',
    'raw_total_overdue_amount': 'Total overdue amount across all accounts',
    'raw_max_overdue_amount': 'Maximum overdue amount on any account',
    'raw_overdue_loans_count': 'Number of loans with overdue amounts',
    'raw_missing_credit_active_count': 'Count of records with missing credit active status',
    'raw_missing_credit_active_flag': 'Flag for missing credit active status',
    'raw_has_overdue_flag': 'Flag indicating if customer has any overdue amounts',
    'flag_negative_amount': 'Flag for negative credit amounts in bureau',
    'flag_unrealistic_credit': 'Flag for unrealistic credit values',
    'flag_negative_days_credit': 'Flag for negative days credit values',
    'flag_high_utilization': 'Flag for high credit utilization (>100%)',
    'flag_large_overdue_ratio': 'Flag for large overdue ratio',
    
    # Credit Card Features
    'cc_avg_utilization': 'Average credit card utilization across all months',
    'cc_max_utilization': 'Maximum credit card utilization observed',
    'cc_payment_ratio': 'Ratio of payments to balance',
    'cc_atm_draw_ratio': 'Ratio of ATM withdrawals to total drawings',
    'cc_total_months': 'Total months of credit card history',
    'cc_active_month_ratio': 'Ratio of active months to total months',
    'cc_has_overdue_flag': 'Flag indicating if customer had credit card overdue',
    'missing_limit_flag': 'Flag for missing credit limit data',
    'flag_negative_balance': 'Flag for negative balance observations',
    'flag_invalid_limit': 'Flag for invalid credit limit values',
    'flag_high_utilization': 'Flag for high utilization (>100%)',
    'flag_overpayment': 'Flag for overpayment observations',
    'flag_negative_draw': 'Flag for negative drawing amounts',
    'flag_dpd_error': 'Flag for days past due errors',
    'flag_small_balance_payment': 'Flag for small balance with large payment',
    'raw_cc_records': 'Number of credit card records',
    'raw_limit_max': 'Maximum credit limit observed',
    'raw_limit_min': 'Minimum credit limit observed',
    'raw_limit_avg': 'Average credit limit',
    'raw_balance_max': 'Maximum balance observed',
    'raw_balance_avg': 'Average balance',
    'raw_total_payment': 'Total payments made',
    'raw_total_drawings': 'Total drawings/purchases',
    'raw_total_atm_drawings': 'Total ATM withdrawals',
    'raw_overdue_months': 'Number of months with overdue status',
    'raw_max_dpd': 'Maximum days past due',
    'raw_invalid_limit_months': 'Number of months with invalid limits',
    'raw_invalid_limit_flag': 'Flag for invalid limit presence',
    'raw_negative_balance_months': 'Number of months with negative balance',
    'raw_negative_balance_flag': 'Flag for negative balance presence',
    
    # Installments Features
    'dpd_mean': 'Average days past due across all installments',
    'dpd_max': 'Maximum days past due observed',
    'on_time_ratio': 'Ratio of on-time payments to total payments',
    'num_payments': 'Total number of installment payments',
    'dpd_gt30_flag': 'Flag indicating if any payment was >30 days late',
    'ins_payment_ratio': 'Ratio of actual payment to expected installment',
    'ins_payment_variance': 'Variance in payment amounts',
    'ins_early_ratio': 'Ratio of early payments',
    'installment_missing_flag': 'Flag for missing installment data',
    'flag_negative_amount': 'Flag for negative installment amounts',
    'flag_overpayment': 'Flag for overpayment observations',
    'flag_missing_amount': 'Flag for missing payment amounts',
    'flag_missing_days': 'Flag for missing payment days',
    'flag_unrealistic_delay': 'Flag for unrealistic payment delays',
    'raw_total_instalment': 'Total expected installment amount',
    'raw_total_payment': 'Total actual payment amount',
    'raw_payments_count': 'Count of payment records',
    'raw_instalments_count': 'Count of installment records',
    'raw_on_time_count': 'Count of on-time payments',
    'raw_late_count': 'Count of late payments',
    'raw_max_dpd': 'Maximum days past due (raw)',
    'raw_payment_ratio_obs': 'Observed payment ratio',
    'raw_missing_amount_rows': 'Number of rows with missing amounts',
    'raw_missing_days_rows': 'Number of rows with missing days',
    'raw_missing_amount_flag': 'Flag for missing amount presence',
    'raw_missing_days_flag': 'Flag for missing days presence',
}

def create_data_dictionary_table(file_path, dataset_name, output_dir):
    """Create a data dictionary in table format"""
    
    try:
        df = pd.read_parquet(file_path)
        
        # Create output directory if it doesn't exist
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Start markdown content
        md_content = f"""# {dataset_name} - Data Dictionary

**Dataset**: `{Path(file_path).name}`  
**Location**: `{file_path}`  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Rows** | {df.shape[0]:,} |
| **Total Columns** | {df.shape[1]} |
| **Memory Usage** | {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB |

## Field Definitions

| Column Name | Description | Data Type | Non-Null Count | Null % | Unique Values | Mean | Min | Max | Std Dev |
|-------------|-------------|-----------|----------------|--------|---------------|------|-----|-----|---------|
"""
        
        # Add each column
        for col in df.columns:
            description = FEATURE_DESCRIPTIONS.get(col, 'Feature description not available')
            dtype = str(df[col].dtype)
            non_null = df[col].count()
            null_pct = f"{df[col].isnull().sum() / len(df) * 100:.1f}%"
            unique = df[col].nunique()
            
            # Statistics for numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                mean = f"{df[col].mean():.2f}" if not pd.isna(df[col].mean()) else "N/A"
                min_val = f"{df[col].min():.2f}" if not pd.isna(df[col].min()) else "N/A"
                max_val = f"{df[col].max():.2f}" if not pd.isna(df[col].max()) else "N/A"
                std = f"{df[col].std():.2f}" if not pd.isna(df[col].std()) else "N/A"
            else:
                mean = "N/A"
                min_val = "N/A"
                max_val = "N/A"
                std = "N/A"
            
            md_content += f"| `{col}` | {description} | `{dtype}` | {non_null:,} | {null_pct} | {unique:,} | {mean} | {min_val} | {max_val} | {std} |\n"
        
        # Add value distributions for important categorical fields
        md_content += "\n## Value Distributions\n\n"
        
        # Check for TARGET variable
        if 'TARGET' in df.columns:
            md_content += "### TARGET (Loan Default)\n\n"
            md_content += "| Value | Count | Percentage |\n"
            md_content += "|-------|-------|------------|\n"
            for val, count in df['TARGET'].value_counts().items():
                pct = count / len(df) * 100
                label = "Default" if val else "No Default"
                md_content += f"| {label} (`{val}`) | {count:,} | {pct:.1f}% |\n"
            md_content += "\n"
        
        # Add flag distributions
        flag_cols = [col for col in df.columns if 'flag' in col.lower() and df[col].nunique() <= 5]
        if flag_cols:
            md_content += "### Key Flags\n\n"
            md_content += "| Flag | Value | Count | Percentage |\n"
            md_content += "|------|-------|-------|------------|\n"
            for col in flag_cols[:10]:  # Limit to first 10 flags
                for val, count in df[col].value_counts().items():
                    pct = count / len(df) * 100
                    md_content += f"| `{col}` | {val} | {count:,} | {pct:.1f}% |\n"
            md_content += "\n"
        
        # Save to file
        output_filename = dataset_name.lower().replace(' ', '_').replace('(', '').replace(')', '') + '.md'
        output_path = output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return output_path, True, None
        
    except Exception as e:
        return None, False, str(e)

# Define datasets
datasets = [
    ('application_train_features/application_features_20251027_141620.parquet', 'Application Train Features'),
    ('bureau_features/bureau_features_20251027_142231.parquet', 'Bureau Features'),
    ('credit_card_balance_features/credit_card_features_20251027_142534.parquet', 'Credit Card Balance Features'),
    ('installments_payments_features/installments_features_20251027_142834.parquet', 'Installments Payments Features'),
    ('flat_table/flat_credit_model_20251027_143321.parquet', 'Flat Table Combined'),
]

# Output directory
output_dir = '../../docs/data-dictionaries'

print("Generating data dictionaries for documentation...\n")
print("=" * 80)

results = []

for file_path, dataset_name in datasets:
    print(f"\nProcessing: {dataset_name}")
    print("-" * 80)
    
    output_path, success, error = create_data_dictionary_table(file_path, dataset_name, output_dir)
    
    if success:
        print(f"✓ Success: {output_path}")
        results.append((dataset_name, output_path, True))
    else:
        print(f"✗ Error: {error}")
        results.append((dataset_name, None, False))

print("\n" + "=" * 80)
print("\nSummary:")
print("-" * 80)

successful = sum(1 for _, _, success in results if success)
print(f"Successfully generated: {successful}/{len(datasets)} dictionaries")
print(f"Output directory: {Path(output_dir).absolute()}")

print("\nGenerated files:")
for name, path, success in results:
    if success:
        print(f"  ✓ {path}")
    else:
        print(f"  ✗ {name} (failed)")
