# Model Retraining Pipeline

**Status:** ✅ **FULLY DEPLOYED & AUTOMATED**

Automated weekly pipeline for retraining the Credit Scoring LightGBM model using production data from Firebase Firestore.

## 🎯 Current Deployment

| Component | Status | Schedule | Region |
|-----------|--------|----------|--------|
| **Firestore Database** | ✅ ACTIVE | Real-time | Firebase |
| **Cloud Function** (`export-firestore-to-gcs`) | ✅ DEPLOYED | Every Sunday 2:00 AM | asia-southeast1 |
| **Cloud Scheduler** (`firestore-export-weekly`) | ✅ ENABLED | `0 2 * * 0` (Weekly) | asia-southeast1 |
| **Cloud Run Job** (`retrain-job`) | ✅ DEPLOYED | Every Sunday 3:00 AM | asia-southeast1 |
| **Cloud Scheduler** (`retrain-weekly`) | ✅ ENABLED | `0 3 * * 0` (Weekly) | asia-southeast1 |
| **Email Notifications** | ✅ CONFIGURED | After each retrain | Gmail SMTP |

**GCS Bucket:** `credit-scoring-retrain-976448868286`  
**Project:** `project-71e73ad8-4a84-471e-b69`  
**Notification Email:** `vanquoc11082004@gmail.com`

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Flutter   │────▶│    Firestore     │────▶│Cloud Function│
│     App     │     │  loan_applications│     │   (Export)  │
└─────────────┘     └──────────────────┘     └──────┬──────┘
                                                      │
                    ┌─────────────────────────────────┘
                    │
                    ▼
              ┌──────────┐     ┌──────────────┐     ┌──────────┐
              │   GCS    │────▶│  Cloud Run   │────▶│   GCS    │
              │ (exports)│     │ (Retrain Job)│     │ (models) │
              └──────────┘     └──────┬───────┘     └──────────┘
                                      │
                                      ▼
                               ┌─────────────┐
                               │    Gmail    │
                               │Notification │
                               └─────────────┘
```

**Data Flow:**
1. **App → Firestore:** Flutter app saves loan applications with `status: 'scored'`
2. **Firestore → GCS:** Cloud Function exports data weekly (Sunday 2 AM)
3. **GCS → Training:** Cloud Run Job loads data and trains model (Sunday 3 AM)
4. **Training → GCS:** New model saved to staging/production based on performance
5. **Training → Email:** Results sent via Gmail to `vanquoc11082004@gmail.com`

---

## 📁 Components

### 1. Data Export (Cloud Function)
**Location:** `/cloud-functions/firestore-exporter/`  
**Function Name:** `export-firestore-to-gcs`  
**Trigger:** HTTP (called by Cloud Scheduler)  
**Schedule:** Every Sunday at 2:00 AM (UTC+7)

**What it does:**
- Queries Firestore collection `loan_applications` where `status == 'scored'`
- Converts to Parquet format
- Uploads to `gs://credit-scoring-retrain-976448868286/data/exports/`
- Saves export metadata

**Output Files:**
- Data: `loan_applications_YYYYMMDD_HHMMSS.parquet`
- Metadata: `metadata_YYYYMMDD_HHMMSS.json`

### 2. Retraining Pipeline (Cloud Run Job)
**Location:** `/credit-scoring-api/pipeline/`  
**Job Name:** `retrain-job`  
**Trigger:** Cloud Scheduler  
**Schedule:** Every Sunday at 3:00 AM (UTC+7)

**What it does:**
1. Loads latest export from GCS
2. Validates data quality (min 500 samples)
3. Engineers 55 features
4. Trains LightGBM model
5. Compares with production model
6. Auto-promotes if AUC improves by ≥2%
7. Sends email report via Gmail

### 3. Email Notification System
**Method:** Gmail SMTP  
**Recipient:** `vanquoc11082004@gmail.com`  
**Credentials:** Stored in GCP Secret Manager

**Email Contents:**
- ✅/⚠️ Model promotion status
- 📈 New model performance metrics (AUC, Precision, Recall, F1)
- 📊 Comparison with production model
- ℹ️ Training timestamp and GCS locations
- 🔗 Link to view models in GCS Console

---

## 📄 Files

| File | Purpose |
|------|---------|
| `retrain_job.py` | Main orchestration script - coordinates entire training pipeline |
| `feature_engineering.py` | Feature engineering logic (55 features from 9 inputs) |
| `email_notifier.py` | Gmail SMTP notification service |
| `config.py` | Pipeline configuration settings |
| `requirements.txt` | Python dependencies (no SendGrid) |
| `Dockerfile` | Container definition for Cloud Run |
| `deploy.sh` / `deploy.ps1` | Deployment scripts for Cloud Build |
| `setup-email-notifications.ps1` | Gmail credential setup script |

---

## ⚙️ Configuration

**Current Environment Variables:**

| Variable | Value | Description |
|----------|-------|-------------|
| `GCS_BUCKET` | `credit-scoring-retrain-976448868286` | GCS bucket name for data & models |
| `MIN_SAMPLES` | `500` | Minimum samples required for retraining |
| `MIN_AUC_IMPROVEMENT` | `0.02` | Minimum AUC improvement for auto-promotion (2%) |
| `PROMOTION_THRESHOLD` | `0.86` | Classification probability threshold for metrics |
| `NOTIFICATION_EMAIL` | `vanquoc11082004@gmail.com` | Email recipient for training reports |

**Secrets (GCP Secret Manager):**
- `gmail-user`: Gmail account for sending emails
- `gmail-app-password`: Gmail App Password (not regular password)

---

## 🚀 Quick Start Guide

### Prerequisites

✅ **Already Completed:**
1. GCP Project configured (`project-71e73ad8-4a84-471e-b69`)
2. Required APIs enabled (Cloud Build, Cloud Run, Cloud Scheduler, Storage, Firestore)
3. GCS Bucket created (`credit-scoring-retrain-976448868286`)
4. Cloud Function deployed (`export-firestore-to-gcs`)
5. Cloud Run Job deployed (`retrain-job`)
6. Cloud Schedulers configured (export & retrain)
7. Gmail notifications configured

### Manual Execution

**Trigger Data Export:**
```bash
gcloud scheduler jobs run firestore-export-weekly --location=asia-southeast1
```

**Trigger Retraining:**
```bash
gcloud run jobs execute retrain-job --region=asia-southeast1 --wait
```

**View Recent Logs:**
```bash
# Retraining job logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=retrain-job" \
  --limit 50 --format="table(timestamp,textPayload)"

# Export function logs
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=export-firestore-to-gcs" \
  --limit 50 --format="table(timestamp,textPayload)"
```

**List Execution History:**
```bash
gcloud run jobs executions list --job=retrain-job --region=asia-southeast1
```

**Check Exported Data:**
```bash
gsutil ls gs://credit-scoring-retrain-976448868286/data/exports/
```

**View Models:**
```bash
# Staging models (not promoted)
gsutil ls gs://credit-scoring-retrain-976448868286/models/staging/

# Production models (auto-promoted)
gsutil ls gs://credit-scoring-retrain-976448868286/models/production/
```

---

## 🔄 Update/Redeploy

### Update Email Notifications
```powershell
cd credit-scoring-api\pipeline
.\setup-email-notifications.ps1 `
  -NotificationEmail "your-email@gmail.com" `
  -GmailUser "your-gmail@gmail.com" `
  -GmailAppPassword "your-16-char-app-password"
```

### Rebuild & Redeploy Container
```bash
cd credit-scoring-api/pipeline

# Build and push new image
PROJECT_ID=$(gcloud config get-value project)
gcloud builds submit --tag asia-southeast1-docker.pkg.dev/$PROJECT_ID/retrain-job/retrain-job .

# Image will be automatically used in next scheduled run
```

### Update Environment Variables
```bash
gcloud run jobs update retrain-job \
  --region=asia-southeast1 \
  --set-env-vars="GCS_BUCKET=credit-scoring-retrain-976448868286,MIN_SAMPLES=500,MIN_AUC_IMPROVEMENT=0.02,PROMOTION_THRESHOLD=0.86,NOTIFICATION_EMAIL=vanquoc11082004@gmail.com"
```

---

## 📊 Pipeline Flow Details

### Step 1: Data Loading
- Loads latest parquet file from `gs://credit-scoring-retrain-976448868286/data/exports/`
- Checks if minimum sample size is met (default: 500 samples)
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
- **If promoted:** Archives old production model, copies new model to production
- **If not promoted:** Model stays in staging for manual review
- Sends email notification with results

---

## 📂 GCS Bucket Structure

```
gs://credit-scoring-retrain-976448868286/
  data/
    exports/                                    # Firestore exports (input)
      loan_applications_20260312_125758.parquet
      metadata_20260312_125758.json
  models/
    staging/                                    # Models not meeting promotion criteria
      lgb_retrained_20260312_084813.pkl
      metadata_20260312_084813.json
    production/                                 # Auto-promoted models
      lgb_model_YYYYMMDD_HHMMSS.pkl
      metadata_YYYYMMDD_HHMMSS.json
    archive/                                    # Archived production models
      lgb_model_20260305_030245.pkl
```

---

## 📧 Email Notification Format

**Subject:** `✅ Model Promoted` or `⚠️ Model Not Promoted - Credit Scoring Retraining`

**Content Includes:**
- **Status Banner:** Green (promoted) or Orange (not promoted)
- **New Model Performance Table:**
  - AUC-ROC
  - Precision
  - Recall
  - F1-Score
  - Test Samples
  - Positive Rate
  - Decision Threshold
- **Model Comparison Table:** (if production model exists)
  - Side-by-side metrics comparison
  - Change percentages (color-coded: green for improvement, red for decline)
- **Training Information:**
  - Timestamp
  - GCS bucket location
  - Model storage path (staging or production)
- **Action Link:** Direct link to GCS Console to view models

---

## 🔍 Monitoring & Troubleshooting

### Check System Status
```bash
# Check Cloud Function status
gcloud functions describe export-firestore-to-gcs --gen2 --region=asia-southeast1

# Check Cloud Run Job status
gcloud run jobs describe retrain-job --region=asia-southeast1

# Check Cloud Schedulers
gcloud scheduler jobs list --location=asia-southeast1
```

### Common Issues

**Issue: No data exported**
- ✅ Check if Firestore has records with `status: 'scored'`
- ✅ Check Cloud Function logs
- ✅ Verify Firestore API is enabled

**Issue: Retraining fails with "Insufficient samples"**
- ✅ Check if export has at least 500 records
- ✅ Adjust `MIN_SAMPLES` if needed for testing

**Issue: Model not promoted**
- ✅ Check logs for AUC comparison
- ✅ New model must improve by ≥2% (0.02 AUC points)
- ✅ Model is saved to staging for manual review

**Issue: No email received**
- ✅ Check spam/junk folder
- ✅ Verify Gmail App Password is correct (no spaces)
- ✅ Check Secret Manager secrets: `gmail-user`, `gmail-app-password`
- ✅ Check Cloud Run Job logs for email errors

### View Full Execution Details
```bash
# Get latest execution name
EXECUTION=$(gcloud run jobs executions list --job=retrain-job --region=asia-southeast1 --limit=1 --format="value(name)")

# View execution details
gcloud run jobs executions describe $EXECUTION --region=asia-southeast1

# View execution logs
gcloud logging read "resource.labels.\"run.googleapis.com/execution_name\"=$EXECUTION" --limit=200
```

---

## 🔐 Security

**Secrets Management:**
- Gmail credentials stored in GCP Secret Manager (encrypted at rest)
- Service account with minimal required permissions
- No secrets in code or environment variables (only references)

**IAM Roles Required:**
- Cloud Run Job: `roles/secretmanager.secretAccessor` (to read secrets)
- Cloud Function: `roles/datastore.user` (to query Firestore)
- Both: `roles/storage.objectAdmin` (to read/write GCS)

---

## 📅 Schedule Summary

| Time (UTC+7) | Action | Component |
|--------------|--------|-----------|
| **Sunday 2:00 AM** | Export Firestore data to GCS | Cloud Function |
| **Sunday 3:00 AM** | Train & evaluate new model | Cloud Run Job |
| **Sunday 3:05 AM** | Send email notification | Cloud Run Job |

**Next Run:** Every Sunday at 2:00 AM (Asia/Ho_Chi_Minh timezone)

---

## 📝 Notes

- **Ground Truth Labels:** The pipeline uses `actual_default` field if available. If not available (for recent applications), it uses `approved` status as a proxy for model calibration.
- **Feature Engineering:** Creates 55 engineered features from 9 input features (age, income, employment, home ownership, credit history, defaults).
- **Model Architecture:** LightGBM with early stopping, balanced class weights, and production-tuned hyperparameters.
- **Auto-Promotion:** Only promotes if new model demonstrates clear improvement (≥2% AUC gain) to avoid unnecessary model churn.
- **Email Method:** Uses Gmail SMTP only (SendGrid support removed for simplicity).

---

## 🆘 Support

**For Issues:**
1. Check logs using commands above
2. Verify all components are ACTIVE/ENABLED
3. Test email notification manually: `gcloud run jobs execute retrain-job --region=asia-southeast1`
4. Check GCS bucket for exports and models

**Configuration Files:**
- Pipeline: `/credit-scoring-api/pipeline/`
- Cloud Function: `/cloud-functions/firestore-exporter/`
- Documentation: This README

---

**Last Updated:** March 12, 2026  
**Status:** ✅ Production-ready and fully automated
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
  gsutil cp gs://credit-scoring-retrain-976448868286/models/staging/lgb_retrained_TIMESTAMP.pkl \
            gs://credit-scoring-retrain-976448868286/models/production/lgb_model_optimized.pkl
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
export GCS_BUCKET=credit-scoring-retrain-976448868286
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
- `storage.objects.get` on `gs://credit-scoring-retrain-976448868286/data/exports/`
- `storage.objects.create` on `gs://credit-scoring-retrain-976448868286/models/`
- `storage.objects.list` on `gs://credit-scoring-retrain-976448868286/`

**Service Account:** `976448868286-compute@developer.gserviceaccount.com`

**Permissions already configured** ✅

## Next Steps

1. Deploy Firestore exporter: See `/cloud-functions/firestore-exporter/README.md`
2. Upload initial training data (if available)
3. Deploy retraining pipeline: Run `./deploy.sh`
4. Verify first execution: `gcloud run jobs execute retrain-job --region=asia-southeast1`
5. Set up monitoring/alerting for pipeline failures
