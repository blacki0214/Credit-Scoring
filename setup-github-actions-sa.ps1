# Setup Service Account for GitHub Actions
# This script creates a service account with necessary permissions for CI/CD

$PROJECT_ID = "project-71e73ad8-4a84-471e-b69"
$SA_NAME = "github-actions-cicd"
$SA_EMAIL = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
$KEY_FILE = "github-actions-key.json"

Write-Host "Setting up GitHub Actions Service Account..." -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host ""

# Set the project
Write-Host "Setting GCP project..." -ForegroundColor Cyan
gcloud config set project $PROJECT_ID

# Check if service account exists
Write-Host "`nChecking if service account exists..." -ForegroundColor Cyan
$saExists = gcloud iam service-accounts list --filter="email:$SA_EMAIL" --format="value(email)" 2>$null

if (-not $saExists) {
    Write-Host "Creating service account: $SA_NAME" -ForegroundColor Green
    gcloud iam service-accounts create $SA_NAME --display-name="GitHub Actions CI/CD" --description="Service account for GitHub Actions deployment"
}
else {
    Write-Host "Service account already exists: $SA_EMAIL" -ForegroundColor Yellow
}

# Grant necessary roles
Write-Host "`nGranting IAM roles..." -ForegroundColor Cyan

$roles = @(
    "roles/artifactregistry.writer",
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/storage.objectAdmin"
)

foreach ($role in $roles) {
    Write-Host "  Granting $role" -ForegroundColor Gray
    gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="$role" --condition=None --quiet | Out-Null
}

Write-Host "All roles granted successfully" -ForegroundColor Green

# Create service account key
Write-Host "`nCreating service account key..." -ForegroundColor Cyan
if (Test-Path $KEY_FILE) {
    Write-Host "Removing old key file..." -ForegroundColor Yellow
    Remove-Item $KEY_FILE -Force
}

gcloud iam service-accounts keys create $KEY_FILE --iam-account=$SA_EMAIL

if (Test-Path $KEY_FILE) {
    Write-Host "Service account key created: $KEY_FILE" -ForegroundColor Green
    
    # Read the key
    $keyContent = Get-Content $KEY_FILE -Raw
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Go to your GitHub repository:" -ForegroundColor White
    Write-Host "   Settings > Secrets and variables > Actions" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Create or update the secret:" -ForegroundColor White
    Write-Host "   Name: GCP_SA_KEY" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Copy the JSON content below as the secret value:" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host $keyContent -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "IMPORTANT: Delete the key file after copying:" -ForegroundColor Red
    Write-Host "   Remove-Item $KEY_FILE -Force" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Service Account Email: $SA_EMAIL" -ForegroundColor Cyan
    Write-Host ""
}
else {
    Write-Host "Failed to create service account key" -ForegroundColor Red
    exit 1
}
