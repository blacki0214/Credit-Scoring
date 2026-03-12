# Setup Workload Identity Federation for GitHub Actions
# This is more secure than using service account keys

$PROJECT_ID = "project-71e73ad8-4a84-471e-b69"
$PROJECT_NUMBER = "976448868286"
$GITHUB_REPO = "blacki0214/Credit-Scoring"  # Your GitHub username/repo
$SA_EMAIL = "github-actions-cicd@$PROJECT_ID.iam.gserviceaccount.com"
$POOL_NAME = "github-actions-pool"
$PROVIDER_NAME = "github-provider"
$LOCATION = "global"

Write-Host "Setting up Workload Identity Federation for GitHub Actions" -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "GitHub Repo: $GITHUB_REPO" -ForegroundColor Yellow
Write-Host ""

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable iamcredentials.googleapis.com
gcloud services enable sts.googleapis.com
Write-Host "APIs enabled" -ForegroundColor Green
Write-Host ""

# Create Workload Identity Pool
Write-Host "Creating Workload Identity Pool..." -ForegroundColor Cyan
$poolExists = gcloud iam workload-identity-pools describe $POOL_NAME --location=$LOCATION 2>$null
if (-not $poolExists) {
    gcloud iam workload-identity-pools create $POOL_NAME `
        --location=$LOCATION `
        --display-name="GitHub Actions Pool"
    Write-Host "Workload Identity Pool created" -ForegroundColor Green
}
else {
    Write-Host "Workload Identity Pool already exists" -ForegroundColor Yellow
}
Write-Host ""

# Create Workload Identity Provider
Write-Host "Creating Workload Identity Provider..." -ForegroundColor Cyan
$providerExists = gcloud iam workload-identity-pools providers describe $PROVIDER_NAME --location=$LOCATION --workload-identity-pool=$POOL_NAME 2>$null
if (-not $providerExists) {
    gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME `
        --location=$LOCATION `
        --workload-identity-pool=$POOL_NAME `
        --display-name="GitHub Provider" `
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" `
        --attribute-condition="assertion.repository_owner == '$($GITHUB_REPO.Split('/')[0])'" `
        --issuer-uri="https://token.actions.githubusercontent.com"
    Write-Host "Workload Identity Provider created" -ForegroundColor Green
}
else {
    Write-Host "Workload Identity Provider already exists" -ForegroundColor Yellow
}
Write-Host ""

# Grant service account permissions to the workload identity
Write-Host "Granting workload identity permissions..." -ForegroundColor Cyan
$member = "principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/$LOCATION/workloadIdentityPools/$POOL_NAME/attribute.repository/$GITHUB_REPO"
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL `
    --role="roles/iam.workloadIdentityUser" `
    --member="$member"
Write-Host "Permissions granted" -ForegroundColor Green
Write-Host ""

# Generate the Workload Identity Provider resource name
$WORKLOAD_IDENTITY_PROVIDER = "projects/$PROJECT_NUMBER/locations/$LOCATION/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Add these secrets to your GitHub repository:" -ForegroundColor Yellow
Write-Host "Settings > Secrets and variables > Actions" -ForegroundColor Gray
Write-Host ""
Write-Host "1. GCP_PROJECT_ID:" -ForegroundColor White
Write-Host "   $PROJECT_ID" -ForegroundColor Green
Write-Host ""
Write-Host "2. GCP_SERVICE_ACCOUNT:" -ForegroundColor White
Write-Host "   $SA_EMAIL" -ForegroundColor Green
Write-Host ""
Write-Host "3. GCP_WORKLOAD_IDENTITY_PROVIDER:" -ForegroundColor White
Write-Host "   $WORKLOAD_IDENTITY_PROVIDER" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your GitHub Actions workflow will use these values." -ForegroundColor Cyan
Write-Host "No service account keys needed - much more secure!" -ForegroundColor Green
Write-Host ""
