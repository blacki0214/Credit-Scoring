#!/bin/bash
# Setup Service Account for GitHub Actions CI/CD
# Run this once to create and configure the service account

set -e

PROJECT_ID="project-71e73ad8-4a84-471e-b69"
SA_NAME="github-actions"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "========================================="
echo "GitHub Actions Service Account Setup"
echo "========================================="
echo ""

# Check if already logged in
echo "[1/6] Checking authentication..."
gcloud config set project $PROJECT_ID

# Create service account
echo "[2/6] Creating service account..."
if gcloud iam service-accounts describe $SA_EMAIL &>/dev/null; then
  echo "  ✓ Service account already exists"
else
  gcloud iam service-accounts create $SA_NAME \
    --display-name="GitHub Actions CI/CD" \
    --description="Service account for GitHub Actions workflow"
  echo "  ✓ Service account created"
fi

# Grant required roles
echo "[3/6] Granting IAM roles..."

echo "  - Cloud Run Admin..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.admin" \
  --quiet

echo "  - Artifact Registry Writer..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/artifactregistry.writer" \
  --quiet

echo "  - Service Account User..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountUser" \
  --quiet

echo "  - Cloud Build Editor..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/cloudbuild.builds.editor" \
  --quiet

echo "  - Service Enablement..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/serviceusage.serviceUsageConsumer" \
  --quiet

echo "  ✓ All roles granted"

# Create key
echo "[4/6] Creating service account key..."
KEY_FILE="github-actions-key.json"
if [ -f "$KEY_FILE" ]; then
  echo "  ⚠ Key file already exists: $KEY_FILE"
  read -p "  Overwrite? (y/n): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "  Skipping key creation"
    KEY_FILE=""
  else
    rm $KEY_FILE
  fi
fi

if [ -n "$KEY_FILE" ]; then
  gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SA_EMAIL
  echo "  ✓ Key created: $KEY_FILE"
fi

# Enable required APIs
echo "[5/6] Enabling required APIs..."
gcloud services enable artifactregistry.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
echo "  ✓ APIs enabled"

# Display instructions
echo "[6/6] GitHub Setup Instructions"
echo "========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Copy the service account key content:"
if [ -f "$KEY_FILE" ]; then
  echo "   cat $KEY_FILE | pbcopy  # macOS"
  echo "   cat $KEY_FILE | xclip   # Linux"
  echo "   Get-Content $KEY_FILE | Set-Clipboard  # Windows PowerShell"
  echo ""
fi
echo "2. Add to GitHub Secrets:"
echo "   • Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
echo "   • Click: 'New repository secret'"
echo "   • Name: GCP_SA_KEY"
echo "   • Value: Paste the entire JSON content from $KEY_FILE"
echo ""
echo "3. Push code to trigger workflow:"
echo "   git add .github/workflows/deploy-gcp.yml"
echo "   git commit -m 'fix: Update CI/CD workflow for Artifact Registry'"
echo "   git push origin main"
echo ""
echo "========================================="
echo "✓ Setup Complete!"
echo "========================================="
echo ""
echo "⚠ IMPORTANT: Keep $KEY_FILE secure and delete after adding to GitHub!"
echo "   rm $KEY_FILE"
