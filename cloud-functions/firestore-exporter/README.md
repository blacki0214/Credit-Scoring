# Firestore to GCS Exporter

Cloud Function that exports loan applications from Firestore to GCS for model retraining.

## Setup

1. Install gcloud CLI
2. Authenticate:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. Enable required APIs:
   ```bash
   gcloud services enable cloudfunctions.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable firestore.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

## Deployment

```bash
chmod +x deploy.sh
./deploy.sh
```

Or manually:

```bash
gcloud functions deploy export-firestore-to-gcs \
  --gen2 \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --region asia-southeast1 \
  --memory 512MB \
  --timeout 300s \
  --entry-point export_firestore_to_gcs \
  --source .
```

## Schedule Weekly Export

```bash
gcloud scheduler jobs create http firestore-export-weekly \
  --schedule="0 2 * * 0" \
  --uri="https://asia-southeast1-YOUR_PROJECT.cloudfunctions.net/export-firestore-to-gcs" \
  --location=asia-southeast1 \
  --http-method=POST
```

## Manual Trigger

```bash
curl -X POST https://asia-southeast1-YOUR_PROJECT.cloudfunctions.net/export-firestore-to-gcs
```

## Output

Exports are saved to:
- Data: `gs://retrain/data/exports/loan_applications_YYYYMMDD_HHMMSS.parquet`
- Metadata: `gs://retrain/data/exports/metadata_YYYYMMDD_HHMMSS.json`
