# Student API Demo Authentication

This project supports two ways to test student endpoints:

- Real Firebase bearer token (recommended for realistic test)
- Development-only auth bypass (demo only)

## Endpoints

- POST /api/student/credit-score
- POST /api/student/calculate-limit

## Option A: Real Firebase Bearer Token

### 1) Get token manually from app

- Sign in from your Flutter app.
- Get Firebase ID token from current user and copy it.
- Use header: Authorization: Bearer <id_token>

### 2) Get token by REST login

Use demo script:

```powershell
d:/Project_A/Credit-Scoring/.venv/Scripts/python.exe demo_student_api.py \
  --base-url http://localhost:8000 \
  --mode firebase-login \
  --firebase-api-key <FIREBASE_WEB_API_KEY> \
  --email <USER_EMAIL> \
  --password <USER_PASSWORD>
```

This script calls Firebase Identity Toolkit signInWithPassword and then tests both student endpoints.

## Option B: Demo Bypass (local dev only)

Bypass works only when:

- ENVIRONMENT is not production
- DEMO_AUTH_BYPASS_ENABLED is true
- No Authorization bearer is provided

Add to credit-scoring-api/.env:

```env
ENVIRONMENT=development
DEMO_AUTH_BYPASS_ENABLED=true
DEMO_AUTH_BYPASS_USER_ID=demo-user
DEMO_AUTH_BYPASS_EMAIL=demo@example.com
```

Then run API and test:

```powershell
d:/Project_A/Credit-Scoring/.venv/Scripts/python.exe demo_student_api.py \
  --base-url http://localhost:8000 \
  --mode bypass
```

## Quick cURL tests

### Real token

```bash
curl -X POST http://localhost:8000/api/student/credit-score \
  -H "Authorization: Bearer <id_token>" \
  -H "Content-Type: application/json" \
  -d '{"gpa_latest":3.2,"academic_year":3,"major":"technology","program_level":"undergraduate","loan_amount":8000000,"living_status":"dormitory","has_buffer":true,"support_sources":["family"],"monthly_income":2000000,"monthly_expenses":3000000}'
```

### Demo bypass

```bash
curl -X POST http://localhost:8000/api/student/credit-score \
  -H "Content-Type: application/json" \
  -d '{"gpa_latest":3.2,"academic_year":3,"major":"technology","program_level":"undergraduate","loan_amount":8000000,"living_status":"dormitory","has_buffer":true,"support_sources":["family"],"monthly_income":2000000,"monthly_expenses":3000000}'
```

## Security note

Never enable DEMO_AUTH_BYPASS_ENABLED in production.
