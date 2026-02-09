# Installments Payments Features - Data Dictionary

**Dataset**: `installments_features_20251027_142834.parquet`  
**Location**: `installments_payments_features/installments_features_20251027_142834.parquet`  
**Generated**: 2026-02-09 09:57:55

## Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Rows** | 339,587 |
| **Total Columns** | 27 |
| **Memory Usage** | 57.00 MB |

## Field Definitions

| Column Name | Description | Data Type | Non-Null Count | Null % | Unique Values | Mean | Min | Max | Std Dev |
|-------------|-------------|-----------|----------------|--------|---------------|------|-----|-----|---------|
| `SK_ID_CURR` | Unique identifier for each customer/loan application | `int32` | 339,587 | 0.0% | 339,587 | 278154.89 | 100001.00 | 456255.00 | 102880.49 |
| `dpd_mean` | Average days past due across all installments | `float64` | 339,578 | 0.0% | 24,272 | 1.23 | 0.00 | 2813.00 | 12.36 |
| `dpd_max` | Maximum days past due observed | `float64` | 339,578 | 0.0% | 1,694 | 17.84 | 0.00 | 2884.00 | 108.28 |
| `on_time_ratio` | Ratio of on-time payments to total payments | `float64` | 339,587 | 0.0% | 4,909 | 0.92 | 0.00 | 1.00 | 0.14 |
| `num_payments` | Total number of installment payments | `int64` | 339,587 | 0.0% | 308 | 37.88 | 1.00 | 336.00 | 39.24 |
| `dpd_gt30_flag` | Flag indicating if any payment was >30 days late | `int32` | 339,587 | 0.0% | 2 | 0.07 | 0.00 | 1.00 | 0.25 |
| `ins_payment_ratio` | Ratio of actual payment to expected installment | `float64` | 339,575 | 0.0% | 167,125 | 1.23 | 0.00 | 10024.53 | 26.75 |
| `ins_payment_variance` | Variance in payment amounts | `float64` | 338,584 | 0.3% | 167,882 | 15367.56 | 0.00 | 1105204096.60 | 3291582.02 |
| `ins_early_ratio` | Ratio of early payments | `float64` | 339,578 | 0.0% | 8,889 | 0.78 | 0.00 | 1.00 | 0.24 |
| `installment_missing_flag` | Flag for missing installment data | `int32` | 339,587 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `flag_negative_amount` | Flag for negative installment amounts | `int32` | 339,587 | 0.0% | 1 | 0.00 | 0.00 | 0.00 | 0.00 |
| `flag_overpayment` | Flag for overpayment observations | `int32` | 339,587 | 0.0% | 2 | 0.08 | 0.00 | 1.00 | 0.28 |
| `flag_missing_amount` | Flag for missing payment amounts | `int32` | 339,587 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.06 |
| `flag_missing_days` | Flag for missing payment days | `int32` | 339,587 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.06 |
| `flag_unrealistic_delay` | Flag for unrealistic payment delays | `int32` | 339,587 | 0.0% | 2 | 0.01 | 0.00 | 1.00 | 0.10 |
| `raw_total_instalment` | Total expected installment amount | `float64` | 339,587 | 0.0% | 336,690 | 636129.44 | 0.00 | 32310192.92 | 833986.47 |
| `raw_total_payment` | Total actual payment amount | `float64` | 339,578 | 0.0% | 337,072 | 646837.21 | 0.18 | 32362711.61 | 852680.25 |
| `raw_payments_count` | Count of payment records | `float64` | 339,587 | 0.0% | 309 | 37.87 | 0.00 | 336.00 | 39.23 |
| `raw_instalments_count` | Count of installment records | `float64` | 339,587 | 0.0% | 308 | 37.88 | 1.00 | 336.00 | 39.24 |
| `raw_on_time_count` | Count of on-time payments | `float64` | 339,587 | 0.0% | 300 | 34.62 | 0.00 | 336.00 | 36.84 |
| `raw_late_count` | Count of late payments | `float64` | 339,587 | 0.0% | 98 | 3.25 | 0.00 | 142.00 | 6.07 |
| `raw_max_dpd` | Maximum days past due (raw) | `float64` | 339,578 | 0.0% | 1,694 | 17.84 | 0.00 | 2884.00 | 108.28 |
| `raw_payment_ratio_obs` | Observed payment ratio | `float64` | 339,587 | 0.0% | 309 | 37.87 | 0.00 | 336.00 | 39.23 |
| `raw_missing_amount_rows` | Number of rows with missing amounts | `float64` | 339,587 | 0.0% | 27 | 0.01 | 0.00 | 57.00 | 0.26 |
| `raw_missing_days_rows` | Number of rows with missing days | `float64` | 339,587 | 0.0% | 27 | 0.01 | 0.00 | 57.00 | 0.26 |
| `raw_missing_amount_flag` | Flag for missing amount presence | `int32` | 339,587 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.06 |
| `raw_missing_days_flag` | Flag for missing days presence | `int32` | 339,587 | 0.0% | 2 | 0.00 | 0.00 | 1.00 | 0.06 |

## Value Distributions

### Key Flags

| Flag | Value | Count | Percentage |
|------|-------|-------|------------|
| `dpd_gt30_flag` | 0 | 315,880 | 93.0% |
| `dpd_gt30_flag` | 1 | 23,707 | 7.0% |
| `installment_missing_flag` | 0 | 339,587 | 100.0% |
| `flag_negative_amount` | 0 | 339,587 | 100.0% |
| `flag_overpayment` | 0 | 311,409 | 91.7% |
| `flag_overpayment` | 1 | 28,178 | 8.3% |
| `flag_missing_amount` | 0 | 338,339 | 99.6% |
| `flag_missing_amount` | 1 | 1,248 | 0.4% |
| `flag_missing_days` | 0 | 338,339 | 99.6% |
| `flag_missing_days` | 1 | 1,248 | 0.4% |
| `flag_unrealistic_delay` | 0 | 336,313 | 99.0% |
| `flag_unrealistic_delay` | 1 | 3,274 | 1.0% |
| `raw_missing_amount_flag` | 0 | 338,339 | 99.6% |
| `raw_missing_amount_flag` | 1 | 1,248 | 0.4% |
| `raw_missing_days_flag` | 0 | 338,339 | 99.6% |
| `raw_missing_days_flag` | 1 | 1,248 | 0.4% |

