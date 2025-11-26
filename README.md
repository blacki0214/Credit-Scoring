# 🏦 Credit Scoring System - Smart Loan Approval Platform

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![LightGBM](https://img.shields.io/badge/LightGBM-Latest-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

> **A complete AI-powered loan approval system with customer-friendly API in Vietnamese Dong (VND)**

---

## 🎯 What This Project Does

This is a **complete loan approval system** that helps banks and financial institutions:

**Automatically approve or reject loans** based on customer information  
**Calculate credit scores** (300-850) from simple customer data  
**Determine loan amounts** customers can get in VND  
**Assess risk levels** (Low, Medium, High, Very High)  
**Provide instant decisions** - no manual review needed  

### 💡 Perfect For

- **Banks** wanting to automate loan decisions
- **Fintech Apps** needing credit scoring
- **Lending Platforms** in Vietnam (VND support)
- **Students** learning ML and API development

---

## ⚡ Quick Demo

**Customer applies for 100 million VND loan:**
```json
Input: {
  "full_name": "Nguyen Van A",
  "age": 30,
  "monthly_income": 15000000,  // 15 million VND/month
  "loan_amount": 100000000      // 100 million VND
}

Output: {
  "approved": true,
  "credit_score": 785,           // Auto-calculated!
  "monthly_payment_vnd": 3156754,
  "interest_rate": 8.5,
  "risk_level": "Low"
}
```

**That's it!** No complex data needed. System calculates everything automatically.

---

## 📂 Project Structure (Simple)

```
Credit-Scoring/
│
├── 🚀 credit-scoring-api/        ⭐ THE MAIN API (START HERE!)
│   ├── app/                      Production-ready FastAPI
│   ├── models/                   AI models (LightGBM)
│   ├── tests/                    All tests passing ✅
│   ├── docker-compose.yml        One command to run!
│   └── README.md                 API documentation
│
├── 📊 notebooks/                 How the AI was built
│   └── parquet_files/           Step-by-step analysis
│
├── 💾 data/                      Training data
│   ├── application_train.csv    Customer data
│   ├── bureau.csv               Credit history
│   └── ...                      More datasets
│
├── 📈 output/                    Saved models
│   └── models/
│       ├── lgb_model_optimized.pkl        The main AI
│       └── ensemble_comparison_metadata.pkl
│
└── 📚 docs/                      Guides
    └── API_GUIDE.md
```

### Where to Start?

1. **Want to use the API?** → Go to `credit-scoring-api/` folder
2. **Want to understand the AI?** → Check `notebooks/` folder  
3. **Want to see the data?** → Look in `data/` folder

---

## 🚀 Getting Started (3 Easy Steps)

### Step 1: Clone This Project

```bash
git clone https://github.com/blacki0214/Credit-Scoring.git
cd Credit-Scoring
```

### Step 2: Go to API Folder

```bash
cd credit-scoring-api
```

### Step 3: Run with Docker (Easiest!)

```bash
docker-compose up -d
```

**That's it!** Your API is now running at `http://localhost:8000`

### 🌐 Open API Documentation

Go to: **http://localhost:8000/api/docs**

You'll see a beautiful interactive interface where you can test everything!

---

## 📱 How to Use the API (4 Endpoints)

### 1️⃣ `/api/apply` - Customer Loan Application ⭐ **RECOMMENDED**

**Best for:** Customer-facing apps, mobile apps, websites

```javascript
// Customer fills simple form
POST http://localhost:8000/api/apply
{
  "full_name": "Nguyen Van A",
  "age": 30,
  "monthly_income": 15000000,        // VND
  "employment_status": "EMPLOYED",
  "years_employed": 5.0,
  "home_ownership": "RENT",
  "loan_amount": 100000000,          // VND
  "loan_purpose": "PERSONAL",
  "years_credit_history": 3,
  "has_previous_defaults": false,
  "currently_defaulting": false
}

// Instant response
{
  "approved": true,
  "credit_score": 785,                // Auto-calculated!
  "loan_amount_vnd": 100000000,
  "monthly_payment_vnd": 3156754,
  "interest_rate": 8.5,
  "loan_term_months": 36,
  "risk_level": "Low",
  "approval_message": "Loan approved!"
}
```

### 2️⃣ `/api/credit-score` - Credit Score Calculator ⭐ **FOR DASHBOARDS**

**Best for:** Customer dashboards, analytics, credit tracking

```javascript
POST http://localhost:8000/api/credit-score
// Same input as /api/apply

// Response shows HOW score was calculated
{
  "credit_score": 785,
  "loan_grade": "A",
  "risk_level": "Low",
  "score_breakdown": {
    "base_score": 650,
    "age_adjustment": +30,
    "income_adjustment": +30,
    "employment_adjustment": +30,
    "home_ownership_adjustment": +5,
    "credit_history_adjustment": +20,
    "employment_status_adjustment": +20,
    "defaults_adjustment": 0,
    "debt_to_income_adjustment": 0,
    "final_score": 785
  }
}
```

### 3️⃣ `/api/health` - Check if API is Running

```javascript
GET http://localhost:8000/api/health
// Response
{
  "status": "healthy",
  "models_loaded": true
}
```

### 4️⃣ `/api/model/info` - AI Model Information

```javascript
GET http://localhost:8000/api/model/info
// Get details about the AI
```

---

## Integration Examples

### React/Next.js Example

```javascript
async function applyForLoan() {
  const response = await fetch('http://localhost:8000/api/apply', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      full_name: 'Nguyen Van A',
      age: 30,
      monthly_income: 15000000,
      employment_status: 'EMPLOYED',
      years_employed: 5.0,
      home_ownership: 'RENT',
      loan_amount: 100000000,
      loan_purpose: 'PERSONAL',
      years_credit_history: 3,
      has_previous_defaults: false,
      currently_defaulting: false
    })
  });
  
  const result = await response.json();
  
  if (result.approved) {
    alert(`Approved! Credit Score: ${result.credit_score}`);
  } else {
    alert('Sorry, loan not approved');
  }
}
```

### Python Example

```python
import requests

response = requests.post(
    'http://localhost:8000/api/apply',
    json={
        'full_name': 'Nguyen Van A',
        'age': 30,
        'monthly_income': 15000000,
        'employment_status': 'EMPLOYED',
        'years_employed': 5.0,
        'home_ownership': 'RENT',
        'loan_amount': 100000000,
        'loan_purpose': 'PERSONAL',
        'years_credit_history': 3,
        'has_previous_defaults': False,
        'currently_defaulting': False
    }
)

result = response.json()
print(f"Approved: {result['approved']}")
print(f"Credit Score: {result['credit_score']}")
```

---

## The AI Behind It

### What Model We Use

**LightGBM** - A fast, accurate machine learning algorithm

- Trained on **300,000+ real loan applications**
- **64 smart features** engineered from simple inputs
- **72%+ accuracy** in predicting loan defaults

### How It Works

```
Customer Data (11 simple fields)
        ↓
Feature Engineering (Auto-creates 64 features)
        ↓
LightGBM AI Model (Predicts risk)
        ↓
Credit Score Calculation (300-850)
        ↓
Loan Decision (Approve/Reject + Amount)
```

### Accuracy Stats

| Metric | Value | What It Means |
|--------|-------|---------------|
| **ROC-AUC** | 72% | How well we separate good/bad loans |
| **Precision** | 45% | Of rejections, 45% would default |
| **Recall** | 55% | We catch 55% of bad loans |
| **Response Time** | <100ms | Super fast! |

---

## Understanding the Data

### Input: Simple Customer Information

Only **11 easy fields** needed:

1. **Full Name** - Customer name
2. **Age** - 18 to 100
3. **Monthly Income** - In VND
4. **Employment Status** - EMPLOYED, SELF_EMPLOYED, UNEMPLOYED
5. **Years Employed** - How long at current job
6. **Home Ownership** - RENT, OWN, MORTGAGE, LIVING_WITH_PARENTS
7. **Loan Amount** - Requested amount in VND
8. **Loan Purpose** - What they need money for
9. **Years Credit History** - How long they've had credit
10. **Has Previous Defaults** - Yes/No
11. **Currently Defaulting** - Yes/No

### Output: Complete Loan Decision

The API returns **everything you need**:

- **Approved or Rejected** - Clear decision
- **Credit Score** - 300-850 (auto-calculated)
- **Loan Amount in VND** - How much they can borrow
- **Monthly Payment** - Exact payment in VND
- **Interest Rate** - Based on credit score
- **Risk Level** - Low/Medium/High/Very High
- **Approval Message** - Human-readable explanation

---

## 🎓 How Credit Score is Calculated

The system automatically calculates credit score (300-850) based on:

| Factor | Impact | Max Points |
|--------|--------|------------|
| **Base Score** | Everyone starts here | 650 |
| **Age** | Older = more stable | +50 |
| **Income** | Higher = better | +50 |
| **Employment** | Longer = more stable | +40 |
| **Home Ownership** | Own > Mortgage > Rent | +30 |
| **Credit History** | Longer = better | +40 |
| **Employment Status** | Employed > Self-employed | +20 |
| **Previous Defaults** | Major penalty | -80 to -150 |
| **Debt-to-Income** | Lower is better | -0 to -50 |

**Example Calculation:**
```
Base: 650
Age 30: +30
Income 15M VND: +30
Employed 5 years: +30
Renting: +5
Credit history 3 years: +20
Employed: +20
No defaults: 0
Good DTI: 0
───────────
Total: 785 ⭐
```

---

## 🐳 Docker Commands (Easy!)

### Start the API
```bash
cd credit-scoring-api
docker-compose up -d
```

### Check if it's running
```bash
docker ps
```

### View logs
```bash
docker logs credit-scoring-api
```

### Stop the API
```bash
docker-compose down
```

### Rebuild after changes
```bash
docker-compose up --build -d
```

---

## 🧪 Testing

All tests are passing! ✅

```bash
cd credit-scoring-api
pytest tests/
```

**Test Results:** 10/10 passing
- Health check ✅
- Model info ✅  
- Predictions ✅
- Loan offers ✅
- Credit score ✅
- Customer applications ✅

---

## 📚 Complete Documentation

| Document | Purpose | Link |
|----------|---------|------|
| **Customer API Guide** | How to use `/api/apply` | [CUSTOMER_API_GUIDE.md](credit-scoring-api/CUSTOMER_API_GUIDE.md) |
| **Dashboard Guide** | Build dashboards with `/api/credit-score` | [DASHBOARD_GUIDE.md](credit-scoring-api/DASHBOARD_GUIDE.md) |
| **API Documentation** | All endpoints explained | [README.md](credit-scoring-api/README.md) |
| **API Docs (Interactive)** | Test API in browser | http://localhost:8000/api/docs |

---

## 💡 Common Use Cases

### 1. Mobile Banking App
```javascript
// Customer applies for loan in app
const result = await applyForLoan(customerData);
if (result.approved) {
  showApprovalScreen(result.loan_amount_vnd, result.monthly_payment_vnd);
}
```

### 2. Customer Dashboard
```javascript
// Show credit score on dashboard
const scoreData = await getCreditScore(customerData);
displayCreditScore(scoreData.credit_score, scoreData.score_breakdown);
```

### 3. Admin Panel
```javascript
// Process multiple applications
const results = await batchProcessLoans(applications);
showApprovalStats(results);
```

---

## 🛠️ Tech Stack (Simple Explanation)

### What We Use:

- **Python 3.10** - Programming language
- **FastAPI** - Builds the web API (super fast!)
- **LightGBM** - The AI brain (machine learning)
- **Docker** - Packages everything to run anywhere
- **Pydantic** - Makes sure data is correct
- **Pytest** - Tests everything automatically

### Why These?

- **Fast** - API responds in <100ms
- **Reliable** - All tests passing
- **Easy** - One command to start (`docker-compose up`)
- **Smart** - AI trained on 300,000+ loans

---

## Roadmap

### Completed
- [x] AI model training (LightGBM)
- [x] Feature engineering (13 → 64 features)
- [x] REST API with FastAPI
- [x] Customer-friendly endpoints
- [x] Credit score calculator
- [x] Docker deployment
- [x] VND currency support
- [x] All tests passing (10/10)
- [x] Complete documentation

### Coming Soon
- [ ] React dashboard example
- [ ] Mobile app integration guide
- [ ] Real-time monitoring
- [ ] A/B testing
- [ ] Auto-model retraining
- [ ] Multi-language support

---

## 📄 License

MIT License - Free to use, modify, and distribute!

---

## 👨‍💻 Author

**Nguyen Van Quoc**

- 📧 Email: vanquoc11082004@gmail.com
- 🐙 GitHub: [@blacki0214](https://github.com/blacki0214)
- 💼 LinkedIn: [Nguyen Van Quoc](https://www.linkedin.com/in/quoc-nguyen-van-7898ba255/)

---

## 🙏 Acknowledgments

- **Dataset**: Home Credit Default Risk (Kaggle)
- **Inspiration**: Real-world banking systems
- **Tools**: Amazing open-source community

---

## ⚠️ Important Disclaimer

**This is an educational/demo project.**

For production use in real financial services:
- Add user authentication
- Implement rate limiting
- Add encryption (HTTPS)
- Comply with regulations (FCRA, GDPR, etc.)
- Get legal and financial expert review
- Add fraud detection
- Implement audit logs

---

## 🚀 Ready to Start?

```bash
# 1. Clone
git clone https://github.com/blacki0214/Credit-Scoring.git

# 2. Go to API
cd Credit-Scoring/credit-scoring-api

# 3. Run
docker-compose up -d

# 4. Open browser
# http://localhost:8000/api/docs

# 5. Start building! 🎉
```

---

**Last Updated**: November 26, 2025  
**Status**: Production Ready ✅