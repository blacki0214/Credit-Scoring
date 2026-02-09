# Bureau Features - Data Dictionary

**Dataset**: `bureau_features_20251027_142231.parquet`  
**Location**: `bureau_features/bureau_features_20251027_142231.parquet`  
**Generated**: 2026-02-09 09:57:54

## Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Rows** | 305,811 |
| **Total Columns** | 26 |
| **Memory Usage** | 49.00 MB |

## Field Definitions

| Column Name | Description | Data Type | Non-Null Count | Null % | Unique Values | Mean | Min | Max | Std Dev |
|-------------|-------------|-----------|----------------|--------|---------------|------|-----|-----|---------|
| `SK_ID_CURR` | Unique identifier for each customer/loan application | `int32` | 305,811 | 0.0% | 305,811 | 278047.30 | 100001.00 | 456255.00 | 102849.57 |
| `total_credit_sum` | Total credit amount from all bureau records | `float64` | 305,811 | 0.0% | 236,496 | 1992466.07 | 0.00 | 1017957917.38 | 4165820.02 |
| `total_credit_debt` | Total current debt from bureau records | `float64` | 305,811 | 0.0% | 174,749 | 654129.20 | 0.00 | 334498331.20 | 1640573.41 |
| `active_loans_count` | Number of active loans in bureau | `float64` | 305,811 | 0.0% | 23 | 2.06 | 0.00 | 32.00 | 1.79 |
| `closed_loans_count` | Number of closed loans in bureau | `float64` | 305,811 | 0.0% | 57 | 3.53 | 0.00 | 108.00 | 3.43 |
| `credit_active_flag` | Flag indicating if customer has active credit | `int32` | 305,811 | 0.0% | 2 | 0.82 | 0.00 | 1.00 | 0.38 |
| `total_utilization` | Overall credit utilization ratio | `float64` | 296,233 | 3.1% | 213,493 | 0.29 | 0.00 | 1.50 | 0.29 |
| `oldest_account_m` | Age of oldest credit account in months | `float64` | 305,811 | 0.0% | 2,922 | 57.96 | 0.00 | 95.99 | 28.23 |
| `newest_account_m` | Age of newest credit account in months | `float64` | 305,811 | 0.0% | 2,923 | 16.13 | 0.00 | 95.99 | 17.53 |
| `aaoa_m` | Average age of accounts in months | `float64` | 305,811 | 0.0% | 69,801 | 35.60 | 0.00 | 95.99 | 18.35 |
| `max_overdue_ratio` | Maximum overdue amount ratio across all accounts | `float64` | 215,542 | 29.5% | 3,404 | 0.00 | 0.00 | 3.00 | 0.03 |
| `bureau_missing_flag` | Flag for missing bureau data | `int32` | 305,811 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `raw_bureau_records` | Number of bureau records for customer | `int64` | 305,811 | 0.0% | 64 | 5.61 | 1.00 | 116.00 | 4.43 |
| `raw_total_credit_sum` | Raw total credit sum before processing | `float64` | 305,809 | 0.0% | 236,496 | 1992479.10 | 0.00 | 1017957917.38 | 4165830.52 |
| `raw_total_credit_debt` | Raw total credit debt before processing | `float64` | 297,354 | 2.8% | 174,749 | 672733.19 | 0.00 | 334498331.20 | 1659974.04 |
| `raw_total_overdue_amount` | Total overdue amount across all accounts | `float64` | 305,811 | 0.0% | 1,369 | 212.79 | 0.00 | 3756681.00 | 15691.61 |
| `raw_max_overdue_amount` | Maximum overdue amount on any account | `float64` | 305,811 | 0.0% | 1,350 | 176.41 | 0.00 | 3756681.00 | 13686.50 |
| `raw_overdue_loans_count` | Number of loans with overdue amounts | `float64` | 305,811 | 0.0% | 8 | 0.01 | 0.00 | 8.00 | 0.13 |
| `raw_missing_credit_active_count` | Count of records with missing credit active status | `float64` | 305,811 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `raw_missing_credit_active_flag` | Flag for missing credit active status | `int32` | 305,811 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `raw_has_overdue_flag` | Flag indicating if customer has any overdue amounts | `int32` | 305,811 | 0.0% | 2 | 0.01 | 0.00 | 1.00 | 0.11 |
| `flag_negative_amount` | Flag for negative installment amounts | `int32` | 305,811 | 0.0% | 2 | 0.02 | 0.00 | 1.00 | 0.14 |
| `flag_unrealistic_credit` | Flag for unrealistic credit values | `int32` | 305,811 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.01 |
| `flag_negative_days_credit` | Flag for negative days credit values | `int32` | 305,811 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `flag_high_utilization` | Flag for high utilization (>100%) | `int32` | 305,811 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.02 |
| `flag_large_overdue_ratio` | Flag for large overdue ratio | `int32` | 305,811 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.01 |

## Value Distributions

### Key Flags

| Flag | Value | Count | Percentage |
|------|-------|-------|------------|
| `credit_active_flag` | 1 | 251,815 | 82.3% |
| `credit_active_flag` | 0 | 53,996 | 17.7% |
| `bureau_missing_flag` | 0 | 305,811 | 100.0% |
| `raw_missing_credit_active_flag` | 0 | 305,811 | 100.0% |
| `raw_has_overdue_flag` | 0 | 302,010 | 98.8% |
| `raw_has_overdue_flag` | 1 | 3,801 | 1.2% |
| `flag_negative_amount` | 0 | 299,925 | 98.1% |
| `flag_negative_amount` | 1 | 5,886 | 1.9% |
| `flag_unrealistic_credit` | 0 | 305,800 | 100.0% |
| `flag_unrealistic_credit` | 1 | 11 | 0.0% |
| `flag_negative_days_credit` | 0 | 305,811 | 100.0% |
| `flag_high_utilization` | 0 | 305,629 | 99.9% |
| `flag_high_utilization` | 1 | 182 | 0.1% |
| `flag_large_overdue_ratio` | 0 | 305,800 | 100.0% |
| `flag_large_overdue_ratio` | 1 | 11 | 0.0% |

