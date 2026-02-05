# Render Deployment Guide - Credit Scoring API with XGBoost

## 🚀 Quick Deploy to Render

### Prerequisites
- GitHub account
- Render account (free tier available)
- Code pushed to GitHub repository

---

## Step 1: Prepare Repository

### 1.1 Ensure Required Files Exist
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Render startup command
- ✅ `.env` - Environment variables (DO NOT commit this!)
- ✅ XGBoost model file at `../output/models/xgboost_final.pkl`

### 1.2 Update `.gitignore`
Make sure `.env` is in `.gitignore`:
```
.env
*.pkl
__pycache__/
*.pyc
```

### 1.3 Commit and Push
```bash
git add .
git commit -m "Add XGBoost model and Render deployment config"
git push origin main
```

---

## Step 2: Create Web Service on Render

### 2.1 Go to Render Dashboard
1. Visit https://render.com
2. Click "New +" → "Web Service"

### 2.2 Connect Repository
1. Connect your GitHub account
2. Select your repository: `Credit-Scoring`
3. Click "Connect"

### 2.3 Configure Service

**Basic Settings:**
- **Name:** `credit-scoring-api`
- **Region:** Singapore (or closest to your users)
- **Branch:** `main`
- **Root Directory:** `credit-scoring-api`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Free tier: 512 MB RAM (may be slow)
- **Recommended:** Starter ($7/month) - 512 MB RAM
- **Better:** Standard ($25/month) - 2 GB RAM (for ML models)

---

## Step 3: Set Environment Variables

In Render dashboard, go to "Environment" tab and add:

### Required Variables:
```
SECRET_KEY=E6QlhIxLscoqY9cBfxxu98yJcDzK9uhlAVm5nMyP000
API_KEY=dtuNV40UX0RxID96Z1-d-z1WdoA-RmMECuuDGJPwfWk
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Model Settings:
```
USE_XGBOOST=True
XGBOOST_THRESHOLD=0.86
LIGHTGBM_THRESHOLD=0.12
XGB_MODEL_PATH=../output/models/xgboost_final.pkl
LGBM_MODEL_PATH=models/lgb_model_optimized.pkl
METADATA_PATH=models/ensemble_comparison_metadata.pkl
```

### CORS Settings:
```
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://another-domain.com
```

### Rate Limiting:
```
RATE_LIMIT_CALCULATE_LIMIT=10
RATE_LIMIT_CALCULATE_TERMS=10
RATE_LIMIT_APPLY=5
RATE_LIMIT_BATCH=2
```

---

## Step 4: Handle Model Files

### ⚠️ Important: Model File Size Issue

XGBoost model files are large (100MB+). Render has limitations:

**Option 1: Include in Repository (if < 100MB)**
```bash
# Remove *.pkl from .gitignore temporarily
git add output/models/xgboost_final.pkl
git add credit-scoring-api/models/*.pkl
git commit -m "Add model files"
git push
```

**Option 2: Use External Storage (Recommended for large models)**
1. Upload models to Google Cloud Storage / AWS S3 / Dropbox
2. Download during build:

Create `download_models.sh`:
```bash
#!/bin/bash
mkdir -p output/models
mkdir -p models

# Download from your storage
curl -o output/models/xgboost_final.pkl "YOUR_MODEL_URL"
curl -o models/lgb_model_optimized.pkl "YOUR_LGBM_URL"
curl -o models/ensemble_comparison_metadata.pkl "YOUR_METADATA_URL"
```

Update Build Command in Render:
```
chmod +x download_models.sh && ./download_models.sh && pip install -r requirements.txt
```

**Option 3: Use Git LFS**
```bash
git lfs install
git lfs track "*.pkl"
git add .gitattributes
git add output/models/*.pkl
git commit -m "Add models with Git LFS"
git push
```

---

## Step 5: Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Monitor build logs for errors

---

## Step 6: Test Deployment

### Get Your Service URL
Render will provide a URL like: `https://credit-scoring-api.onrender.com`

### Test Health Endpoint
```bash
curl https://credit-scoring-api.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-02-05T12:55:00Z"
}
```

### Test Model Info
```bash
curl https://credit-scoring-api.onrender.com/api/model/info
```

Expected response:
```json
{
  "model_name": "XGBoost",
  "threshold": 0.86,
  "performance": {
    "roc_auc": 0.7042,
    "precision": 0.2017,
    ...
  }
}
```

### Test Prediction (with API Key)
```bash
curl https://credit-scoring-api.onrender.com/api/calculate-limit \
  -H "X-API-Key: dtuNV40UX0RxID96Z1-d-z1WdoA-RmMECuuDGJPwfWk" \
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
```

---

## Step 7: Monitor & Troubleshoot

### View Logs
1. Go to Render dashboard
2. Click on your service
3. Go to "Logs" tab

### Common Issues

**Issue 1: Model file not found**
```
Error loading models: No such file or directory
```
**Solution:** Check model paths in environment variables

**Issue 2: Out of memory**
```
Killed (OOM)
```
**Solution:** Upgrade to larger instance (Standard plan with 2GB RAM)

**Issue 3: Slow cold starts**
```
Request timeout
```
**Solution:** 
- Keep service warm with health check pings
- Upgrade instance type
- Reduce model size

**Issue 4: Module not found**
```
ModuleNotFoundError: No module named 'xgboost'
```
**Solution:** Ensure `xgboost==2.0.3` is in `requirements.txt`

---

## Step 8: Production Checklist

- [ ] Environment variables set correctly
- [ ] API_KEY is secure (not the default one)
- [ ] CORS origins configured for your frontend
- [ ] Model files uploaded successfully
- [ ] Health endpoint returns 200
- [ ] Model info shows "XGBoost"
- [ ] Predictions work with API key
- [ ] Logs show no errors
- [ ] Response times acceptable (<2s)

---

## Useful Render Features

### Auto-Deploy
- Render auto-deploys on every `git push` to main branch
- Can disable in Settings → "Auto-Deploy"

### Custom Domain
1. Go to Settings → Custom Domains
2. Add your domain
3. Update DNS records

### Health Checks
Render automatically pings `/` endpoint
- Can customize in Settings → Health Check Path
- Set to `/api/health`

### Scaling
- Free tier: 1 instance, spins down after inactivity
- Paid tier: Always-on, can scale horizontally

---

## Cost Estimate

**Free Tier:**
- ✅ 750 hours/month
- ❌ Spins down after 15 min inactivity
- ❌ 512 MB RAM (may not be enough for XGBoost)

**Starter ($7/month):**
- ✅ Always-on
- ⚠️ 512 MB RAM (tight for ML models)

**Standard ($25/month):** ⭐ Recommended
- ✅ Always-on
- ✅ 2 GB RAM (comfortable for XGBoost)
- ✅ Better performance

---

## Next Steps After Deployment

1. **Update Frontend:**
   - Change API URL to Render URL
   - Update CORS settings

2. **Monitor Performance:**
   - Check response times
   - Monitor error rates
   - Track prediction accuracy

3. **Set Up Alerts:**
   - Use Render notifications
   - Set up uptime monitoring (UptimeRobot, Pingdom)

4. **A/B Testing:**
   - Toggle `USE_XGBOOST` to switch models
   - Compare performance

---

## Rollback Plan

If XGBoost causes issues:

1. **Quick Fix:** Set environment variable
   ```
   USE_XGBOOST=False
   ```
   This switches back to LightGBM immediately

2. **Full Rollback:** Revert git commit
   ```bash
   git revert HEAD
   git push
   ```

---

## Support

**Render Documentation:** https://render.com/docs
**Render Status:** https://status.render.com
**Community:** https://community.render.com
