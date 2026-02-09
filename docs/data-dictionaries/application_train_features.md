# Application Train Features - Data Dictionary

**Dataset**: `application_features_20251027_141620.parquet`  
**Location**: `application_train_features/application_features_20251027_141620.parquet`  
**Generated**: 2026-02-09 09:57:54

## Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Rows** | 307,511 |
| **Total Columns** | 30 |
| **Memory Usage** | 47.22 MB |

## Field Definitions

| Column Name | Description | Data Type | Non-Null Count | Null % | Unique Values | Mean | Min | Max | Std Dev |
|-------------|-------------|-----------|----------------|--------|---------------|------|-----|-----|---------|
| `SK_ID_CURR` | Unique identifier for each customer/loan application | `int32` | 307,511 | 0.0% | 307,511 | 278180.52 | 100002.00 | 456255.00 | 102790.18 |
| `TARGET` | Target variable indicating loan default (True = default, False = no default) | `bool` | 307,511 | 0.0% | 2 | 0.08 | 0.00 | 1.00 | 0.27 |
| `age_years` | Customer age in years | `int32` | 307,511 | 0.0% | 49 | 43.91 | 21.00 | 69.00 | 11.96 |
| `raw_days_employed` | Number of days employed (negative values, 0 = current) | `float64` | 252,137 | 18.0% | 12,573 | -2384.17 | -17912.00 | 0.00 | 2338.36 |
| `employment_years` | Years of employment (derived from raw_days_employed) | `float64` | 252,137 | 18.0% | 12,573 | 6.53 | 0.00 | 49.04 | 6.40 |
| `raw_income_total` | Total annual income of the customer | `float64` | 307,511 | 0.0% | 2,210 | 162626.95 | 25650.00 | 337500.00 | 73303.15 |
| `raw_credit_amt` | Credit amount requested for the loan | `float64` | 307,511 | 0.0% | 4,969 | 592313.04 | 45000.00 | 1616625.00 | 380316.24 |
| `raw_annuity_amt` | Loan annuity (monthly payment amount) | `float64` | 307,499 | 0.0% | 11,674 | 26797.73 | 1615.50 | 61704.00 | 13281.54 |
| `raw_goods_price` | Price of goods for which the loan is given | `float64` | 307,233 | 0.1% | 781 | 527925.77 | 40500.00 | 1341000.00 | 337154.66 |
| `raw_cnt_fam_members` | Number of family members | `float64` | 307,509 | 0.0% | 17 | 2.15 | 1.00 | 20.00 | 0.91 |
| `annuity_income_ratio` | Ratio of annuity to income (payment burden) | `float64` | 307,499 | 0.0% | 82,170 | 0.18 | 0.01 | 1.50 | 0.09 |
| `annuity_income_outlier_flag` | Flag indicating if annuity/income ratio is an outlier | `int32` | 307,511 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.00 |
| `credit_income_ratio` | Ratio of credit amount to income | `float64` | 307,511 | 0.0% | 29,622 | 3.31 | 0.13 | 5.00 | 1.42 |
| `credit_income_outlier_flag` | Flag indicating if credit/income ratio is an outlier | `int32` | 307,511 | 0.0% | 2 | 0.26 | 0.00 | 1.00 | 0.44 |
| `goods_income_ratio` | Ratio of goods price to income | `float64` | 307,233 | 0.1% | 7,563 | 3.08 | 0.13 | 5.00 | 1.42 |
| `goods_income_outlier_flag` | Flag indicating if goods/income ratio is an outlier | `int32` | 307,511 | 0.0% | 2 | 0.20 | 0.00 | 1.00 | 0.40 |
| `income_per_person` | Income per family member | `float64` | 307,509 | 0.0% | 2,716 | 89924.40 | 2812.50 | 337500.00 | 58441.74 |
| `has_job_flag` | Flag indicating if customer has employment (1 = yes, 0 = no) | `int32` | 307,511 | 0.0% | 2 | 0.82 | 0.00 | 1.00 | 0.38 |
| `missing_feature_flag_income` | Flag for missing income data | `int32` | 307,511 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `missing_feature_flag_credit` | Flag for missing credit amount data | `int32` | 307,511 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `missing_feature_flag_annuity` | Flag for missing annuity data | `int32` | 307,511 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.01 |
| `missing_feature_flag_goods_price` | Flag for missing goods price data | `int32` | 307,511 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.03 |
| `missing_feature_flag_family` | Flag for missing family member count | `int32` | 307,511 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.00 |
| `missing_feature_flag_employment` | Flag for missing employment data | `int32` | 307,511 | 0.0% | 2 | 0.18 | 0.00 | 1.00 | 0.38 |
| `raw_income_nonpositive_flag` | Flag for non-positive income values | `int32` | 307,511 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `raw_credit_negative_flag` | Flag for negative credit amounts | `int32` | 307,511 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `raw_annuity_negative_flag` | Flag for negative annuity amounts | `int32` | 307,511 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `raw_goods_nonpositive_flag` | Flag for non-positive goods prices | `int32` | 307,511 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `raw_family_nonpositive_flag` | Flag for non-positive family member count | `int32` | 307,511 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `raw_employment_placeholder_flag` | Flag for placeholder employment values | `int32` | 307,511 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |

## Value Distributions

### TARGET (Loan Default)

| Value | Count | Percentage |
|-------|-------|------------|
| No Default (`False`) | 282,686 | 91.9% |
| Default (`True`) | 24,825 | 8.1% |

### Key Flags

| Flag | Value | Count | Percentage |
|------|-------|-------|------------|
| `annuity_income_outlier_flag` | 0 | 307,510 | 100.0% |
| `annuity_income_outlier_flag` | 1 | 1 | 0.0% |
| `credit_income_outlier_flag` | 0 | 227,387 | 73.9% |
| `credit_income_outlier_flag` | 1 | 80,124 | 26.1% |
| `goods_income_outlier_flag` | 0 | 246,965 | 80.3% |
| `goods_income_outlier_flag` | 1 | 60,546 | 19.7% |
| `has_job_flag` | 1 | 252,137 | 82.0% |
| `has_job_flag` | 0 | 55,374 | 18.0% |
| `missing_feature_flag_income` | 0 | 307,511 | 100.0% |
| `missing_feature_flag_credit` | 0 | 307,511 | 100.0% |
| `missing_feature_flag_annuity` | 0 | 307,499 | 100.0% |
| `missing_feature_flag_annuity` | 1 | 12 | 0.0% |
| `missing_feature_flag_goods_price` | 0 | 307,233 | 99.9% |
| `missing_feature_flag_goods_price` | 1 | 278 | 0.1% |
| `missing_feature_flag_family` | 0 | 307,509 | 100.0% |
| `missing_feature_flag_family` | 1 | 2 | 0.0% |
| `missing_feature_flag_employment` | 0 | 252,137 | 82.0% |
| `missing_feature_flag_employment` | 1 | 55,374 | 18.0% |

