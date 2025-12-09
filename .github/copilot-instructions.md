# Credit Scoring System - AI Agent Instructions

## Project Overview

This is a production-ready **loan approval system** with Vietnamese Dong (VND) support. The system consists of:
- **FastAPI REST API** (`credit-scoring-api/`) - Customer-facing loan application service
- **ML Research** (`notebooks/`) - Model development using LightGBM, XGBoost, Random Forest
- **Feature Engineering** (`fico_derive/`) - FICO-style credit score calculation
- **Training Data** (`data/`) - Home Credit dataset with multiple CSV tables

**Key Architecture**: The API uses a pre-trained LightGBM model with 64 features derived from the Home Credit dataset, but accepts simple customer inputs (11 fields) and maps them intelligently to model features.

## Critical Workflows

### Running the API (Production)
```bash
# Windows
cd credit-scoring-api
start.bat

# Linux/Mac
cd credit-scoring-api
chmod +x start.sh
./start.sh
```

The API runs in Docker on port 8000. Model files MUST exist in `credit-scoring-api/models/`:
- `lgb_model_optimized.pkl` - Primary LightGBM model
- `ensemble_comparison_metadata.pkl` - Model metadata

### Testing the API
```bash
cd credit-scoring-api
python test_api.py
```

Access interactive docs at `http://localhost:8000/docs`

### Model Development (Notebooks)
Work in `notebooks/parquet_files/`. Key notebooks:
- `04b_baseline_model_LightGBM_improved.ipynb` - Current production model
- `04c_ensemble_comparison_RF_XGB.ipynb` - Model comparison (RF/XGB/LGBM)
- `04d_XGBoost.ipynb` - XGBoost deep dive with threshold optimization

**Data Loading Pattern**: All notebooks load from `data/data-processing/flat_table/*.parquet` using absolute Windows paths (e.g., `C:\Users\...\flat_credit_model_*.parquet`)

## Project-Specific Conventions

### API Service Architecture

**Singleton Pattern**: Services are instantiated once and imported as singletons:
```python
from app.services.model_loader import model_loader  # Not ModelLoader()
from app.services.prediction_service import prediction_service
from app.services.loan_offer_service import loan_offer_service
```

**Feature Mapping Strategy**: The `FeatureEngineer` class (`app/services/feature_engineering.py`) maps 11 simple customer inputs to 64 model features by:
1. Creating a DataFrame with all 64 features filled with zeros
2. Mapping available customer data to corresponding features
3. Using intelligent defaults for missing features (e.g., `thin_file_flag=1` for new customers)

Example mapping:
```python
mapping['age_years'] = age
mapping['annuity_income_ratio'] = loan_pct_income
mapping['credit_income_ratio'] = loan_amount / income
```

### Currency Handling

**USD to VND Conversion**: All API responses use VND. Fixed rate defined in `loan_offer_service.py`:
```python
USD_TO_VND = 25000
```

Customer inputs are in VND (e.g., `monthly_income: 15000000` = 15 million VND), but internal model calculations may use USD-scaled values.

### Credit Score Calculation

Credit scores (300-850) are calculated **at request time** in `request_converter.py` using a rule-based system:
- Base score: 650
- Age bonus: up to +50 points
- Income bonus: up to +50 points
- Employment length: up to +40 points
- Home ownership: up to +30 points (OWN > MORTGAGE > RENT)
- Credit history: up to +40 points
- **Penalties**: Previous defaults -80 to -150 points

This differs from typical ML pipelines where scores come from models. Here the score is an INPUT to risk assessment, not an output.

### Risk Levels & Business Rules

Risk levels in `LoanOfferService` drive approval decisions:
```python
approval_threshold = 0.30  # Approve if default probability < 30%

interest_rates = {
    "Low": 8.5%,      # < 15% default probability
    "Medium": 12.0%,  # 15-30%
    "High": 16.0%,    # 30-50%
    "Very High": 20.0%  # > 50%
}

loan_amount_factors = {
    "Low": 1.0,       # Full amount
    "Medium": 0.75,   # 75% of requested
    "High": 0.5,      # 50% of requested
    "Very High": 0.0  # Rejected
}
```

Max loan = 5x annual income × risk factor.

## Data Processing Patterns

### Notebook Data Flow

1. **Data Loading**: Always from Parquet files in `data/data-processing/flat_table/`
2. **Feature Engineering**: Use `fico_derive/feature_engineering.py` patterns (repayment history, amounts owed, credit age)
3. **Train/Test Split**: Always stratified with `random_state=42`, typically 80/20 split
4. **Class Imbalance**: Calculate `imbalance_ratio = class_0_count / class_1_count` and use as `scale_pos_weight` in tree models
5. **Model Saving**: Save to `output/models/` with joblib, include comprehensive metadata dictionary

### Feature Engineering Rules (FICO-style)

From `fico_derive/feature_engineering.py`:
```python
# Days Past Due calculation
install["dpd"] = (install["DAYS_ENTRY_PAYMENT"] - install["DAYS_INSTALMENT"]).clip(lower=0)

# Utilization ratio (capped at 1.5 to handle outliers)
owed_feat["total_utilization"] = (debt / credit_sum).clip(upper=1.5)

# Credit age in months
bureau["CREDIT_AGE_MONTHS"] = abs(bureau["DAYS_CREDIT"]) / 30.44
```

**Critical**: Replace infinite values (`np.inf`) with `np.nan`, then fill all NaN with 0.

## Configuration & Environment

### API Configuration
Settings in `app/core/config.py` use Pydantic Settings with `.env` file support. Key settings:
- `MODEL_DIR`: Relative path that works in Docker (`self.BASE_DIR / "models"`)
- `ALLOWED_ORIGINS`: CORS configuration - includes `"*"` for development
- `API_PREFIX`: Always `/api`

### Docker Configuration
`docker-compose.yml` mounts models as read-only:
```yaml
volumes:
  - ./models:/app/models:ro  # Read-only prevents accidental modification
```

Healthcheck uses `/api/health` endpoint (not root `/health`).

## Testing Conventions

Tests in `credit-scoring-api/tests/` use pytest with async support:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
```

**Type Checker Workaround**: Tests intentionally validate missing fields with `# type: ignore` comments - this is correct behavior for validation testing.

## Model Comparison Workflow

When comparing models (see `04c_ensemble_comparison_RF_XGB.ipynb`):

1. Train all models with same `random_state=42`
2. Use `scale_pos_weight=imbalance_ratio` for tree models
3. Calculate both default threshold (0.5) AND optimized threshold using F1/cost analysis
4. Save comprehensive metadata including:
   - Training date
   - Model params
   - Performance metrics at multiple thresholds
   - Feature importance (top 20)
   - Confusion matrix breakdown
   - Business cost calculations

## Common Pitfalls

1. **Model File Paths**: API expects models in `credit-scoring-api/models/`, NOT `output/models/`. Copy files after training.

2. **Feature Count Mismatch**: The model expects 64 features. Don't try to retrain with different feature sets without updating `FeatureEngineer._create_feature_mapping()`.

3. **Windows Path Handling**: Notebooks use raw strings for Windows paths: `r'C:\Users\...'`. Update paths for your environment.

4. **Circular Imports**: Never import `model_loader` in a file that `model_loader` imports. Use the singleton pattern consistently.

5. **Docker Model Loading**: Models must exist BEFORE `docker-compose up`. The startup script (`start.bat`) checks for this.

6. **Currency Confusion**: Customer-facing amounts are VND (millions). Internal calculations may scale to USD equivalent. Always check `USD_TO_VND` conversion.

## Key Files to Reference

- **API Entry**: `credit-scoring-api/app/main.py` - FastAPI app setup
- **Feature Mapping Logic**: `credit-scoring-api/app/services/feature_engineering.py`
- **Business Rules**: `credit-scoring-api/app/services/loan_offer_service.py`
- **Schema Definitions**: `credit-scoring-api/app/models/schemas.py`
- **Production Model**: Notebook `04b_baseline_model_LightGBM_improved.ipynb`
- **FICO Features**: `fico_derive/feature_engineering.py`

## Documentation

- **API Guide**: `credit-scoring-api/README.md` - Technical API docs
- **Customer Guide**: `credit-scoring-api/CUSTOMER_API_GUIDE.md` - Customer-friendly endpoint
- **Deployment**: `credit-scoring-api/DEPLOYMENT_READY.md` - Production readiness checklist
- **Docker**: `credit-scoring-api/DOCKER_GUIDE.md` - Docker-specific instructions

## Quick Reference Commands

```bash
# Start API
cd credit-scoring-api && start.bat

# Run tests
cd credit-scoring-api && pytest tests/

# Test API endpoints
cd credit-scoring-api && python test_api.py

# View API docs
http://localhost:8000/docs

# Stop API
cd credit-scoring-api && docker-compose down

# View logs
cd credit-scoring-api && docker-compose logs -f
```
