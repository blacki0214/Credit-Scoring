# Student Model Production Fast Track

Muc tieu: len production nhanh va an toan cho luong student scoring.

## 1) Policy profile

Su dung bien moi truong STUDENT_DECISION_POLICY:
- safe: review window rong, giam auto-approve
- balanced: can bang, phu hop cho default
- aggressive: review window hep, tang auto-approve

Bien bo tro:
- STUDENT_MANUAL_REVIEW_MARGIN (0.00-0.25)

Khuyen nghi go-live dau tien:
- STUDENT_DECISION_POLICY=safe
- STUDENT_MANUAL_REVIEW_MARGIN=0.10

## 2) Pre-deploy checks

1. Chay test student:
   python -m pytest credit-scoring-api/tests/test_student_feature_contract.py credit-scoring-api/tests/test_prediction.py -k "student" -q
2. Kiem tra runtime assets:
   python -c "import sys, json; sys.path.insert(0, 'credit-scoring-api'); from app.services.student_prediction_service import student_prediction_service; print(json.dumps(student_prediction_service.validate_runtime_assets(strict=False), indent=2))"
3. Kiem tra model + threshold + calibrator duoc load dung duong dan.

## 3) Deploy canary nhanh (Cloud Run)

1. Deploy revision voi policy safe:
   - set env vars:
     ENVIRONMENT=production
     STUDENT_DECISION_POLICY=safe
     STUDENT_MANUAL_REVIEW_MARGIN=0.10
2. Chia traffic 10% revision moi, 90% revision cu.
3. Theo doi 24-48h:
   - approve_rate
   - bad_approve_rate (can manual sample neu chua co label day du)
   - manual_review_rate
   - error_rate / latency
4. Neu on dinh, nang len 30% -> 50% -> 100%.

### Lenh traffic split mau

Luu y: thay SERVICE va REGION theo he thong cua ban.

```bash
# Xem danh sach revision
gcloud run revisions list --service=credit-scoring-api --region=asia-southeast1

# Vi du dat traffic 90% revision cu, 10% revision moi
gcloud run services update-traffic credit-scoring-api \
   --region=asia-southeast1 \
   --to-revisions credit-scoring-api-00034-abc=90,credit-scoring-api-00035-def=10

# Tang len 70/30
gcloud run services update-traffic credit-scoring-api \
   --region=asia-southeast1 \
   --to-revisions credit-scoring-api-00034-abc=70,credit-scoring-api-00035-def=30

# Tang len 50/50
gcloud run services update-traffic credit-scoring-api \
   --region=asia-southeast1 \
   --to-revisions credit-scoring-api-00034-abc=50,credit-scoring-api-00035-def=50

# Full traffic cho revision moi
gcloud run services update-traffic credit-scoring-api \
   --region=asia-southeast1 \
   --to-revisions credit-scoring-api-00035-def=100
```

### Endpoint monitoring moi (bao ve bang API key)

```bash
curl "https://<your-cloud-run-url>/api/student/monitoring/summary?hours=24" \
   -H "X-API-Key: <YOUR_API_KEY>"
```

Response co cac chi so chinh de canary gating:
- total_applications
- approve_rate
- manual_review_rate
- reject_rate
- student_decision_policy
- student_threshold

### Script rollout tu dong (PowerShell)

Script: credit-scoring-api/scripts/student_canary_rollout.ps1

Vi du dung script:

```powershell
# 1) Xem plan (tu lay revision moi/old)
./credit-scoring-api/scripts/student_canary_rollout.ps1 `
   -ProjectId "<YOUR_PROJECT_ID>" `
   -ServiceName "credit-scoring-api" `
   -Region "asia-southeast1" `
   -Action plan

# 2) Day 10% traffic
./credit-scoring-api/scripts/student_canary_rollout.ps1 `
   -ProjectId "<YOUR_PROJECT_ID>" `
   -ServiceName "credit-scoring-api" `
   -Region "asia-southeast1" `
   -Action apply-10

# 3) Day 30% traffic
./credit-scoring-api/scripts/student_canary_rollout.ps1 `
   -ProjectId "<YOUR_PROJECT_ID>" `
   -ServiceName "credit-scoring-api" `
   -Region "asia-southeast1" `
   -Action apply-30

# 4) Monitoring KPI 24h
./credit-scoring-api/scripts/student_canary_rollout.ps1 `
   -ProjectId "<YOUR_PROJECT_ID>" `
   -ServiceName "credit-scoring-api" `
   -Region "asia-southeast1" `
   -Action monitor `
   -Hours 24 `
   -ApiKey "<YOUR_API_KEY>"
```

## 4) Rollback plan

Khi KPI xau di:
1. Chuyen traffic ve revision cu.
2. Giam policy tu aggressive/balanced xuong safe.
3. Tang margin review.

## 5) KPI gating de tang traffic

Chi tang traffic neu dat dong thoi:
- error rate endpoint student < 1%
- p95 latency trong nguong he thong
- manual_review_rate nam trong kha nang van hanh
- bad_approve_rate khong vuot muc policy noi bo

## 6) Ghi chu quan trong

Neu thay canh bao tu XGBoost ve serialized model compatibility, nen len ke hoach chuyen qua dung Booster.save_model/load_model de on dinh dai han.
