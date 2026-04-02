# Operational Runbook (Tiếng Việt)

## 1) Mục tiêu
Tài liệu này hướng dẫn vận hành hệ thống Credit Scoring trên GCP theo quy trình chuẩn:
- Giám sát dịch vụ hằng ngày
- Kiểm tra pipeline export + retrain hằng tuần
- Xử lý sự cố nhanh theo playbook
- Thực hiện fire-drill định kỳ

## 2) Phạm vi hệ thống hiện tại
- Project: creditscore-c560f
- Region: asia-southeast1
- Domain API: swincredit.duckdns.org
- Static LB IP: 34.149.188.220

Thành phần chính:
- Cloud Run service: credit-scoring-api
- Cloud Function Gen2: export-firestore-to-gcs
- Cloud Run Job: retrain-job
- Cloud Scheduler jobs:
  - firestore-export-weekly (0 2 * * 0)
  - retrain-weekly (0 3 * * 0)
- GCS Bucket: credit-scoring-retrain-513943636250
- Cloud Armor policy: credit-api-armor

## 3) Checklist hằng ngày (5-10 phút)

### 3.1 API health
```powershell
Invoke-WebRequest -Uri "https://swincredit.duckdns.org/api/health" -UseBasicParsing
```
Kỳ vọng: HTTP 200.

### 3.2 Trạng thái Cloud Run service
```powershell
$PROJECT_ID = gcloud config get-value project
gcloud run services describe credit-scoring-api --region=asia-southeast1 --project=$PROJECT_ID --format="table(status.url,status.traffic[0].percent,spec.template.spec.serviceAccountName)"
```
Kỳ vọng: service hoạt động, traffic 100%, service account đúng.

### 3.3 Trạng thái alert policy
```powershell
$PROJECT_ID = gcloud config get-value project
gcloud alpha monitoring policies list --project=$PROJECT_ID --format="table(displayName,enabled)"
```
Kỳ vọng: 3 policy đều enabled.

### 3.4 Trạng thái scheduler
```powershell
$PROJECT_ID = gcloud config get-value project
gcloud scheduler jobs list --location=asia-southeast1 --project=$PROJECT_ID --format="table(name,state,schedule)"
```
Kỳ vọng: cả 2 job ở trạng thái ENABLED.

## 4) Checklist hằng tuần (sau lịch chạy Chủ nhật)

### 4.1 Kiểm tra file export mới
```powershell
$PROJECT_ID = gcloud config get-value project
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
$BUCKET = "credit-scoring-retrain-$PROJECT_NUMBER"
gsutil ls -l "gs://$BUCKET/data/exports/" | Select-Object -Last 10
```
Kỳ vọng: có parquet export mới.

### 4.2 Kiểm tra execution retrain mới nhất
```powershell
$PROJECT_ID = gcloud config get-value project
gcloud run jobs executions list --job=retrain-job --region=asia-southeast1 --project=$PROJECT_ID --limit=5
```
Kỳ vọng: execution mới nhất completed/succeeded.

### 4.3 Kiểm tra artifact model
```powershell
$PROJECT_ID = gcloud config get-value project
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
$BUCKET = "credit-scoring-retrain-$PROJECT_NUMBER"
gsutil ls -l "gs://$BUCKET/models/staging/"
gsutil ls -l "gs://$BUCKET/models/production/"
```
Kỳ vọng: có model/metadata được cập nhật theo lịch.

## 5) Lệnh vận hành nhanh

### 5.1 Chạy export thủ công
```powershell
$PROJECT_ID = gcloud config get-value project
gcloud scheduler jobs run firestore-export-weekly --location=asia-southeast1 --project=$PROJECT_ID
```

### 5.2 Chạy retrain thủ công
```powershell
$PROJECT_ID = gcloud config get-value project
gcloud run jobs execute retrain-job --region=asia-southeast1 --project=$PROJECT_ID --wait
```

### 5.3 Xem log retrain
```powershell
$PROJECT_ID = gcloud config get-value project
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=retrain-job" --project=$PROJECT_ID --limit=50 --format="table(timestamp,severity,textPayload)"
```

### 5.4 Xem log exporter
```powershell
$PROJECT_ID = gcloud config get-value project
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=export-firestore-to-gcs" --project=$PROJECT_ID --limit=50 --format="table(timestamp,severity,textPayload)"
```

## 6) Alerting hiện tại
- API 5xx Errors - credit-scoring-api (CRITICAL)
- Export Function Errors - firestore exporter (ERROR)
- Retrain Job Errors - retrain-job (ERROR)

Notification channel email:
- Credit Ops Email -> vanquoc11082004@gmail.com

## 7) Playbook xử lý sự cố

### 7.1 Lỗi bucket không tồn tại
Dấu hiệu:
- Log chứa The specified bucket does not exist

Xử lý:
1. Kiểm tra env var GCS_BUCKET trong retrain-job.
2. Kiểm tra bucket tồn tại thật trong GCS.
3. Chạy lại retrain sau khi sửa.

Lệnh:
```powershell
$PROJECT_ID = gcloud config get-value project
gcloud run jobs describe retrain-job --region=asia-southeast1 --project=$PROJECT_ID --format=yaml | Select-String -Pattern "GCS_BUCKET|value:"
```

### 7.2 Không có dữ liệu export
Dấu hiệu:
- Log chứa No data exports found in GCS

Xử lý:
1. Trigger export thủ công.
2. Xác minh có file mới ở data/exports.
3. Chạy retrain lại.

### 7.3 API lỗi HTTPS
Dấu hiệu:
- Domain timeout hoặc SSL lỗi

Xử lý:
1. Kiểm tra DNS A record trỏ đúng LB IP.
2. Kiểm tra managed cert trạng thái ACTIVE.
3. Kiểm tra forwarding rule 80/443.

## 8) Fire-drill định kỳ (khuyến nghị 1 lần/tháng)
Mục tiêu:
- Xác nhận pipeline alert bắn đúng policy, đúng severity, đúng email.

Quy trình an toàn:
1. Ghi nhận cấu hình GCS_BUCKET hiện tại.
2. Tạm đổi sang bucket giả.
3. Chạy retrain để tạo lỗi có kiểm soát.
4. Khôi phục cấu hình gốc ngay lập tức.
5. Chạy 1 execution thành công để xác nhận hệ thống khỏe lại.

## 9) Tiêu chí hoàn tất vận hành (Definition of Done)
- API health trả 200 qua domain HTTPS.
- Scheduler ENABLED.
- Export có file mới theo lịch.
- Retrain execution thành công theo lịch.
- Alert policy ENABLED và có thể bắn email khi drill.
- Không còn cấu hình hardcode bucket/project cũ trong runtime path.

## 10) Ghi chú thay đổi
Khi thay đổi cấu hình quan trọng (bucket, service account, domain, policy alert), cần:
1. Ghi changelog ngắn.
2. Chạy lại checklist mục 3 và 4.
3. Nếu thay đổi alert, chạy lại fire-drill nhẹ để xác nhận.
