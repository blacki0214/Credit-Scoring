# GCP Deployment Guide - Complete Setup

This guide covers the complete deployment of both the production API and the automated model retraining pipeline.

## Overview

```
1. Deploy API to Cloud Run
2. Deploy Firestore Exporter (Cloud Function)
3. Deploy Retraining Pipeline (Cloud Run Job)
4. Configure Scheduling
```

## Prerequisites

### 1. Install Google Cloud CLI
- Windows: https://cloud.google.com/sdk/docs/install
- Linux/Mac: `curl https://sdk.cloud.google.com | bash`

### 2. Authenticate and Configure
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud config set compute/region asia-southeast1
```

### 3. Enable Required APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## Part 1: Deploy Production API

### Step 1: Create Secrets
```bash
# Generate keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32)); print('API_KEY=' + secrets.token_urlsafe(32))"

# Store in Secret Manager
echo -n "YOUR_SECRET_KEY_HERE" | gcloud secrets create credit-api-secret-key --data-file=-
echo -n "YOUR_API_KEY_HERE" | gcloud secrets create credit-api-key --data-file=-

# Grant access to Cloud Run
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding credit-api-secret-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding credit-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 2: Create GCS Bucket for Models
```bash
gsutil mb -l asia-southeast1 gs://retrain
```

### Step 3: Upload Current Models to GCS
```bash
cd credit-scoring-api
gsutil cp models/xgboost_final.pkl gs://mlretrain/models/production/
gsutil cp models/lgb_model_optimized.pkl gs://mlretrain/models/production/
gsutil cp models/ensemble_comparison_metadata.pkl gs://mlretrain/models/production/
```

### Step 4: Deploy API to Cloud Run
```bash
cd credit-scoring-api

gcloud run deploy credit-scoring-api \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=INFO,GCS_MODEL_BUCKET=mlretrain,GCS_MODEL_PREFIX=models/production" \
  --set-secrets "SECRET_KEY=credit-api-secret-key:latest,API_KEY=credit-api-key:latest" \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --port 8080
```

### Step 5: Test API
```bash
# Get service URL
API_URL=$(gcloud run services describe credit-scoring-api --region asia-southeast1 --format 'value(status.url)')

# Test health endpoint
curl ${API_URL}/api/health

# Test with API key
curl ${API_URL}/api/model/info -H "X-API-Key: YOUR_API_KEY"
```

## Part 2: Deploy Firestore Exporter

### Step 1: Deploy Cloud Function
```bash
cd cloud-functions/firestore-exporter
gcloud functions deploy export-firestore-to-gcs \
  --gen2 \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --region asia-southeast1 \
  --memory 512MB \
  --timeout 300s \
  --entry-point export_firestore_to_gcs
```

### Step 2: Schedule Weekly Export
```bash
# Get function URL
FUNCTION_URL=$(gcloud functions describe export-firestore-to-gcs --region=asia-southeast1 --gen2 --format='value(serviceConfig.uri)')

# Create scheduler job
gcloud scheduler jobs create http firestore-export-weekly \
  --schedule="0 2 * * 0" \
  --uri="${FUNCTION_URL}" \
  --location=asia-southeast1 \
  --http-method=POST
```

### Step 3: Test Manual Export
```bash
curl -X POST ${FUNCTION_URL}
```

## Part 3: Deploy Retraining Pipeline

### Step 1: Build and Deploy Cloud Run Job
```bash
cd credit-scoring-api/pipeline

# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# OR Windows
.\deploy.ps1
```

### Step 2: Verify Deployment
```bash
gcloud run jobs describe retrain-job --region=asia-southeast1
```

### Step 3: Test Manual Execution
```bash
gcloud run jobs execute retrain-job --region=asia-southeast1
```

### Step 4: Monitor Execution
```bash
# View logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=retrain-job" \
  --limit 50 \
  --format json

# List executions
gcloud run jobs executions list --job=retrain-job --region=asia-southeast1
```

## Part 4: Verify Complete Setup

### 1. Check All Services
```bash
# API
gcloud run services list

# Cloud Function
gcloud functions list --region=asia-southeast1

# Cloud Run Job
gcloud run jobs list --region=asia-southeast1

# Schedulers
gcloud scheduler jobs list --location=asia-southeast1
```

### 2. Check GCS Bucket Structure
```bash
gsutil ls -r gs://retrain/
```

Expected structure:
```
gs://retrain/
  data/
    exports/
  models/
    production/
      xgboost_final.pkl
      lgb_model_optimized.pkl
      ensemble_comparison_metadata.pkl
```

### 3. Test Complete Flow

#### Trigger Data Export
```bash
gcloud scheduler jobs run firestore-export-weekly --location=asia-southeast1
```

#### Wait for Export to Complete (check logs)
```bash
gcloud logging read "resource.type=cloud_run_function" --limit 20
```

#### Trigger Retraining
```bash
gcloud run jobs execute retrain-job --region=asia-southeast1
```

#### Monitor Retraining
```bash
gcloud logging read "resource.type=cloud_run_job" --limit 50
```

## Scheduled Operations

| Job | Schedule | Description |
|-----|----------|-------------|
| `firestore-export-weekly` | Sunday 2:00 AM UTC | Export Firestore to GCS |
| `retrain-weekly` | Sunday 3:00 AM UTC | Retrain model (1 hour after export) |

## Cost Monitoring

### View Billing
```bash
gcloud billing accounts list
```

### Estimated Monthly Costs
- Cloud Run API: $5-20 (depends on traffic)
- Cloud Function: $0.10-0.50
- Cloud Run Job: $0.80-2.00
- Cloud Storage: $0.02-0.20
- Total: ~$6-25/month

## Troubleshooting

### API Not Loading Models from GCS
Check environment variables:
```bash
gcloud run services describe credit-scoring-api --region=asia-southeast1 --format=yaml
```

Should show:
```yaml
env:
- name: GCS_MODEL_BUCKET
  value: retrain
- name: GCS_MODEL_PREFIX
  value: models/production
```

### Cloud Function Permissions Error
Grant Firestore read access:
```bash
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### Retraining Job Fails
Check logs:
```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=retrain-job AND severity>=ERROR" \
  --limit 50
```

Common issues:
- Not enough data: Reduce `MIN_SAMPLES`
- GCS permission denied: Grant `storage.objectAdmin` on bucket
- Out of memory: Increase memory in `deploy.sh`

## Maintenance

### Update API
```bash
cd credit-scoring-api
gcloud run deploy credit-scoring-api --source . --region=asia-southeast1
```

### Update Retraining Pipeline
```bash
cd credit-scoring-api/pipeline
./deploy.sh  # or .\deploy.ps1 on Windows
```

### Pause Scheduled Jobs
```bash
gcloud scheduler jobs pause firestore-export-weekly --location=asia-southeast1
gcloud scheduler jobs pause retrain-weekly --location=asia-southeast1
```

### Resume Scheduled Jobs
```bash
gcloud scheduler jobs resume firestore-export-weekly --location=asia-southeast1
gcloud scheduler jobs resume retrain-weekly --location=asia-southeast1
```

### Manual Model Rollback
```bash
# List archived models
gsutil ls gs://retrain/models/archive/

# Copy old model to production
gsutil cp gs://retrain/models/archive/lgb_model_TIMESTAMP.pkl \
          gs://retrain/models/production/lgb_model_optimized.pkl

# Restart API to pick up new model
gcloud run services update credit-scoring-api --region=asia-southeast1
```

## Security Best Practices

1. Never commit secrets to Git
2. Use Secret Manager for all sensitive data
3. Restrict CORS origins in production
4. Enable VPC connector for private resources
5. Use private Cloud Run endpoints if possible
6. Rotate API keys quarterly

## Next Steps

1. Set up monitoring and alerting (Cloud Monitoring)
2. Configure custom domain and SSL certificate
3. Implement API rate limiting per user
4. Add model performance monitoring dashboard
5. Set up automated backups for Firestore
6. Implement model A/B testing framework

## Support

For issues or questions:
- Check logs: `gcloud logging read`
- Review documentation in each component's README
- Verify IAM permissions and service accounts
