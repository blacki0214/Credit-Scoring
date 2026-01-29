# Credit Scoring API

> **AI-powered loan approval system - Simple, Fast, Accurate**

**Live Demo:** https://credit-scoring-h7mv.onrender.com/docs

---

## Quick Start

```bash
# Option 1: Docker (Recommended)
docker-compose up -d

# Option 2: Local
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Open:** http://localhost:8000/docs

---

## API Endpoints

### 1. Two-Step Flow (Recommended for Mobile Apps)

#### Step 1: Calculate Loan Limit

**Endpoint:** `POST /api/calculate-limit`

**Purpose:** Get credit score and maximum loan amount after user fills personal info

**Request:**
```json
{
  "full_name": "Nguyen Van A",
  "age": 30,
  "monthly_income": 20000000,
  "employment_status": "EMPLOYED",
  "years_employed": 5.0,
  "home_ownership": "RENT",
  "loan_purpose": "CAR",
  "years_credit_history": 3,
  "has_previous_defaults": false,
  "currently_defaulting": false
}
```

**Response:**
```json
{
  "credit_score": 750,
  "loan_limit_vnd": 420000000,
  "risk_level": "Low",
  "approved": true,
  "message": "Credit score: 750. Maximum loan: 420M VND"
}
```

---

#### Step 2: Calculate Loan Terms

**Endpoint:** `POST /api/calculate-terms`

**Purpose:** Get interest rate and payment details after user selects purpose

**Request:**
```json
{
  "loan_amount": 300000000,
  "loan_purpose": "CAR",
  "credit_score": 750
}
```

**Response:**
```json
{
  "interest_rate": 6.5,
  "loan_term_months": 60,
  "monthly_payment_vnd": 5869844,
  "total_payment_vnd": 352190668,
  "total_interest_vnd": 52190668
}
```

---

### 2. One-Step Flow (Legacy)

**Endpoint:** `POST /api/apply`

**Purpose:** Complete loan application in one call

**Request:** Same as Step 1 + `loan_amount` field

**Response:** Combined result with approval decision + loan terms

---

### 3. Utility Endpoints

- **`GET /api/health`** - Check API status
- **`GET /api/model/info`** - Get AI model details
- **`POST /api/credit-score`** - Calculate credit score only (for dashboards)

---

## How It Works

### Credit Score (300-850)

**Formula:** Base (650) + Adjustments

| Factor | Good | Points |
|--------|------|--------|
| Age | 25-60 | +30 |
| Income | >15M/month | +40 |
| Employment | 5+ years | +35 |
| Home | Own/Mortgage | +20 |
| Credit History | 3+ years | +20 |
| Defaults | None | +20 |

**Example:** Age 30 + Income 20M + 5 years employed + Rent + 3 years history + No defaults = **750 points**

---

### Loan Limit

**Formula:** `Annual Income × Credit Score Multiplier × Risk Adjustment`

**Credit Score Multipliers:**
- 780+: **5.0x** (Excellent)
- 740-779: **4.0x** (Very Good)
- 700-739: **3.0x** (Good)
- 650-699: **2.5x** (Fair)
- 600-649: **2.0x** (Poor)
- <600: **1.5x** (Very Poor)

**Risk Adjustments:**
- High Risk: **-30%**
- Very High Risk: **-50%**

**Example:** 
- Income: 20M/month × 12 = 240M/year
- Credit Score: 750 → 4.0x multiplier
- Loan Limit: 240M × 4.0 = **960M VND**

---

### Interest Rates

**Formula:** `Base Rate (by Purpose) + Credit Score Adjustment`

**Base Rates:**

| Purpose | Rate | Term | Example Monthly Payment (300M VND) |
|---------|------|------|-----------------------------------|
| HOME | 6.5% | 20 years | 2.2M VND |
| CAR | 7.5% | 5 years | 6.0M VND |
| BUSINESS | 9.0% | 7 years | 4.7M VND |
| EDUCATION | 8.0% | 5 years | 6.1M VND |
| PERSONAL | 11.0% | 3 years | 9.8M VND |

**Credit Score Adjustments:**
- 780+: **-2.0%** (Best rate)
- 740-779: **-1.0%**
- 700-739: **0%** (Standard)
- 650-699: **+1.5%**
- 600-649: **+3.0%**
- <600: **+5.0%** (Highest rate)

**Example:** CAR loan with 750 credit score = 7.5% - 1.0% = **6.5% final rate**

---

## Integration Guide

### Python Example

```python
import requests

API_URL = "http://localhost:8000"

# Step 1: Get loan limit
response = requests.post(f"{API_URL}/api/calculate-limit", json={
    "full_name": "Nguyen Van A",
    "age": 30,
    "monthly_income": 20000000,
    "employment_status": "EMPLOYED",
    "years_employed": 5.0,
    "home_ownership": "RENT",
    "loan_purpose": "CAR",
    "years_credit_history": 3,
    "has_previous_defaults": False,
    "currently_defaulting": False
})

limit_data = response.json()
print(f"Credit Score: {limit_data['credit_score']}")
print(f"Max Loan: {limit_data['loan_limit_vnd']:,} VND")

# Step 2: Get loan terms
response = requests.post(f"{API_URL}/api/calculate-terms", json={
    "loan_amount": 300000000,
    "loan_purpose": "CAR",
    "credit_score": limit_data['credit_score']
})

terms = response.json()
print(f"Interest: {terms['interest_rate']}%")
print(f"Monthly: {terms['monthly_payment_vnd']:,} VND")
print(f"Total: {terms['total_payment_vnd']:,} VND")
```

### JavaScript Example

```javascript
const API_URL = 'http://localhost:8000';

// Step 1: Get loan limit
const limitResponse = await fetch(`${API_URL}/api/calculate-limit`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    full_name: "Nguyen Van A",
    age: 30,
    monthly_income: 20000000,
    employment_status: "EMPLOYED",
    years_employed: 5.0,
    home_ownership: "RENT",
    loan_purpose: "CAR",
    years_credit_history: 3,
    has_previous_defaults: false,
    currently_defaulting: false
  })
});

const limitData = await limitResponse.json();
console.log(`Credit Score: ${limitData.credit_score}`);
console.log(`Max Loan: ${limitData.loan_limit_vnd.toLocaleString()} VND`);

// Step 2: Get loan terms
const termsResponse = await fetch(`${API_URL}/api/calculate-terms`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    loan_amount: 300000000,
    loan_purpose: "CAR",
    credit_score: limitData.credit_score
  })
});

const terms = await termsResponse.json();
console.log(`Interest: ${terms.interest_rate}%`);
console.log(`Monthly: ${terms.monthly_payment_vnd.toLocaleString()} VND`);
```

---

## Deployment

### Docker Deployment

**1. Build and run:**
```bash
docker-compose up -d
```

**2. Check logs:**
```bash
docker-compose logs -f
```

**3. Stop:**
```bash
docker-compose down
```

---

### Cloud Deployment (Render/Railway/Heroku)

**1. Create `Dockerfile`** (already included)

**2. Set environment variables:**
```
API_VERSION=2.0.0
MODEL_PATH=models/lgb_model_optimized.pkl
```

**3. Deploy:**
- **Render:** Connect GitHub repo → Auto-deploy
- **Railway:** `railway up`
- **Heroku:** `git push heroku main`

**4. Health check endpoint:** `/api/health`

---

### Local Development

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Run server:**
```bash
uvicorn app.main:app --reload --port 8000
```

**3. Run tests:**
```bash
python test_api.py
```

---

## Tech Stack

- **Framework:** FastAPI (Python 3.10+)
- **ML Model:** LightGBM
- **Accuracy:** 72% ROC-AUC
- **Training Data:** 300,000+ real loan applications
- **Features:** 64 auto-engineered features
- **Response Time:** <100ms average

---

## API Changes (v2.0)

### What's New
- `/api/calculate-limit` - New 2-step flow (Step 1)
- `/api/calculate-terms` - New 2-step flow (Step 2)
- Credit score-based loan limits (replaced tier system)
- Purpose-based interest rates

### What's Removed
- `loan_tier` field (PLATINUM/GOLD/SILVER/BRONZE)
- `tier_reason` field
- Tier-based multipliers

### Migration
Old `/api/apply` endpoint still works, just without tier fields. Update your code to remove references to `loan_tier` and `tier_reason`.

---

## Testing

**Interactive API Docs:**
- Local: http://localhost:8000/docs
- Live: https://credit-scoring-h7mv.onrender.com/docs

**Test Script:**
```bash
python test_api.py
```

**Sample Test Cases:**

| Scenario | Credit Score | Income | Expected Limit |
|----------|--------------|--------|----------------|
| Excellent | 800 | 30M/month | 1.8B VND |
| Good | 720 | 20M/month | 720M VND |
| Fair | 670 | 15M/month | 450M VND |
| Poor | 620 | 10M/month | 240M VND |

---

## Troubleshooting

**API not starting?**
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
uvicorn app.main:app --port 8001
```

**Model not loading?**
```bash
# Check model file exists
ls models/lgb_model_optimized.pkl

# Check file size (should be ~14KB)
```

**Slow response?**
- First request is slower (model loading)
- Subsequent requests: <100ms
- Check server resources (CPU/RAM)

---

## Project Structure

```
credit-scoring-api/
├── app/
│   ├── api/routes/          # API endpoints
│   ├── services/            # Business logic
│   │   ├── loan_limit_calculator.py
│   │   ├── loan_terms_calculator.py
│   │   └── smart_loan_offer.py
│   ├── models/schemas.py    # Request/Response models
│   └── main.py             # FastAPI app
├── models/                  # ML models
├── tests/                   # Test files
├── Dockerfile
├── docker-compose.yml
└── README.md               # This file
```

---

## License

MIT License - Free to use for commercial and personal projects

---

## Support

- **API Docs:** http://localhost:8000/docs
- **Issues:** Create GitHub issue
- **Questions:** Check API docs first

---

**Built with FastAPI + LightGBM | Made in Vietnam**
