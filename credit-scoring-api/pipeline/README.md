# Model Retraining Pipeline

Automated pipeline for retraining the Credit Scoring LightGBM model using production data from Firestore.

## Architecture

```
Firestore → Cloud Function (export) → GCS (data/exports/) → Cloud Run Job (retrain) → GCS (models/staging/) → Production
```

## Components

### 1. Data Export (Cloud Function)
Located in: `/cloud-functions/firestore-exporter/`
- Exports `loan_applications` collection from Firestore to GCS
- Runs weekly via Cloud Scheduler
- Output: Parquet files in `gs://retrain/data/exports/`

### 2. Retraining Pipeline (Cloud Run Job)
Located in: `/credit-scoring-api/pipeline/`
- Trains new LightGBM model on latest data
- Compares with production model
- Auto-promotes if AUC improvement >= 2%
- Runs weekly via Cloud Scheduler

## Files

| File | Purpose |
|------|---------|
| `retrain_job.py` | Main orchestration script |
| `feature_engineering.py` | Feature engineering (64 features) |
| `config.py` | Pipeline configuration |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container definition |
| `deploy.sh` / `deploy.ps1` | Deployment scripts |

## Prerequisites

1. **GCP Project Setup**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable cloudscheduler.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

3. **Create GCS Bucket**
   ```bash
   gsutil mb -l asia-southeast1 gs://retrain
   ```

4. **Upload Initial Training Data** (optional)
   ```bash
   gsutil cp your_training_data.parquet gs://retrain/data/original/
   ```

## Deployment

### Linux/Mac
```bash
cd credit-scoring-api/pipeline
chmod +x deploy.sh
./deploy.sh
```

### Windows (PowerShell)
```powershell
cd credit-scoring-api\pipeline
.\deploy.ps1
```

## Configuration

Environment variables (set in `deploy.sh` or `deploy.ps1`):

| Variable | Default | Description |
|----------|---------|-------------|
| `GCS_BUCKET` | `retrain` | GCS bucket name |
| `MIN_SAMPLES` | `500` | Minimum samples required for retraining |
| `MIN_AUC_IMPROVEMENT` | `0.02` | Minimum AUC improvement for promotion (2%) |
| `PROMOTION_THRESHOLD` | `0.86` | Classification threshold for evaluation |

## Manual Execution

### Run Retraining Job
```bash
gcloud run jobs execute retrain-job --region=asia-southeast1
```

### View Logs
```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=retrain-job" \
  --limit 50 \
  --format json
```

### List Executions
```bash
gcloud run jobs executions list --job=retrain-job --region=asia-southeast1
```

## Pipeline Flow

### Step 1: Data Loading
- Loads latest parquet file from `gs://retrain/data/exports/`
- Checks if minimum sample size is met
- Validates data quality

### Step 2: Target Variable
- **Preferred**: Uses `actual_default` (ground truth from loan outcomes)
- **Fallback**: Uses `approved` status as proxy (for calibration only)

### Step 3: Feature Engineering
- Validates input data (age, income, employment, etc.)
- Engineers 64 features from 9 input features
- Includes interaction terms and composite scores

### Step 4: Model Training
- Splits data: 70% train, 15% validation, 15% test
- Trains LightGBM with production hyperparameters
- Uses early stopping (50 rounds)

### Step 5: Evaluation
- Calculates AUC-ROC, Precision, Recall, F1
- Compares with current production model
- Generates classification report

### Step 6: Promotion Decision
- Promotes to production if:
  - New AUC >= Production AUC + 0.02 (2% improvement)
  - Model passes validation checks
- Otherwise: saves to staging for manual review

### Step 7: Deployment
- Archives old production model
- Copies new model to `gs://retrain/models/production/`
- Updates metadata

## GCS Bucket Structure

```
gs://retrain/
  data/
    exports/                      # Firestore exports (input)
      loan_applications_*.parquet
      metadata_*.json
    original/                     # Original training data (optional)
      flat_table.parquet
  models/
    production/                   # Active production model
      lgb_model_optimized.pkl
      metadata_latest.json
    staging/                      # Candidate models
      lgb_retrained_*.pkl
      metadata_*.json
    archive/                      # Historical models
      lgb_model_*.pkl
```

## Monitoring

### Check Scheduler Status
```bash
gcloud scheduler jobs describe retrain-weekly --location=asia-southeast1
```

### Pause Scheduled Retraining
```bash
gcloud scheduler jobs pause retrain-weekly --location=asia-southeast1
```

### Resume Scheduled Retraining
```bash
gcloud scheduler jobs resume retrain-weekly --location=asia-southeast1
```

## Troubleshooting

### Issue: Not Enough Data
**Error**: `Not enough data. Need 500, have X.`

**Solution**: Wait for more loan applications or reduce `MIN_SAMPLES`:
```bash
gcloud run jobs update retrain-job \
  --set-env-vars MIN_SAMPLES=100 \
  --region=asia-southeast1
```

### Issue: No Ground Truth Labels
**Warning**: `Ground truth not available. Using proxy: approval status`

**Solution**: This is expected in early stages. Implement loan outcome tracking:
1. Add webhook endpoint to receive loan outcomes
2. Update Firestore records with `actualDefault` field
3. Re-export data using Cloud Function

### Issue: Model Not Promoted
**Info**: `New model did not meet promotion criteria`

**Reason**: AUC improvement < 2%

**Solution**: 
- Review staging model metrics in GCS
- Manually promote if desired:
  ```bash
  gsutil cp gs://retrain/models/staging/lgb_retrained_TIMESTAMP.pkl \
            gs://retrain/models/production/lgb_model_optimized.pkl
  ```

### Issue: Build Timeout
**Error**: Build times out during container build

**Solution**: Increase timeout:
```bash
gcloud builds submit --timeout=20m --tag gcr.io/YOUR_PROJECT/retrain-job .
```

## Development

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GCS_BUCKET=retrain
export MIN_SAMPLES=50

# Run locally
python retrain_job.py
```

### Test Feature Engineering
```python
from feature_engineering import engineer_features, validate_features
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'age': [30],
    'monthly_income': [20000000],
    'employment_status': ['EMPLOYED'],
    'years_employed': [5.0],
    'home_ownership': ['RENT'],
    'loan_purpose': ['CAR'],
    'years_credit_history': [3.0],
    'has_previous_defaults': [False],
    'currently_defaulting': [False],
})

# Validate and engineer
clean_df, invalid_count = validate_features(df)
features = engineer_features(clean_df)
print(f"Generated {len(features.columns)} features")
```

## Cost Estimation

### Cloud Run Job
- CPU: 4 vCPU
- Memory: 8 GB
- Duration: ~10-30 minutes
- Cost per execution: ~$0.20-0.50

### Cloud Scheduler
- 4 executions/month (weekly)
- Cost: ~$0.40/month

### Cloud Storage
- Data + Models: ~1-5 GB
- Cost: ~$0.02-0.10/month

**Total estimated cost**: ~$1-2/month

## Security

### IAM Permissions Required
Cloud Run Job service account needs:
- `storage.objects.get` on `gs://retrain/data/exports/`
- `storage.objects.create` on `gs://retrain/models/`
- `storage.objects.list` on `gs://retrain/`

### Grant Permissions
```bash
gsutil iam ch serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com:roles/storage.objectAdmin \
  gs://retrain
```

## Next Steps

1. Deploy Firestore exporter: See `/cloud-functions/firestore-exporter/README.md`
2. Upload initial training data (if available)
3. Deploy retraining pipeline: Run `./deploy.sh`
4. Verify first execution: `gcloud run jobs execute retrain-job --region=asia-southeast1`
5. Set up monitoring/alerting for pipeline failures
