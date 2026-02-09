# Credit Card Balance Features - Data Dictionary

**Dataset**: `credit_card_features_20251027_142534.parquet`  
**Location**: `credit_card_balance_features/credit_card_features_20251027_142534.parquet`  
**Generated**: 2026-02-09 09:57:55

## Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Rows** | 103,558 |
| **Total Columns** | 31 |
| **Memory Usage** | 19.36 MB |

## Field Definitions

| Column Name | Description | Data Type | Non-Null Count | Null % | Unique Values | Mean | Min | Max | Std Dev |
|-------------|-------------|-----------|----------------|--------|---------------|------|-----|-----|---------|
| `SK_ID_CURR` | Unique identifier for each customer/loan application | `int32` | 103,558 | 0.0% | 103,558 | 278381.46 | 100006.00 | 456250.00 | 102779.52 |
| `cc_avg_utilization` | Average credit card utilization across all months | `float64` | 102,445 | 1.1% | 69,723 | 0.32 | 0.00 | 2.14 | 0.32 |
| `cc_max_utilization` | Maximum credit card utilization observed | `float64` | 102,445 | 1.1% | 65,671 | 0.62 | 0.00 | 11.78 | 0.48 |
| `cc_payment_ratio` | Ratio of payments to balance | `float64` | 67,658 | 34.7% | 67,169 | 0.29 | 0.00 | 9.86 | 0.56 |
| `cc_atm_draw_ratio` | Ratio of ATM withdrawals to total drawings | `float64` | 70,264 | 32.2% | 28,747 | 0.63 | 0.00 | 1.00 | 0.39 |
| `cc_total_months` | Total months of credit card history | `int64` | 103,558 | 0.0% | 96 | 37.01 | 1.00 | 96.00 | 33.40 |
| `cc_active_month_ratio` | Ratio of active months to total months | `float64` | 72,397 | 30.1% | 1,974 | 0.86 | 0.00 | 1.87 | 0.21 |
| `cc_has_overdue_flag` | Flag indicating if customer had credit card overdue | `int32` | 103,558 | 0.0% | 2 | 0.20 | 0.00 | 1.00 | 0.40 |
| `missing_limit_flag` | Flag for missing credit limit data | `int32` | 103,558 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `flag_negative_balance` | Flag for negative balance observations | `int32` | 103,558 | 0.0% | 2 | 0.01 | 0.00 | 1.00 | 0.08 |
| `flag_invalid_limit` | Flag for invalid credit limit values | `int32` | 103,558 | 0.0% | 2 | 0.24 | 0.00 | 1.00 | 0.43 |
| `flag_high_utilization` | Flag for high utilization (>100%) | `int32` | 103,558 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.03 |
| `flag_overpayment` | Flag for overpayment observations | `int32` | 103,558 | 0.0% | 2 | 0.52 | 0.00 | 1.00 | 0.50 |
| `flag_negative_draw` | Flag for negative drawing amounts | `int32` | 103,558 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.01 |
| `flag_dpd_error` | Flag for days past due errors | `int32` | 103,558 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `flag_small_balance_payment` | Flag for small balance with large payment | `int32` | 103,558 | 0.0% | 2 | 0.47 | 0.00 | 1.00 | 0.50 |
| `raw_cc_records` | Number of credit card records | `int64` | 103,558 | 0.0% | 132 | 37.08 | 1.00 | 192.00 | 33.48 |
| `raw_limit_max` | Maximum credit limit observed | `float64` | 103,558 | 0.0% | 54 | 249504.88 | 0.00 | 1350000.00 | 201189.09 |
| `raw_limit_min` | Minimum credit limit observed | `float64` | 103,558 | 0.0% | 180 | 149529.21 | 0.00 | 1350000.00 | 198557.63 |
| `raw_limit_avg` | Average credit limit | `float64` | 103,558 | 0.0% | 13,036 | 207320.67 | 0.00 | 1350000.00 | 190229.28 |
| `raw_balance_max` | Maximum balance observed | `float64` | 103,558 | 0.0% | 66,374 | 142297.93 | 0.00 | 1505902.19 | 171325.54 |
| `raw_balance_avg` | Average balance | `float64` | 103,558 | 0.0% | 70,095 | 69973.19 | -2930.23 | 928686.32 | 107537.81 |
| `raw_total_payment` | Total actual payment amount | `float64` | 72,120 | 30.4% | 63,796 | 437952.62 | 0.00 | 30073144.10 | 522350.37 |
| `raw_total_drawings` | Total drawings/purchases | `float64` | 103,558 | 0.0% | 47,447 | 275657.41 | -1687.50 | 30293320.14 | 455668.25 |
| `raw_total_atm_drawings` | Total ATM withdrawals | `float64` | 72,194 | 30.3% | 5,347 | 255193.65 | 0.00 | 8384850.00 | 321426.60 |
| `raw_overdue_months` | Number of months with overdue status | `float64` | 103,558 | 0.0% | 91 | 1.48 | 0.00 | 94.00 | 6.12 |
| `raw_max_dpd` | Maximum days past due (raw) | `int32` | 103,558 | 0.0% | 438 | 16.40 | 0.00 | 3260.00 | 141.97 |
| `raw_invalid_limit_months` | Number of months with invalid limits | `float64` | 103,558 | 0.0% | 82 | 7.28 | 0.00 | 89.00 | 18.34 |
| `raw_invalid_limit_flag` | Flag for invalid limit presence | `int32` | 103,558 | 0.0% | 2 | 0.24 | 0.00 | 1.00 | 0.43 |
| `raw_negative_balance_months` | Number of months with negative balance | `float64` | 103,558 | 0.0% | 9 | 0.02 | 0.00 | 8.00 | 0.36 |
| `raw_negative_balance_flag` | Flag for negative balance presence | `int32` | 103,558 | 0.0% | 2 | 0.01 | 0.00 | 1.00 | 0.08 |

## Value Distributions

### Key Flags

| Flag | Value | Count | Percentage |
|------|-------|-------|------------|
| `cc_has_overdue_flag` | 0 | 82,898 | 80.0% |
| `cc_has_overdue_flag` | 1 | 20,660 | 20.0% |
| `missing_limit_flag` | 0 | 103,558 | 100.0% |
| `flag_negative_balance` | 0 | 102,914 | 99.4% |
| `flag_negative_balance` | 1 | 644 | 0.6% |
| `flag_invalid_limit` | 0 | 78,241 | 75.6% |
| `flag_invalid_limit` | 1 | 25,317 | 24.4% |
| `flag_high_utilization` | 0 | 103,487 | 99.9% |
| `flag_high_utilization` | 1 | 71 | 0.1% |
| `flag_overpayment` | 1 | 53,547 | 51.7% |
| `flag_overpayment` | 0 | 50,011 | 48.3% |
| `flag_negative_draw` | 0 | 103,554 | 100.0% |
| `flag_negative_draw` | 1 | 4 | 0.0% |
| `flag_dpd_error` | 0 | 103,558 | 100.0% |
| `flag_small_balance_payment` | 0 | 54,430 | 52.6% |
| `flag_small_balance_payment` | 1 | 49,128 | 47.4% |
| `raw_invalid_limit_flag` | 0 | 78,241 | 75.6% |
| `raw_invalid_limit_flag` | 1 | 25,317 | 24.4% |

