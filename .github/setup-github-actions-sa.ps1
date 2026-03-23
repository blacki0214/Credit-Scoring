# Setup Service Account for GitHub Actions CI/CD
# Run this once to create and configure the service account

$ErrorActionPreference = "Stop"

$PROJECT_ID = "project-71e73ad8-4a84-471e-b69"
$SA_NAME = "github-actions"
$SA_EMAIL = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "GitHub Actions Service Account Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if already logged in
Write-Host "[1/6] Checking authentication..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# Create service account
Write-Host "[2/6] Creating service account..." -ForegroundColor Yellow
$saExists = gcloud iam service-accounts describe $SA_EMAIL 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Service account already exists" -ForegroundColor Green
} else {
    gcloud iam service-accounts create $SA_NAME `
        --display-name="GitHub Actions CI/CD" `
        --description="Service account for GitHub Actions workflow"
    Write-Host "  ✓ Service account created" -ForegroundColor Green
}

# Grant required roles
Write-Host "[3/6] Granting IAM roles..." -ForegroundColor Yellow

Write-Host "  - Cloud Run Admin..."
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/run.admin" `
    --quiet

Write-Host "  - Artifact Registry Writer..."
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/artifactregistry.writer" `
    --quiet

Write-Host "  - Service Account User..."
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/iam.serviceAccountUser" `
    --quiet

Write-Host "  - Cloud Build Editor..."
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/cloudbuild.builds.editor" `
    --quiet

Write-Host "  - Service Enablement..."
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/serviceusage.serviceUsageConsumer" `
    --quiet

Write-Host "  ✓ All roles granted" -ForegroundColor Green

# Create key
Write-Host "[4/6] Creating service account key..." -ForegroundColor Yellow
$KEY_FILE = "github-actions-key.json"
if (Test-Path $KEY_FILE) {
    Write-Host "  ⚠ Key file already exists: $KEY_FILE" -ForegroundColor Yellow
    $overwrite = Read-Host "  Overwrite? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "  Skipping key creation" -ForegroundColor Yellow
        $KEY_FILE = $null
    } else {
        Remove-Item $KEY_FILE
    }
}

if ($KEY_FILE) {
    gcloud iam service-accounts keys create $KEY_FILE `
        --iam-account=$SA_EMAIL
    Write-Host "  ✓ Key created: $KEY_FILE" -ForegroundColor Green
}

# Enable required APIs
Write-Host "[5/6] Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable artifactregistry.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
Write-Host "  ✓ APIs enabled" -ForegroundColor Green

# Display instructions
Write-Host "[6/6] GitHub Setup Instructions" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Copy the service account key content:"
if ($KEY_FILE -and (Test-Path $KEY_FILE)) {
    Write-Host "   Get-Content $KEY_FILE | Set-Clipboard" -ForegroundColor Cyan
    Write-Host ""
}
Write-Host "2. Add to GitHub Secrets:"
Write-Host "   • Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions" -ForegroundColor White
Write-Host "   • Click: 'New repository secret'" -ForegroundColor White
Write-Host "   • Name: GCP_SA_KEY" -ForegroundColor White
Write-Host "   • Value: Paste the entire JSON content from $KEY_FILE" -ForegroundColor White
Write-Host ""
Write-Host "3. Push code to trigger workflow:"
Write-Host "   git add .github/workflows/deploy-gcp.yml" -ForegroundColor Cyan
Write-Host "   git commit -m 'fix: Update CI/CD workflow for Artifact Registry'" -ForegroundColor Cyan
Write-Host "   git push origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠ IMPORTANT: Keep $KEY_FILE secure and delete after adding to GitHub!" -ForegroundColor Yellow
Write-Host "   Remove-Item $KEY_FILE" -ForegroundColor Cyan
