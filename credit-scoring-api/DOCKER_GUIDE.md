# Credit Scoring API - Quick Start Guide

## Running with Docker

### Prerequisites
- Docker and Docker Compose installed
- Model files in `models/` directory:
  - `lgb_model_optimized.pkl`
  - `ensemble_comparison_metadata.pkl`

### Start the API

```bash
# Build and start the container
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: https://credit-scoring-h7mv.onrender.com/docs
- **ReDoc**: https://credit-scoring-h7mv.onrender.com/redoc

## API Endpoints

### Health Check
```bash
GET https://credit-scoring-h7mv.onrender.com/docs#/Health/health_check_api_health_get
```

### Make a Prediction
```bash
POST https://credit-scoring-h7mv.onrender.com/docs#/Prediction/predict_loan_api_predict_post
Content-Type: application/json

{
  "person_age": 30,
  "person_income": 60000,
  "person_emp_length": 5.0,
  "person_home_ownership": "MORTGAGE",
  "loan_amnt": 15000,
  "loan_intent": "PERSONAL",
  "loan_grade": "B",
  "loan_int_rate": 8.5,
  "loan_percent_income": 0.25,
  "cb_person_cred_hist_length": 8,
  "credit_score": 720,
  "cb_person_default_on_file": "N",
  "previous_loan_defaults_on_file": "N"
}
```

### Batch Predictions
```bash
POST https://credit-scoring-h7mv.onrender.com/docs#/Prediction/batch_predict_api_batch_predict_post
Content-Type: application/json

[
  { ... prediction data 1 ... },
  { ... prediction data 2 ... }
]
```

### Model Information
```bash
GET https://credit-scoring-h7mv.onrender.com/docs#/Model%20Info/get_model_info_api_model_info_get
GET https://credit-scoring-h7mv.onrender.com/docs#/Model%20Info/get_model_features_api_model_features_get
```

## Testing the API

### Using cURL

```bash
# Health check
curl https://credit-scoring-h7mv.onrender.com/docs#/Health/health_check_api_health_get

# Make a prediction
curl -X POST "https://credit-scoring-h7mv.onrender.com/docs#/Prediction/predict_loan_api_predict_post" \
  -H "Content-Type: application/json" \
  -d '{
    "person_age": 30,
    "person_income": 60000,
    "person_emp_length": 5.0,
    "person_home_ownership": "MORTGAGE",
    "loan_amnt": 15000,
    "loan_intent": "PERSONAL",
    "loan_grade": "B",
    "loan_int_rate": 8.5,
    "loan_percent_income": 0.25,
    "cb_person_cred_hist_length": 8,
    "credit_score": 720,
    "cb_person_default_on_file": "N",
    "previous_loan_defaults_on_file": "N"
  }'
```

### Using Python

```python
import requests

# Health check
response = requests.get("https://credit-scoring-h7mv.onrender.com/docs#/Health/health_check_api_health_get")
print(response.json())

# Make a prediction
data = {
    "person_age": 30,
    "person_income": 60000,
    "person_emp_length": 5.0,
    "person_home_ownership": "MORTGAGE",
    "loan_amnt": 15000,
    "loan_intent": "PERSONAL",
    "loan_grade": "B",
    "loan_int_rate": 8.5,
    "loan_percent_income": 0.25,
    "cb_person_cred_hist_length": 8,
    "credit_score": 720,
    "cb_person_default_on_file": "N",
    "previous_loan_defaults_on_file": "N"
}

response = requests.post("https://credit-scoring-h7mv.onrender.com/docs#/Prediction/predict_loan_api_predict_post", json=data)
print(response.json())
```

## Development Mode

### Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env  # Edit .env with your settings

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Security

1. **Change the SECRET_KEY** in `.env` file for production
2. **Update ALLOWED_ORIGINS** to include only your frontend domains
3. **Use HTTPS** in production
4. **Add authentication** if needed (API keys, JWT, etc.)

## Response Format

### Prediction Response
```json
{
  "prediction": 0,
  "probability": 0.25,
  "risk_level": "Low",
  "confidence": 0.95,
  "message": "Low default risk (25.0%). Applicant likely to repay."
}
```

### Risk Levels
- **Low**: probability < 0.25
- **Medium**: 0.25 ≤ probability < 0.50
- **High**: 0.50 ≤ probability < 0.75
- **Very High**: probability ≥ 0.75

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Rebuild without cache
docker-compose build --no-cache
docker-compose up
```

### Model files not found
Ensure model files are in the `models/` directory:
```bash
ls -la models/
# Should show:
# - lgb_model_optimized.pkl
# - ensemble_comparison_metadata.pkl
```

### Port already in use
Change the port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use port 8001 instead
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_NAME` | API name | Credit Scoring API |
| `VERSION` | API version | 1.0.0 |
| `ENVIRONMENT` | Environment | production |
| `API_PREFIX` | API route prefix | /api |
| `LOG_LEVEL` | Logging level | INFO |
| `ALLOWED_ORIGINS` | CORS origins | * |
| `SECRET_KEY` | Security key | (change in production) |

## Integration Examples

### React/Next.js
```javascript
const predictLoan = async (data) => {
  const response = await fetch('https://credit-scoring-h7mv.onrender.com/docs#/Prediction/predict_loan_api_predict_post', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return await response.json();
};
```

### Vue.js
```javascript
async function predictLoan(data) {
  const response = await axios.post(
    'https://credit-scoring-h7mv.onrender.com/docs#/Prediction/predict_loan_api_predict_post',
    data
  );
  return response.data;
}
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review API documentation: https://credit-scoring-h7mv.onrender.com/docs
3. Ensure all dependencies are installed
4. Verify model files are present

---

**Ready to use!** Start the Docker container and begin making predictions. 
