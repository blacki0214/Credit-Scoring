#!/bin/bash
# Deploy Model Retraining Pipeline to GCP Cloud Run Jobs

set -e

PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
RETRAIN_BUCKET="credit-scoring-retrain-${PROJECT_NUMBER}"
REGION="asia-southeast1"
REPOSITORY="retrain-job"
IMAGE_NAME="retrain-job"
IMAGE_URI="asia-southeast1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}"
SERVICE_ACCOUNT="${PROJECT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "==============================================="
echo "Deploying Model Retraining Pipeline"
echo "==============================================="
echo "Project: $PROJECT_ID"
echo "Retrain bucket: $RETRAIN_BUCKET"
echo "Region: $REGION"
echo ""

# Step 1: Build and push container image
echo "[1/3] Building container image..."
gcloud builds submit \
  --tag "${IMAGE_URI}" \
  --project="${PROJECT_ID}" \
  .

echo ""
echo "[2/3] Creating Cloud Run Job..."

# Step 2: Create or update Cloud Run Job
gcloud run jobs create retrain-job \
  --image "${IMAGE_URI}" \
  --region "${REGION}" \
  --set-env-vars "GCS_BUCKET=${RETRAIN_BUCKET},MIN_SAMPLES=500,MIN_AUC_IMPROVEMENT=0.02,PROMOTION_THRESHOLD=0.86" \
  --memory 8Gi \
  --cpu 4 \
  --task-timeout 7200 \
  --max-retries 1 \
  --project="${PROJECT_ID}" \
  2>/dev/null || \
gcloud run jobs update retrain-job \
  --image "${IMAGE_URI}" \
  --region "${REGION}" \
  --set-env-vars "GCS_BUCKET=${RETRAIN_BUCKET},MIN_SAMPLES=500,MIN_AUC_IMPROVEMENT=0.02,PROMOTION_THRESHOLD=0.86" \
  --memory 8Gi \
  --cpu 4 \
  --task-timeout 7200 \
  --max-retries 1 \
  --project="${PROJECT_ID}"

echo ""
echo "[3/3] Setting up Cloud Scheduler..."

# Step 3: Create Cloud Scheduler job for weekly retraining
gcloud scheduler jobs create http retrain-weekly \
  --schedule="0 3 * * 0" \
  --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/retrain-job:run" \
  --location="${REGION}" \
  --oauth-service-account-email="${SERVICE_ACCOUNT}" \
  --project="${PROJECT_ID}" \
  2>/dev/null || \
gcloud scheduler jobs update http retrain-weekly \
  --schedule="0 3 * * 0" \
  --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/retrain-job:run" \
  --location="${REGION}" \
  --oauth-service-account-email="${SERVICE_ACCOUNT}" \
  --project="${PROJECT_ID}"

echo ""
echo "==============================================="
echo "Deployment Complete!"
echo "==============================================="
echo ""
echo "Cloud Run Job: retrain-job"
echo "Schedule: Every Sunday at 3:00 AM (UTC)"
echo ""
echo "To run manually:"
echo "  gcloud run jobs execute retrain-job --region=${REGION}"
echo ""
echo "To view logs:"
echo "  gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=retrain-job\" --limit 50 --format json"
echo ""
