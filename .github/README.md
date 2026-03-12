# GitHub Actions CI/CD Setup

This directory contains GitHub Actions workflows and setup scripts for automated deployment to Google Cloud Platform.

## 🚀 Quick Setup (First Time Only)

### Step 1: Create Service Account

**Windows (PowerShell):**
```powershell
cd .github
.\setup-github-actions-sa.ps1
```

**Linux/Mac:**
```bash
cd .github
chmod +x setup-github-actions-sa.sh
./setup-github-actions-sa.sh
```

### Step 2: Add Secret to GitHub

1. The script creates `github-actions-key.json`
2. Copy the entire JSON content:
   ```powershell
   Get-Content github-actions-key.json | Set-Clipboard  # Windows
   cat github-actions-key.json | pbcopy  # macOS
   ```
3. Go to your GitHub repo: **Settings → Secrets and variables → Actions**
4. Click **New repository secret**
5. Name: `GCP_SA_KEY`
6. Value: Paste the JSON content
7. Click **Add secret**

### Step 3: Delete the Key File

⚠️ **Important:** Delete the key file after adding to GitHub!

```powershell
Remove-Item github-actions-key.json  # Windows
rm github-actions-key.json  # Linux/Mac
```

---

## 📋 Workflows

### `deploy-gcp.yml` - Deploy to Cloud Run

**Triggers:**
- Push to `main` branch
- Push to `production` branch
- Manual trigger (workflow_dispatch)

**What it does:**
1. ✓ Authenticates with GCP
2. ✓ Enables required APIs (Artifact Registry, Cloud Run, Cloud Build)
3. ✓ Creates Artifact Registry repository (if not exists)
4. ✓ Builds Docker image using Cloud Build
5. ✓ Deploys to Cloud Run in `asia-southeast1` region
6. ✓ Displays service URL

**Configuration:**
```yaml
PROJECT_ID: project-71e73ad8-4a84-471e-b69
REGION: asia-southeast1
SERVICE_NAME: credit-scoring-api
REPOSITORY: credit-scoring
```

---

## 🔐 Service Account Permissions

The GitHub Actions service account has these roles:

| Role | Purpose |
|------|---------|
| `roles/run.admin` | Deploy and manage Cloud Run services |
| `roles/artifactregistry.writer` | Push Docker images |
| `roles/iam.serviceAccountUser` | Act as service account |
| `roles/cloudbuild.builds.editor` | Create Cloud Build jobs |
| `roles/serviceusage.serviceUsageConsumer` | Enable APIs |

---

## 🧪 Testing the Workflow

### Manual Trigger

1. Go to **Actions** tab in GitHub
2. Select **Deploy to Google Cloud Run**
3. Click **Run workflow**
4. Select branch (main/production)
5. Click **Run workflow**

### Automatic Trigger

```bash
# Make any change
git add .
git commit -m "trigger deployment"
git push origin main
```

---

## 📊 Monitoring Deployment

### View Workflow Logs

1. Go to **Actions** tab
2. Click on the workflow run
3. Click on **deploy** job
4. Expand each step to see logs

### View Cloud Run Service

After successful deployment:
```bash
# View service details
gcloud run services describe credit-scoring-api --region=asia-southeast1

# View service URL
gcloud run services describe credit-scoring-api \
  --region=asia-southeast1 \
  --format='value(status.url)'

# View logs
gcloud run services logs read credit-scoring-api --region=asia-southeast1 --limit=50
```

---

## 🔧 Troubleshooting

### Issue: "Unauthenticated request"

**Cause:** Service account key not configured or incorrect

**Solution:**
1. Re-run setup script: `.\setup-github-actions-sa.ps1`
2. Update GitHub secret with new key
3. Retry deployment

### Issue: "Repository does not exist"

**Cause:** Artifact Registry repository not created

**Solution:** The workflow now auto-creates the repository. If it still fails:
```bash
gcloud artifacts repositories create credit-scoring \
  --repository-format=docker \
  --location=asia-southeast1
```

### Issue: "Permission denied"

**Cause:** Service account lacks required permissions

**Solution:** Re-run setup script to grant all permissions:
```powershell
.\setup-github-actions-sa.ps1
```

### Issue: "Cloud Build timeout"

**Cause:** Build takes longer than default timeout

**Solution:** Already configured with 20-minute timeout. If still failing, check:
- Dockerfile efficiency
- Network issues
- Dependencies size

### Issue: "Secret not found"

**Cause:** Cloud Run secrets (API keys) not created

**Solution:**
```bash
# Create required secrets
echo -n "YOUR_SECRET_KEY" | gcloud secrets create credit-api-secret-key --data-file=-
echo -n "YOUR_API_KEY" | gcloud secrets create credit-api-key --data-file=-

# Grant access
PROJECT_NUMBER=$(gcloud projects describe project-71e73ad8-4a84-471e-b69 --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding credit-api-secret-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding credit-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)

---

## 🔄 Update Workflow

To modify the deployment:

1. Edit `.github/workflows/deploy-gcp.yml`
2. Update environment variables or steps
3. Commit and push
4. Workflow runs automatically

**Common Changes:**
```yaml
# Change region
REGION: us-central1

# Change memory/CPU
--memory 4Gi \
--cpu 4 \

# Change scaling
--min-instances 1 \
--max-instances 20 \
```

---

**Status:** ✅ Fully configured and tested  
**Last Updated:** March 12, 2026
