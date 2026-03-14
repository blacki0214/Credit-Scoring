# Email Notification Setup Guide

Receive automated email reports when model retraining completes, including:
- ✅ Model performance metrics (AUC, Precision, Recall, F1)
- 📊 Comparison with production model
- 🚀 Promotion status
- 📧 HTML-formatted professional report

---

## Choose Your Email Method

### **Option 1: SendGrid (Recommended)** ⭐
- ✅ Free tier: 100 emails/day
- ✅ Easy setup
- ✅ Reliable delivery
- ✅ Professional sender

### **Option 2: Gmail SMTP**
- ✅ Free (uses your Gmail account)
- ⚠️ Requires App Password
- ⚠️ Daily sending limits

---

## 🚀 Quick Setup

### Option 1: SendGrid Setup

#### Step 1: Create SendGrid Account
1. Go to https://signup.sendgrid.com/,
2. Sign up for free account (100 emails/day free)
3. Verify your email address

#### Step 2: Get API Key
```bash
# 1. Log into SendGrid dashboard
# 2. Go to Settings > API Keys
# 3. Click "Create API Key"
# 4. Name: "credit-scoring-retraining"
# 5. Permission: "Full Access" or "Mail Send"
# 6. Copy the API key (you'll only see it once!)
```

#### Step 3: Store API Key in GCP Secret Manager
```powershell
# Store SendGrid API key in Secret Manager
$SENDGRID_API_KEY = "SG.xxxxxxxxxxxxxxxxxxxxx"  # Replace with your key
echo -n $SENDGRID_API_KEY | gcloud secrets create sendgrid-api-key --data-file=-

# Grant access to Cloud Run service account
$PROJECT_NUMBER = gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)"
gcloud secrets add-iam-policy-binding sendgrid-api-key `
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"
```

#### Step 4: Update Cloud Run Job
```powershell
cd credit-scoring-api\pipeline

# Redeploy with email configuration
gcloud run jobs update retrain-job `
  --region=asia-southeast1 `
  --set-env-vars="GCS_BUCKET=credit-scoring-retrain-976448868286,MIN_SAMPLES=500,MIN_AUC_IMPROVEMENT=0.02,PROMOTION_THRESHOLD=0.86,EMAIL_METHOD=sendgrid,NOTIFICATION_EMAIL=your-email@gmail.com,SENDER_EMAIL=noreply@creditscoring.app" `
  --set-secrets="SENDGRID_API_KEY=sendgrid-api-key:latest"
```

---

### Option 2: Gmail SMTP Setup

#### Step 1: Create Gmail App Password
1. Go to Google Account: https://myaccount.google.com/
2. Navigate to **Security** > **2-Step Verification** (enable if not already)
3. Scroll to **App passwords**
4. Click **Select app** > **Mail**
5. Click **Select device** > **Other** > Type "GCP Retraining"
6. Click **Generate**
7. Copy the 16-character app password

#### Step 2: Store Credentials in Secret Manager
```powershell
# Store Gmail credentials
echo -n "your-email@gmail.com" | gcloud secrets create gmail-user --data-file=-
echo -n "your-16-char-app-password" | gcloud secrets create gmail-app-password --data-file=-

# Grant access
$PROJECT_NUMBER = gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)"

gcloud secrets add-iam-policy-binding gmail-user `
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gmail-app-password `
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"
```

#### Step 3: Update Cloud Run Job
```powershell
cd credit-scoring-api\pipeline

gcloud run jobs update retrain-job `
  --region=asia-southeast1 `
  --set-env-vars="GCS_BUCKET=credit-scoring-retrain-976448868286,MIN_SAMPLES=500,MIN_AUC_IMPROVEMENT=0.02,PROMOTION_THRESHOLD=0.86,EMAIL_METHOD=gmail,NOTIFICATION_EMAIL=recipient@gmail.com" `
  --set-secrets="GMAIL_USER=gmail-user:latest,GMAIL_APP_PASSWORD=gmail-app-password:latest"
```

---

## 📧 Email Report Preview

When retraining completes, you'll receive an HTML email like this:

```
🤖 Credit Scoring Model Retraining Report
✅ MODEL PROMOTED TO PRODUCTION

📈 New Model Performance
┌─────────────────────┬──────────┐
│ AUC-ROC             │ 0.7850   │
│ Precision           │ 0.8600   │
│ Recall              │ 0.4200   │
│ F1-Score            │ 0.5600   │
│ Test Samples        │ 150      │
│ Positive Rate       │ 30.00%   │
│ Decision Threshold  │ 0.86     │
└─────────────────────┴──────────┘

📊 Model Comparison
┌────────────┬────────────┬───────────┬──────────┐
│ Metric     │ Production │ New Model │ Change   │
├────────────┼────────────┼───────────┼──────────┤
│ AUC-ROC    │ 0.7654     │ 0.7850    │ +0.0196  │
│ Precision  │ 0.8400     │ 0.8600    │ +0.0200  │
│ Recall     │ 0.4000     │ 0.4200    │ +0.0200  │
└────────────┴────────────┴───────────┴──────────┘

[📁 View Models in GCS]
```

---

## 🧪 Test Email Notification

Test the notification system locally or manually trigger:

```powershell
# Manual test execution (triggers email)
gcloud run jobs execute retrain-job --region=asia-southeast1 --wait

# Check logs for email confirmation
gcloud logging read "resource.type=cloud_run_job AND textPayload=~'Email notification'" --limit=10
```

---

## 🔧 Deployment Script Updates

### For New Deployments

Update `deploy.ps1` or `deploy.sh` to include email configuration:

**deploy.ps1** (Windows):
```powershell
# Add after job creation/update:
gcloud run jobs update retrain-job `
  --region $REGION `
  --set-env-vars "GCS_BUCKET=credit-scoring-retrain-976448868286,MIN_SAMPLES=500,MIN_AUC_IMPROVEMENT=0.02,PROMOTION_THRESHOLD=0.86,EMAIL_METHOD=sendgrid,NOTIFICATION_EMAIL=your-email@gmail.com,SENDER_EMAIL=noreply@creditscoring.app" `
  --set-secrets "SENDGRID_API_KEY=sendgrid-api-key:latest"
```

**deploy.sh** (Linux/Mac):
```bash
gcloud run jobs update retrain-job \
  --region $REGION \
  --set-env-vars "GCS_BUCKET=credit-scoring-retrain-976448868286,MIN_SAMPLES=500,MIN_AUC_IMPROVEMENT=0.02,PROMOTION_THRESHOLD=0.86,EMAIL_METHOD=sendgrid,NOTIFICATION_EMAIL=your-email@gmail.com,SENDER_EMAIL=noreply@creditscoring.app" \
  --set-secrets "SENDGRID_API_KEY=sendgrid-api-key:latest"
```

---

## 📋 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_METHOD` | Yes | `sendgrid` | Email provider: `sendgrid` or `gmail` |
| `NOTIFICATION_EMAIL` | Yes | - | Recipient email address |
| `SENDER_EMAIL` | SendGrid only | `noreply@creditscoring.app` | Sender email address |
| `SENDGRID_API_KEY` | SendGrid only | - | SendGrid API key (from Secret Manager) |
| `GMAIL_USER` | Gmail only | - | Gmail address (from Secret Manager) |
| `GMAIL_APP_PASSWORD` | Gmail only | - | Gmail app password (from Secret Manager) |

---

## 🐛 Troubleshooting

### Email Not Received

**Check logs:**
```powershell
gcloud logging read "resource.type=cloud_run_job" --limit=100 --format=text | Select-String "email"
```

**Common Issues:**

1. **SendGrid: "401 Unauthorized"**
   - Verify API key is correct
   - Check Secret Manager binding
   - Regenerate API key if needed

2. **Gmail: "Authentication failed"**
   - Ensure 2-Step Verification is enabled
   - Use App Password (not regular password)
   - Check credentials in Secret Manager

3. **No email sent:**
   - Check NOTIFICATION_EMAIL is set
   - Verify service account has Secret Manager access
   - Check spam folder

4. **Secret not found:**
```powershell
# List secrets
gcloud secrets list

# Grant access again
$PROJECT_NUMBER = gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)"
gcloud secrets add-iam-policy-binding sendgrid-api-key `
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"
```

---

## 💡 Advanced: Custom Email Templates

To customize the email template, edit `email_notifier.py`:

```python
# Modify the generate_html_report() function
# Add custom sections, styling, or metrics
```

---

## 📬 Notification Types

The system sends emails for:

1. ✅ **Successful Training with Promotion**
   - Subject: "✅ Model Promoted - Credit Scoring Retraining"
   - Includes full comparison and metrics

2. ⚠️ **Successful Training without Promotion**
   - Subject: "⚠️ Model Not Promoted - Credit Scoring Retraining"
   - Model saved to staging for manual review

3. ❌ **Training Failure**
   - Subject: "❌ Model Retraining Failed - Credit Scoring"
   - Includes error details

---

## ✅ Verification Checklist

- [ ] Email provider configured (SendGrid or Gmail)
- [ ] API key/password stored in Secret Manager
- [ ] Secret Manager permissions granted
- [ ] Cloud Run Job updated with email variables
- [ ] Test email received successfully
- [ ] Checked spam folder
- [ ] Logs show "✓ Email notification sent"

---

## 🎯 Next Steps

After setup:
1. Test with manual execution
2. Wait for weekly scheduled run
3. Receive automated reports every Sunday at 3 AM
4. Monitor model performance trends

**Your email notifications are ready! 📧✨**
