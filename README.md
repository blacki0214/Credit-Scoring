<div align="center">

# 🏦 Credit Scoring API

**AI-Powered Loan Approval System**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange?style=for-the-badge)](https://lightgbm.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

[📚 Live API Docs](https://credit-scoring-api-wrkfygkl6a-as.a.run.app/docs) • [🚀 Quick Start](#-quick-start) • [📖 Integration Guide](#-integration-guide)

</div>

---

## ✨ Features

- 🤖 **AI-Powered** - XGBoost model trained on 300K+ real loan applications
- ⚡ **Fast** - Sub-100ms response time
- 🎯 **Accurate** - 72% ROC-AUC score
- 🔒 **Secure** - API key authentication, rate limiting & CORS protection
- 📱 **Mobile-Ready** - Two-step flow optimized for mobile apps
- 🌍 **Production-Ready** - Docker support, health checks, monitoring

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and run
git clone <repo-url>
cd credit-scoring-api
docker-compose up -d

# Check status
docker-compose logs -f
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000
```

**🌐 Open:** https://credit-scoring-api-wrkfygkl6a-as.a.run.app/docs

---

## 📡 API Endpoints

### 🎯 Two-Step Flow (Recommended)

> 📱 **Perfect for mobile apps** - Separate credit assessment from loan terms calculation

<table>
<tr>
<td width="50%" valign="top">

### 1 Calculate Credit Score & Loan Limit

🎯 **Endpoint:** `POST /api/calculate-limit`  
✨ **No loan purpose needed!**

**📋 Input Fields:**
- 👤 `full_name` - Name
- 🎂 `age` - Age (18-100)
- 💰 `monthly_income` - Income (VND)
- 💼 `employment_status` - Job status
- ⏱️ `years_employed` - Work years
- 🏠 `home_ownership` - Housing
- 📜 `years_credit_history` - Credit years
- ⚠️ `has_previous_defaults` - Past defaults?
- 🚫 `currently_defaulting` - Current defaults?

**📊 Output:**
- 💳 `credit_score` - Score (300-850)
- 💵 `loan_limit_vnd` - Max loan
- 🎯 `risk_level` - Risk level
- ✅ `approved` - Approved?

</td>
<td width="50%" valign="top">

### 2️Calculate Loan Terms

🎯 **Endpoint:** `POST /api/calculate-terms`  
🎨 **After user selects purpose**

**📋 Input Fields:**
- 💵 `loan_amount` - Desired amount
- 🎯 `loan_purpose` - Purpose  
  🏠 HOME | 🚗 CAR | 💼 BUSINESS  
  🎓 EDUCATION | 💳 PERSONAL
- 💳 `credit_score` - From Step 1

**📊 Output:**
- 📈 `interest_rate` - APR %
- ⏰ `loan_term_months` - Duration
- 💰 `monthly_payment_vnd` - Monthly
- 💸 `total_payment_vnd` - Total cost
- 🧮 `total_interest_vnd` - Interest
- 📝 `rate_explanation` - Why this rate
- 📅 `term_explanation` - Why this term

</td>
</tr>
</table>

---

**📥 Example Request (Step 1):**

```json
{
  "full_name": "Nguyen Van A",
  "age": 30,
  "monthly_income": 20000000,
  "employment_status": "EMPLOYED",
  "years_employed": 5.0,
  "home_ownership": "MORTGAGE",
  "years_credit_history": 3,
  "has_previous_defaults": false,
  "currently_defaulting": false
}
```

**📤 Example Response (Step 1):**
```json
{
  "full_name": "Nguyen Van A",
  "age": 30,
  "monthly_income": 20000000,
  "employment_status": "EMPLOYED",
  "years_employed": 5.0,
  "home_ownership": "MORTGAGE",
  "years_credit_history": 3,
  "has_previous_defaults": false,
  "currently_defaulting": false
}
```

```json
{
  "credit_score": 750,
  "loan_limit_vnd": 420000000,
  "risk_level": "Low",
  "approved": true
}
```

---

**📥 Example Request (Step 2):**
```json
{
  "loan_amount": 300000000,
  "loan_purpose": "CAR",
  "credit_score": 750
}
```

**📤 Example Response (Step 2):**
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

### 🛠️ Utility Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/health` | GET | ❌ No | 🏥 Health check |
| `/api/model/info` | GET | ❌ No | 📊 ML model details |
| `/api/model/features` | GET | ❌ No | 📋 Feature list (64 features) |
| `/api/credit-score` | POST | ✅ Yes | 💯 Calculate credit score only |

---

## 🔒 API Security

### Authentication

All prediction and calculation endpoints require **API Key authentication**.

**Protected Endpoints:**
- `/api/calculate-limit` - Requires API key
- `/api/calculate-terms` - Requires API key
- `/api/apply` - Requires API key
- `/api/credit-score` - Requires API key
- `/api/batch-predict` - Requires API key

**Public Endpoints:**
- `/api/health` - No authentication needed
- `/api/model/info` - No authentication needed
- `/api/model/features` - No authentication needed

### How to Use API Key

**Python:**
```python
import requests

headers = {
    "X-API-Key": "your-api-key-here",
    "Content-Type": "application/json"
}

response = requests.post(
    "https://credit-scoring-api-wrkfygkl6a-as.a.run.app/caculate-limit",
    headers=headers,
    json={...}
)
```

**JavaScript:**
```javascript
const response = await fetch('https://credit-scoring-api-wrkfygkl6a-as.a.run.app/caculate-limit', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your-api-key-here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({...})
});
```

**cURL:**
```bash
curl -X POST "https://credit-scoring-api-wrkfygkl6a-as.a.run.app/caculate-limit" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Rate Limiting

To prevent abuse, the API implements rate limiting:

| Endpoint | Rate Limit |
|----------|------------|
| `/api/calculate-limit` | 60 requests/minute |
| `/api/calculate-terms` | 60 requests/minute |
| `/api/apply` | 30 requests/minute |
| `/api/batch-predict` | 10 requests/minute |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1234567890
```

### CORS (Cross-Origin Resource Sharing)

The API supports CORS for web applications:
- **Allowed Origins:** Configurable (contact admin to whitelist your domain)
- **Allowed Methods:** GET, POST, PUT, DELETE, OPTIONS
- **Allowed Headers:** All standard headers
- **Credentials:** Supported

### Error Responses

**401 Unauthorized** - Missing or invalid API key:
```json
{
  "detail": "Invalid API key"
}
```

**429 Too Many Requests** - Rate limit exceeded:
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## 🧮 How It Works

### 💳 Credit Score Calculation (300-850)

**Formula:** `Base Score (650) + Adjustments`

| Factor | 🟢 Good | 📈 Points |
|--------|---------|-----------|
| 👤 Age | 25-60 years | +30 |
| 💰 Income | >15M VND/month | +40 |
| 💼 Employment | 5+ years | +35 |
| 🏠 Home Ownership | Own/Mortgage | +20 |
| 📜 Credit History | 3+ years | +20 |
| ✅ No Defaults | Clean record | +20 |

**Example:**
```
Age 30 + Income 20M + 5 years employed + Mortgage + 3 years history + No defaults
= 650 + 30 + 40 + 35 + 20 + 20 + 0 = 795 points ⭐
```

---

### 💵 Loan Limit Calculation

**Formula:** `Annual Income × Credit Score Multiplier × Risk Adjustment`

#### Credit Score Multipliers

| Credit Score | Rating | Multiplier |
|--------------|--------|------------|
| 780+ | ⭐⭐⭐⭐⭐ Excellent | 5.0x |
| 740-779 | ⭐⭐⭐⭐ Very Good | 4.0x |
| 700-739 | ⭐⭐⭐ Good | 3.0x |
| 650-699 | ⭐⭐ Fair | 2.5x |
| 600-649 | ⭐ Poor | 2.0x |
| <600 | ❌ Very Poor | 1.5x |

#### Risk Adjustments

| Risk Level | Adjustment |
|------------|------------|
| 🟢 Low | No adjustment |
| 🟡 Medium | No adjustment |
| 🟠 High | -30% |
| 🔴 Very High | -50% |

**Example:**
```
Income: 20M/month × 12 = 240M/year
Credit Score: 750 → 4.0x multiplier (Very Good)
Risk Level: Low → No adjustment
Loan Limit: 240M × 4.0 = 960M VND 💰
```

---

### 📊 Interest Rates

**Formula:** `Base Rate (by Purpose) + Credit Score Adjustment`

#### Base Rates by Loan Purpose

| Purpose | 🏷️ Base Rate | ⏱️ Term | 💵 Monthly Payment<br/>(300M VND) |
|---------|--------------|---------|-----------------------------------|
| 🏠 HOME | 6.5% | 20 years | 2.2M VND |
| 🚗 CAR | 7.5% | 5 years | 6.0M VND |
| 💼 BUSINESS | 9.0% | 7 years | 4.7M VND |
| 🎓 EDUCATION | 8.0% | 5 years | 6.1M VND |
| 💳 PERSONAL | 11.0% | 3 years | 9.8M VND |

#### Credit Score Adjustments

| Credit Score | Rate Adjustment |
|--------------|-----------------|
| 780+ | -2.0% 🎉 |
| 740-779 | -1.0% ✨ |
| 700-739 | 0% (Standard) |
| 650-699 | +1.5% |
| 600-649 | +3.0% |
| <600 | +5.0% ⚠️ |

**Example:**
```
CAR loan (base 7.5%) + Credit score 750 (-1.0%) = 6.5% final rate 🎯
```

---

## 📖 Integration Guide

### 🐍 Python Example

```python
import requests

API_URL = "https://credit-scoring-api-wrkfygkl6a-as.a.run.app/docs"
API_KEY = "your-api-key-here"  # Get from admin

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Step 1: Get credit score and loan limit
response = requests.post(f"{API_URL}/api/calculate-limit", headers=headers, json={
    "full_name": "Nguyen Van A",
    "age": 30,
    "monthly_income": 20000000,
    "employment_status": "EMPLOYED",
    "years_employed": 5.0,
    "home_ownership": "MORTGAGE",
    "years_credit_history": 3,
    "has_previous_defaults": False,
    "currently_defaulting": False
})

limit_data = response.json()
print(f"Credit Score: {limit_data['credit_score']}")
print(f"Max Loan: {limit_data['loan_limit_vnd']:,} VND")

# Step 2: Get loan terms (after user selects purpose)
response = requests.post(f"{API_URL}/api/calculate-terms", headers=headers, json={
    "loan_amount": 300000000,
    "loan_purpose": "CAR",
    "credit_score": limit_data['credit_score']
})

terms = response.json()
print(f"Interest Rate: {terms['interest_rate']}%")
print(f"Monthly Payment: {terms['monthly_payment_vnd']:,} VND")
print(f"Total Payment: {terms['total_payment_vnd']:,} VND")
```

---

### 🟨 JavaScript/TypeScript Example

```javascript
const API_URL = 'https://credit-scoring-api-wrkfygkl6a-as.a.run.app/docs';
const API_KEY = 'your-api-key-here';  // Get from admin

// Step 1: Get credit score and loan limit
const limitResponse = await fetch(`${API_URL}/api/calculate-limit`, {
  method: 'POST',
  headers: { 
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json' 
  },
  body: JSON.stringify({
    full_name: "Nguyen Van A",
    age: 30,
    monthly_income: 20000000,
    employment_status: "EMPLOYED",
    years_employed: 5.0,
    home_ownership: "MORTGAGE",
    years_credit_history: 3,
    has_previous_defaults: false,
    currently_defaulting: false
  })
});

const limitData = await limitResponse.json();
console.log(`Credit Score: ${limitData.credit_score}`);
console.log(`Max Loan: ${limitData.loan_limit_vnd.toLocaleString()} VND`);

// Step 2: Get loan terms (after user selects purpose)
const termsResponse = await fetch(`${API_URL}/api/calculate-terms`, {
  method: 'POST',
  headers: { 
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json' 
  },
  body: JSON.stringify({
    loan_amount: 300000000,
    loan_purpose: "CAR",
    credit_score: limitData.credit_score
  })
});

const terms = await termsResponse.json();
console.log(`Interest Rate: ${terms.interest_rate}%`);
console.log(`Monthly Payment: ${terms.monthly_payment_vnd.toLocaleString()} VND`);
```

---

## 🚢 Deployment

### 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

---

### ☁️ Cloud Deployment

#### Render / Railway / Heroku

**1. Environment Variables:**
```env
API_VERSION=2.0.0
MODEL_PATH=models/xgboost_final.pkl
USE_XGBOOST=true
```

**2. Deploy:**
- **Render:** Connect GitHub repo → Auto-deploy
- **Railway:** `railway up`
- **Heroku:** `git push heroku main`

**3. Health Check:** `/api/health`

---

## 🧪 Testing

### Interactive API Documentation

- 🏠 **Local:** http://localhost:8000/docs
- 🌐 **Live:** https://credit-scoring-api-wrkfygkl6a-as.a.run.app/docs

### Test Cases

| Scenario | 💳 Credit Score | 💰 Income | 🎯 Expected Limit |
|----------|-----------------|-----------|-------------------|
| ⭐⭐⭐⭐⭐ Excellent | 800 | 30M/month | 1.8B VND |
| ⭐⭐⭐⭐ Very Good | 750 | 20M/month | 960M VND |
| ⭐⭐⭐ Good | 720 | 20M/month | 720M VND |
| ⭐⭐ Fair | 670 | 15M/month | 450M VND |
| ⭐ Poor | 620 | 10M/month | 240M VND |

### Run Tests

```bash
python test_api.py
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| 🌐 Framework | FastAPI (Python 3.10+) |
| 🤖 ML Model | **XGBoost v2.0** |
| 📊 Accuracy | 72% ROC-AUC |
| 📚 Training Data | 300,000+ loan applications |
| 🔧 Features | 64 auto-engineered features |
| ⚡ Response Time | <100ms average |
| 🐳 Containerization | Docker + Docker Compose |
| 🔒 Security | API Key + Rate Limiting + CORS |

---

## 📁 Project Structure

```
credit-scoring-api/
├── 📂 app/
│   ├── 📂 api/
│   │   └── 📂 routes/          # API endpoints
│   │       ├── prediction.py   # Main endpoints
│   │       ├── health.py       # Health checks
│   │       └── model_info.py   # Model info
│   ├── 📂 services/            # Business logic
│   │   ├── loan_limit_calculator.py
│   │   ├── loan_terms_calculator.py
│   │   ├── smart_loan_offer.py
│   │   ├── prediction_service.py
│   │   └── feature_engineering.py
│   ├── 📂 models/
│   │   └── schemas.py          # Request/Response models
│   ├── 📂 core/
│   │   ├── config.py           # Configuration
│   │   └── security.py         # Authentication
│   └── 📄 main.py              # FastAPI app
├── 📂 models/                  # ML models
│   ├── lgb_model_optimized.pkl (Backup)
│   └── xgboost_final.pkl       (Active - v2.0)
├── 📂 tests/                   # Test files
├── 🐳 Dockerfile
├── 🐳 docker-compose.yml
└── 📖 README.md
```

---

## 🔄 API Changes (v2.0)

### ✅ What's New

- ✨ `/api/calculate-limit` - Two-step flow (Step 1) - **No loan purpose needed!**
- ✨ `/api/calculate-terms` - Two-step flow (Step 2)
- 💳 Credit score-based loan limits (replaced tier system)
- 🎯 Purpose-based interest rates
- 🔒 API key authentication
- ⚡ Rate limiting

### ❌ What's Removed

- `loan_tier` field (PLATINUM/GOLD/SILVER/BRONZE)
- `tier_reason` field
- Tier-based multipliers

### 🔄 Migration Guide

The old `/api/apply` endpoint still works but no longer returns `loan_tier` and `tier_reason` fields. Update your code to:

1. Remove references to `loan_tier` and `tier_reason`
2. Use the new two-step flow for better UX
3. `loan_purpose` is now **optional** in Step 1

---

## 🐛 Troubleshooting

### API Not Starting?

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
uvicorn app.main:app --port 8001
```

### Model Not Loading?

```bash
# Check model file exists
ls models/xgboost_final.pkl

# Check file size (should be ~1MB for XGBoost)
```

### Slow Response?

- ⏱️ First request is slower (model loading)
- ⚡ Subsequent requests: <100ms
- 💻 Check server resources (CPU/RAM)

---

## 📄 License

MIT License - Free to use for commercial and personal projects

---

## 💬 Support

- 📚 **API Documentation:** https://credit-scoring-api-wrkfygkl6a-as.a.run.app/docs
- 🐛 **Issues:** Create a GitHub issue
- ❓ **Questions:** Check API docs first
- 🔑 **API Key:** Contact admin for access

---

<div align="center">

**Built with ❤️ using FastAPI + XGBoost v2.0**

🇻🇳 Made in Vietnam

[Back to Top](#-credit-scoring-api)

</div>