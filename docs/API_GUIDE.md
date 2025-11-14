# 🔌 API Integration Guide

Complete guide for integrating Credit Scoring API with your frontend application.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Request/Response Format](#request-response-format)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Best Practices](#best-practices)
7. [Code Examples](#code-examples)

---

## 🚀 Getting Started

### Base URL

**Local Development:**
```
http://localhost:8000
```

**Production:**
```
https://your-api-domain.com
```

### API Versioning

All endpoints are prefixed with `/api`:
```
POST /api/predict
GET  /api/health
GET  /api/model/info
```

---

## 🔐 Authentication

### Development
No authentication required for local development.

### Production (Recommended)

Add API Key header:

```http
Authorization: Bearer YOUR_API_KEY
```

**Request Example:**
```javascript
fetch('https://api.example.com/api/predict', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  // ...
})
```

---

## 📨 Request/Response Format

### Request Body Structure

```typescript
interface CustomerInput {
  customer_id: string;           // Unique identifier
  age_years: number;             // 18-75
  employment_years: number;      // 0-50
  annual_income: number;         // 10,000 - 10,000,000
  requested_amount: number;      // 1,000 - 5,000,000
  credit_card_usage: number;     // 0-200 (percentage)
  days_past_due_avg: number;     // 0-90
  higher_education: boolean;     // true/false
  employment_status: string;     // "working" | "self_employed" | "retired" | "unemployed" | "student"
}
```

### Response Body Structure

```typescript
interface PredictionResult {
  customer_id: string;
  default_probability: number;    // 0-1
  threshold: number;              // Decision threshold
  risk_level: string;             // "VERY_LOW" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  decision: string;               // "APPROVE" | "REJECT"
  confidence: number;             // 0-1
  loan_estimation: LoanEstimation;
  risk_factors: RiskFactor[];
  model_version: string;
}

interface LoanEstimation {
  requested_amount: number;
  approved_amount: number;
  max_eligible_amount: number;
  interest_rate: number;
  loan_term_months: number;
  monthly_payment: number;
  recommendation: string;         // "APPROVE_FULL" | "APPROVE_PARTIAL" | "REJECT"
}

interface RiskFactor {
  factor: string;
  impact: string;                 // "positive" | "negative" | "neutral"
  value: string;
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Invalid input data |
| 422 | Validation Error | Data doesn't meet schema requirements |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | API temporarily unavailable |

### Error Response Format

```json
{
  "detail": "Error message here",
  "errors": [
    {
      "loc": ["body", "age_years"],
      "msg": "ensure this value is greater than or equal to 18",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### Error Handling Example

```javascript
async function predictLoan(customerData) {
  try {
    const response = await fetch('http://localhost:8000/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(customerData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Prediction failed');
    }

    return await response.json();

  } catch (error) {
    console.error('API Error:', error.message);
    // Show user-friendly error message
    return {
      error: true,
      message: 'Unable to process loan application. Please try again.'
    };
  }
}
```

---

## 🚦 Rate Limiting

### Limits

- **Development**: No limits
- **Production**: 100 requests/minute per IP

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699999999
```

### Handling Rate Limits

```javascript
async function apiCallWithRetry(url, data, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (response.status === 429) {
      const resetTime = response.headers.get('X-RateLimit-Reset');
      const waitTime = (resetTime * 1000) - Date.now();
      await new Promise(resolve => setTimeout(resolve, waitTime));
      continue;
    }

    return response;
  }
  throw new Error('Max retries exceeded');
}
```

---

## ✅ Best Practices

### 1. Validate Input Before Sending

```javascript
function validateCustomerData(data) {
  const errors = [];

  if (data.age_years < 18 || data.age_years > 75) {
    errors.push('Age must be between 18 and 75');
  }

  if (data.annual_income < 10000) {
    errors.push('Annual income must be at least $10,000');
  }

  if (data.requested_amount < 1000) {
    errors.push('Loan amount must be at least $1,000');
  }

  return errors;
}

// Usage
const errors = validateCustomerData(formData);
if (errors.length > 0) {
  alert(errors.join('\n'));
  return;
}
```

### 2. Use TypeScript for Type Safety

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

interface CustomerData {
  customer_id: string;
  age_years: number;
  // ... other fields
}

interface PredictionResponse {
  decision: string;
  loan_estimation: {
    approved_amount: number;
    // ... other fields
  };
}

async function predictLoan(data: CustomerData): Promise<PredictionResponse> {
  const response = await axios.post<PredictionResponse>(
    `${API_BASE}/predict`,
    data
  );
  return response.data;
}
```

### 3. Handle Loading States

```javascript
const [loading, setLoading] = useState(false);
const [result, setResult] = useState(null);
const [error, setError] = useState(null);

async function handleSubmit(formData) {
  setLoading(true);
  setError(null);

  try {
    const result = await predictLoan(formData);
    setResult(result);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
}
```

### 4. Cache Predictions (If Appropriate)

```javascript
const predictionCache = new Map();

async function predictWithCache(customerData) {
  const cacheKey = JSON.stringify(customerData);
  
  if (predictionCache.has(cacheKey)) {
    return predictionCache.get(cacheKey);
  }

  const result = await predictLoan(customerData);
  predictionCache.set(cacheKey, result);
  
  // Clear cache after 5 minutes
  setTimeout(() => predictionCache.delete(cacheKey), 5 * 60 * 1000);
  
  return result;
}
```

---

## 💻 Code Examples

### React Hook

```typescript
import { useState, useCallback } from 'react';
import axios from 'axios';

interface UseLoanPredictionResult {
  predict: (data: CustomerData) => Promise<void>;
  loading: boolean;
  result: PredictionResponse | null;
  error: string | null;
  reset: () => void;
}

export function useLoanPrediction(): UseLoanPredictionResult {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const predict = useCallback(async (data: CustomerData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post<PredictionResponse>(
        'http://localhost:8000/api/predict',
        data
      );
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { predict, loading, result, error, reset };
}

// Usage in component
function LoanForm() {
  const { predict, loading, result, error } = useLoanPrediction();

  const handleSubmit = (formData) => {
    predict(formData);
  };

  return (
    <div>
      {loading && <Spinner />}
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {result && <PredictionResult data={result} />}
    </div>
  );
}
```

### Vue Composable

```typescript
import { ref } from 'vue';
import axios from 'axios';

export function useLoanPrediction() {
  const loading = ref(false);
  const result = ref(null);
  const error = ref(null);

  async function predict(customerData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post(
        'http://localhost:8000/api/predict',
        customerData
      );
      result.value = response.data;
    } catch (err) {
      error.value = err.response?.data?.detail || 'Prediction failed';
    } finally {
      loading.value = false;
    }
  }

  function reset() {
    result.value = null;
    error.value = null;
  }

  return {
    predict,
    loading,
    result,
    error,
    reset
  };
}
```

### Angular Service

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LoanPredictionService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  predict(customerData: CustomerData): Observable<PredictionResponse> {
    return this.http.post<PredictionResponse>(
      `${this.apiUrl}/predict`,
      customerData
    );
  }

  getModelInfo(): Observable<ModelInfo> {
    return this.http.get<ModelInfo>(`${this.apiUrl}/model/info`);
  }

  checkHealth(): Observable<HealthStatus> {
    return this.http.get<HealthStatus>(`${this.apiUrl}/health`);
  }
}
```

---

## 🧪 Testing Integration

### Unit Test Example (Jest)

```javascript
import { predictLoan } from './api';

// Mock fetch
global.fetch = jest.fn();

describe('Loan Prediction API', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('should return prediction result on success', async () => {
    const mockResponse = {
      decision: 'APPROVE',
      default_probability: 0.23,
      loan_estimation: {
        approved_amount: 150000
      }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    const result = await predictLoan({ customer_id: 'TEST123' });

    expect(result.decision).toBe('APPROVE');
    expect(result.loan_estimation.approved_amount).toBe(150000);
  });

  it('should handle errors correctly', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Invalid input' })
    });

    await expect(predictLoan({ customer_id: 'TEST123' }))
      .rejects
      .toThrow('Invalid input');
  });
});
```

---

## 📞 Support

- **Documentation**: http://localhost:8000/api/docs
- **Email**: vanquoc11082004@gmai.com
- **GitHub Issues**: https://github.com/blacki0214/Credit-Scoring/issues

---

**Last Updated**: November 2024