# Quick Email Notification Setup Script - Gmail Only
# Run this after deploying the retraining pipeline

param(
    [Parameter(Mandatory=$true)]
    [string]$NotificationEmail,
    
    [Parameter(Mandatory=$false)]
    [string]$GmailUser,
    
    [Parameter(Mandatory=$false)]
    [string]$GmailAppPassword
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Gmail Email Notification Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = gcloud config get-value project
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
$REGION = "asia-southeast1"

Write-Host "[1/4] Setting up Gmail SMTP..." -ForegroundColor Yellow

if (-not $GmailUser) {
    $GmailUser = Read-Host "Enter your Gmail address"
}

if (-not $GmailAppPassword) {
    Write-Host ""
    Write-Host "WARNING: You need a Gmail App Password (not your regular password)" -ForegroundColor Yellow
    Write-Host "    Get it from: https://myaccount.google.com/apppasswords" -ForegroundColor Cyan
    Write-Host ""
    $GmailAppPassword = Read-Host "Enter your Gmail App Password (without spaces)"
}

# Store credentials
Write-Host "  - Storing credentials in Secret Manager..."
echo -n $GmailUser | gcloud secrets create gmail-user --data-file=- 2>$null
if ($LASTEXITCODE -ne 0) {
    echo -n $GmailUser | gcloud secrets versions add gmail-user --data-file=-
}

echo -n $GmailAppPassword | gcloud secrets create gmail-app-password --data-file=- 2>$null
if ($LASTEXITCODE -ne 0) {
    echo -n $GmailAppPassword | gcloud secrets versions add gmail-app-password --data-file=-
}

# Grant access
Write-Host "  - Granting Secret Manager access..."
gcloud secrets add-iam-policy-binding gmail-user `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --quiet

gcloud secrets add-iam-policy-binding gmail-app-password `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --quiet

Write-Host "[2/4] Updating Cloud Run Job..." -ForegroundColor Yellow
gcloud run jobs update retrain-job `
    --region=$REGION `
    --set-env-vars="GCS_BUCKET=credit-scoring-retrain-976448868286,MIN_SAMPLES=500,MIN_AUC_IMPROVEMENT=0.02,PROMOTION_THRESHOLD=0.86,NOTIFICATION_EMAIL=$NotificationEmail" `
    --set-secrets="GMAIL_USER=gmail-user:latest,GMAIL_APP_PASSWORD=gmail-app-password:latest" `
    --quiet

Write-Host "[3/4] Verifying configuration..." -ForegroundColor Yellow
$job_config = gcloud run jobs describe retrain-job --region=$REGION --format=json | ConvertFrom-Json
$has_email = $job_config.spec.template.spec.template.spec.containers[0].env | Where-Object { $_.name -eq "NOTIFICATION_EMAIL" }

if ($has_email) {
    Write-Host "  [OK] Email notification configured" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Configuration failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[4/4] Testing email notification...(Optional)" -ForegroundColor Yellow
$test = Read-Host "Do you want to test now? (y/n)"

if ($test -eq "y") {
    Write-Host "  - Executing retraining job..."
    gcloud run jobs execute retrain-job --region=$REGION --wait
    Write-Host ""
    Write-Host "  [OK] Job executed. Check your email: $NotificationEmail" -ForegroundColor Green
    Write-Host "  (Check spam folder if not in inbox)" -ForegroundColor Yellow
} else {
    Write-Host "  Skipped test. You can test later with:" -ForegroundColor Yellow
    Write-Host "  gcloud run jobs execute retrain-job --region=$REGION --wait" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "[SUCCESS] Gmail notifications configured!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next automatic notification: Sunday 3 AM (weekly)" -ForegroundColor Cyan
Write-Host "Notification email: $NotificationEmail" -ForegroundColor Cyan
Write-Host ""
