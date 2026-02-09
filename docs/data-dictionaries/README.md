# Data Dictionaries

This directory contains comprehensive data dictionaries for all datasets used in the Credit Scoring AI project.

## Available Dictionaries

### 1. [Application Train Features](application_train_features.md)
**Records**: 307,511 | **Fields**: 30 | **Size**: 47.22 MB

Main application dataset containing customer information and loan details.

**Key Features**:
- Customer demographics (age, family size)
- Employment and income information
- Loan details (credit amount, annuity, goods price)
- Derived ratios (credit-to-income, payment burden)
- Data quality flags

**Target Variable**: 8.1% default rate

---

### 2. [Bureau Features](bureau_features.md)
**Records**: 305,811 | **Fields**: 26

Credit bureau information from external credit reporting agencies.

**Key Features**:
- Total credit and debt amounts
- Active and closed loan counts
- Credit utilization metrics
- Account age information
- Overdue payment indicators

---

### 3. [Credit Card Balance Features](credit_card_balance_features.md)
**Records**: 103,558 | **Fields**: 31

Credit card usage patterns and payment behavior (33.7% coverage).

**Key Features**:
- Credit card utilization (average and maximum)
- Payment and ATM withdrawal ratios
- Active month ratios
- Overdue flags
- Balance and limit information

---

### 4. [Installments Payments Features](installments_payments_features.md)
**Records**: 339,587 | **Fields**: 27

Payment history from installment loans.

**Key Features**:
- Days past due metrics (mean, max)
- On-time payment ratios
- Payment variance and early payment behavior
- Total installment and payment amounts
- Payment anomaly flags

---

## Dictionary Format

Each data dictionary contains:

### Dataset Overview
- Total rows, columns, and memory usage

### Field Definitions Table
For each field:
- **Column Name**: Field identifier
- **Description**: Business meaning and purpose
- **Data Type**: int32, float64, bool, etc.
- **Non-Null Count**: Number of non-missing values
- **Null %**: Percentage of missing values
- **Unique Values**: Cardinality
- **Statistics**: Mean, Min, Max, Std Dev (for numeric fields)

### Value Distributions
- Target variable distribution
- Key flag distributions

## Feature Categories

### Demographics
- `age_years`, `raw_cnt_fam_members`

### Financial Information
- `raw_income_total`, `raw_credit_amt`, `raw_annuity_amt`, `raw_goods_price`

### Employment
- `employment_years`, `has_job_flag`, `raw_days_employed`

### Derived Ratios
- `annuity_income_ratio` - Payment burden indicator
- `credit_income_ratio` - Credit affordability
- `goods_income_ratio` - Purchase affordability
- `income_per_person` - Per capita income

### Credit Bureau
- `total_credit_sum`, `total_credit_debt`
- `active_loans_count`, `closed_loans_count`
- `total_utilization`, `max_overdue_ratio`

### Credit Card Behavior
- `cc_avg_utilization`, `cc_max_utilization`
- `cc_payment_ratio`, `cc_atm_draw_ratio`
- `cc_has_overdue_flag`

### Payment History
- `dpd_mean`, `dpd_max` - Days past due
- `on_time_ratio` - Payment timeliness
- `ins_payment_ratio` - Payment completeness

### Data Quality Flags
- `missing_feature_flag_*` - Missing value indicators
- `*_outlier_flag` - Outlier indicators
- `flag_*` - Various data quality issues

## Usage

These dictionaries are essential for:
- **Model Development**: Understanding input features
- **Feature Engineering**: Creating new derived features
- **Model Interpretation**: Explaining predictions
- **Documentation**: Technical specifications and model cards
- **Onboarding**: Training new team members
- **Debugging**: Investigating data pipeline issues

## Notes

- **Missing Values**: Flagged with dedicated indicator columns
- **Outliers**: Capped at specific thresholds with outlier flags
- **Target Variable**: Only in Application Train Features (8.1% default rate)
- **Coverage**: Not all customers have bureau, credit card, or installment data

---

**Last Updated**: 2026-02-09  
**Project**: Credit Scoring AI  
**Maintained By**: Data Science Team
