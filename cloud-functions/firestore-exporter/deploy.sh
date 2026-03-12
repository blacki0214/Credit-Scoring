#!/bin/bash
# Deploy Firestore to GCS Exporter Cloud Function

set -e

echo "Deploying Firestore Exporter Cloud Function..."

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

echo "Cloud Function deployed successfully!"
echo ""
echo "To schedule weekly exports, run:"
echo ""
echo "gcloud scheduler jobs create http firestore-export-weekly \\"
echo "  --schedule=\"0 2 * * 0\" \\"
echo "  --uri=\"https://asia-southeast1-YOUR_PROJECT.cloudfunctions.net/export-firestore-to-gcs\" \\"
echo "  --location=asia-southeast1 \\"
echo "  --http-method=POST"
