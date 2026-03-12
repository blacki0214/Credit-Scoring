# Deploy Model Retraining Pipeline to GCP Cloud Run Jobs
# PowerShell version for Windows

$ErrorActionPreference = "Stop"

$PROJECT_ID = gcloud config get-value project
$REGION = "asia-southeast1"
$REPOSITORY = "retrain-job"
$IMAGE_NAME = "retrain-job"
$IMAGE_URI = "asia-southeast1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}"
$SERVICE_ACCOUNT = "${PROJECT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Deploying Model Retraining Pipeline" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host ""

# Step 1: Build and push container image
Write-Host "[1/3] Building container image..." -ForegroundColor Yellow
gcloud builds submit `
  --tag "${IMAGE_URI}" `
  --project="${PROJECT_ID}" `
  .

Write-Host ""
Write-Host "[2/3] Creating Cloud Run Job..." -ForegroundColor Yellow

# Step 2: Create or update Cloud Run Job
try {
    gcloud run jobs create retrain-job `
      --image "${IMAGE_URI}" `
      --region "${REGION}" `
      --set-env-vars "GCS_BUCKET=credit-scoring-retrain-976448868286,MIN_SAMPLES=500,MIN_AUC_IMPROVEMENT=0.02,PROMOTION_THRESHOLD=0.86" `
      --memory 8Gi `
      --cpu 4 `
      --task-timeout 7200 `
      --max-retries 1 `
      --project="${PROJECT_ID}" `
      2>$null
} catch {
    gcloud run jobs update retrain-job `
      --image "${IMAGE_URI}" `
      --region "${REGION}" `
      --set-env-vars "GCS_BUCKET=credit-scoring-retrain-976448868286,MIN_SAMPLES=500,MIN_AUC_IMPROVEMENT=0.02,PROMOTION_THRESHOLD=0.86" `
      --memory 8Gi `
      --cpu 4 `
      --task-timeout 7200 `
      --max-retries 1 `
      --project="${PROJECT_ID}"
}

Write-Host ""
Write-Host "[3/3] Setting up Cloud Scheduler..." -ForegroundColor Yellow

# Step 3: Create Cloud Scheduler job for weekly retraining
try {
    gcloud scheduler jobs create http retrain-weekly `
      --schedule="0 3 * * 0" `
      --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/retrain-job:run" `
      --location="${REGION}" `
      --oauth-service-account-email="${SERVICE_ACCOUNT}" `
      --project="${PROJECT_ID}" `
      2>$null
} catch {
    gcloud scheduler jobs update http retrain-weekly `
      --schedule="0 3 * * 0" `
      --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/retrain-job:run" `
      --location="${REGION}" `
      --oauth-service-account-email="${SERVICE_ACCOUNT}" `
      --project="${PROJECT_ID}"
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Cloud Run Job: retrain-job"
Write-Host "Schedule: Every Sunday at 3:00 AM (UTC)"
Write-Host ""
Write-Host "To run manually:"
Write-Host "  gcloud run jobs execute retrain-job --region=${REGION}"
Write-Host ""
Write-Host "To view logs:"
Write-Host '  gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=retrain-job" --limit 50 --format json'
Write-Host ""
