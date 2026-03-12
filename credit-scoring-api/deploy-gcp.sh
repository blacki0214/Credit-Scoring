# Quick Deploy Script for Google Cloud Run

## Prerequisites
# 1. Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install
# 2. Login: gcloud auth login
# 3. Set project: gcloud config set project YOUR_PROJECT_ID

## Step 1: Enable APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

## Step 2: Create Secrets
# Generate new keys first:
# python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32)); print('API_KEY=' + secrets.token_urlsafe(32))"

# Create secrets (replace with your actual keys):
echo -n "YOUR_SECRET_KEY_HERE" | gcloud secrets create credit-api-secret-key --data-file=-
echo -n "YOUR_API_KEY_HERE" | gcloud secrets create credit-api-key --data-file=-

# Get your project number:
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")

# Grant Cloud Run access to secrets:
gcloud secrets add-iam-policy-binding credit-api-secret-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding credit-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

## Step 3: Deploy to Cloud Run
cd credit-scoring-api

gcloud run deploy credit-scoring-api \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=INFO,ALLOWED_ORIGINS=https://your-frontend-domain.com" \
  --set-secrets "SECRET_KEY=credit-api-secret-key:latest,API_KEY=credit-api-key:latest" \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --port 8080

## Step 4: Get Service URL
gcloud run services describe credit-scoring-api \
  --region asia-southeast1 \
  --format 'value(status.url)'

## Step 5: Test Deployment
# Replace URL with your actual Cloud Run URL
curl https://credit-scoring-api-xxxxx-as.a.run.app/api/health

# Test with API key:
curl https://credit-scoring-api-xxxxx-as.a.run.app/api/calculate-limit \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "age": 30,
    "monthly_income": 20000000,
    "employment_status": "EMPLOYED",
    "years_employed": 5.0,
    "home_ownership": "MORTGAGE",
    "loan_purpose": "CAR",
    "years_credit_history": 5,
    "has_previous_defaults": false,
    "currently_defaulting": false
  }'

## Useful Commands

# View logs:
gcloud run services logs read credit-scoring-api --region asia-southeast1 --limit 50

# Update service (e.g., change memory):
gcloud run services update credit-scoring-api --memory 4Gi --region asia-southeast1

# Delete service:
gcloud run services delete credit-scoring-api --region asia-southeast1

# List all services:
gcloud run services list

# Get service details:
gcloud run services describe credit-scoring-api --region asia-southeast1
