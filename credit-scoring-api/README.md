# 🚀 Credit Scoring API

FastAPI-based REST API for credit scoring and loan approval predictions.

---

## 📋 Overview

This API provides endpoints for:
- **Loan Default Prediction**: Predict probability of customer default
- **Loan Amount Estimation**: Calculate maximum eligible loan amount
- **Risk Assessment**: Detailed risk factor analysis
- **Model Information**: Access model metadata and performance

---

## 🏗️ Architecture

```
FastAPI Application
    ├── Routes
    │   ├── /api/predict          (Main prediction)
    │   ├── /api/batch-predict    (Batch processing)
    │   ├── /api/health           (Health check)
    │   └── /api/model/info       (Model metadata)
    │
    ├── Services
    │   ├── PredictionService     (Core ML logic)
    │   ├── ModelLoader           (Model management)
    │   └── FeatureEngineering    (Data preprocessing)
    │
    └── Models
        ├── CustomerInput         (Request schema)
        ├── PredictionResult      (Response schema)
        └── LoanEstimation        (Loan details)
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Check status
docker ps

# View logs
docker logs -f credit-scoring-api

# Stop
docker-compose down
```

Access API: http://localhost:8000/api/docs

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload

# Or use Python directly
python -m app.main
```

---

## 📡 API Endpoints

### 1️⃣ Predict Loan

**POST** `/api/predict`

Predict loan default probability and estimate loan amount.

**Request Body:**
```json
{
  "customer_id": "CUST12345",
  "age_years": 35,
  "employment_years": 5,
  "annual_income": 50000,
  "requested_amount": 150000,
  "credit_card_usage": 42,
  "days_past_due_avg": 3,
  "higher_education": true,
  "employment_status": "working"
}
```

**Response:**
```json
{
  "customer_id": "CUST12345",
  "default_probability": 0.23,
  "threshold": 0.5,
  "risk_level": "LOW",
  "decision": "APPROVE",
  "confidence": 0.27,
  "loan_estimation": {
    "requested_amount": 150000,
    "approved_amount": 150000,
    "max_eligible_amount": 200000,
    "interest_rate": 6.5,
    "loan_term_months": 72,
    "monthly_payment": 2567.89,
    "recommendation": "APPROVE_FULL"
  },
  "risk_factors": [
    {
      "factor": "Stable employment",
      "impact": "positive",
      "value": "5 years"
    }
  ],
  "model_version": "LightGBM v1.0"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST12345",
    "age_years": 35,
    "employment_years": 5,
    "annual_income": 50000,
    "requested_amount": 150000,
    "credit_card_usage": 42,
    "days_past_due_avg": 3,
    "higher_education": true,
    "employment_status": "working"
  }'
```

---

### 2️⃣ Batch Predict

**POST** `/api/batch-predict`

Process multiple predictions at once.

**Request Body:**
```json
{
  "customers": [
    {
      "customer_id": "CUST001",
      "age_years": 30,
      // ... other fields
    },
    {
      "customer_id": "CUST002",
      "age_years": 45,
      // ... other fields
    }
  ]
}
```

---

### 3️⃣ Health Check

**GET** `/api/health`

Check API health and model status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-14T10:30:00",
  "models_loaded": true,
  "lgbm_features": 120,
  "threshold": 0.5
}
```

---

### 4️⃣ Model Information

**GET** `/api/model/info`

Get model metadata and performance metrics.

**Response:**
```json
{
  "model_name": "LightGBM",
  "version": "1.0",
  "features_count": 120,
  "threshold": 0.5,
  "performance": {
    "roc_auc": 0.72,
    "f1_score": 0.35,
    "precision": 0.45,
    "recall": 0.55
  }
}
```

---

### 5️⃣ Get Features

**GET** `/api/model/features`

List all model features.

---

## 💻 Frontend Integration

### JavaScript (Fetch API)

```javascript
async function predictLoan(customerData) {
  const response = await fetch('http://localhost:8000/api/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(customerData)
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return await response.json();
}

// Usage
const customer = {
  customer_id: "CUST12345",
  age_years: 35,
  employment_years: 5,
  annual_income: 50000,
  requested_amount: 150000,
  credit_card_usage: 42,
  days_past_due_avg: 3,
  higher_education: true,
  employment_status: "working"
};

try {
  const result = await predictLoan(customer);
  console.log(`Decision: ${result.decision}`);
  console.log(`Approved: $${result.loan_estimation.approved_amount}`);
  console.log(`Interest Rate: ${result.loan_estimation.interest_rate}%`);
} catch (error) {
  console.error('Prediction failed:', error);
}
```

### Python (Requests)

```python
import requests

url = "http://localhost:8000/api/predict"

customer_data = {
    "customer_id": "CUST12345",
    "age_years": 35,
    "employment_years": 5,
    "annual_income": 50000,
    "requested_amount": 150000,
    "credit_card_usage": 42,
    "days_past_due_avg": 3,
    "higher_education": True,
    "employment_status": "working"
}

response = requests.post(url, json=customer_data)
result = response.json()

print(f"Decision: {result['decision']}")
print(f"Probability: {result['default_probability']:.2%}")
print(f"Approved Amount: ${result['loan_estimation']['approved_amount']:,.2f}")
```

### React Example

```jsx
import { useState } from 'react';

function LoanPredictor() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const predictLoan = async (formData) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Form here */}
      {result && (
        <div>
          <h3>Decision: {result.decision}</h3>
          <p>Approved Amount: ${result.loan_estimation.approved_amount}</p>
          <p>Interest Rate: {result.loan_estimation.interest_rate}%</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🐳 Docker Configuration

### Dockerfile

Optimized multi-stage build for production.

### docker-compose.yml

Single-command deployment with health checks.

### Environment Variables

```bash
# .env file
ENVIRONMENT=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test file
pytest tests/test_prediction.py

# Verbose output
pytest -v
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

---

## 📊 Performance

- **Average Response Time**: < 100ms
- **Throughput**: 100+ requests/second
- **Model Load Time**: < 2 seconds
- **Memory Usage**: ~500MB

---

## 🔒 Security

### CORS Configuration

Update `app/core/config.py`:

```python
ALLOWED_ORIGINS = [
    "https://your-frontend.com",
    "https://www.your-frontend.com"
]
```

### API Key Authentication (Optional)

Add to `app/core/security.py` for production use.

---

## 🐛 Troubleshooting

### Model Loading Error

```bash
# Check if models exist
ls -la models/

# Verify model paths in config.py
```

### CORS Error

```bash
# Add frontend URL to ALLOWED_ORIGINS in config.py
```

### Docker Build Fails

```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

---

## 📈 Monitoring

### Logs

```bash
# Docker logs
docker logs credit-scoring-api -f

# Application logs
tail -f logs/app.log
```

### Health Check

```bash
# Check health endpoint
curl http://localhost:8000/api/health

# Docker health status
docker inspect credit-scoring-api | grep Health
```

---

## 🚀 Deployment

### Deploy to Heroku

```bash
heroku login
heroku container:login
heroku create your-app-name
heroku container:push web -a your-app-name
heroku container:release web -a your-app-name
heroku open
```

### Deploy to AWS EC2

```bash
# SSH to EC2 instance
ssh -i your-key.pem ec2-user@your-ip

# Install Docker
sudo yum install docker
sudo service docker start

# Pull and run
docker pull your-username/credit-scoring-api:latest
docker run -d -p 80:8000 your-username/credit-scoring-api:latest
```

---

## 📚 Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

---

## 🤝 Contributing

See main project [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## 📄 License

MIT License - See [LICENSE](../LICENSE)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Credit-Scoring/issues)
- **Email**: vanquoc11082004@gmail.com

---

**Last Updated**: November 2024