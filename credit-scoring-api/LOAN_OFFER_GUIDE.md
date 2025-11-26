# Loan Offer API - Integration Guide

## 💰 Loan Offer Endpoint (VND Currency)

Your app can now get loan approval decisions with amounts in Vietnamese Dong (VND).

### Endpoint: `/api/loan-offer`

**Method:** POST

**URL:** `http://localhost:8000/api/loan-offer`

---

## 📋 Request Example

```json
{
  "person_age": 35,
  "person_income": 80000,
  "person_emp_length": 10.0,
  "person_home_ownership": "OWN",
  "loan_amnt": 10000,
  "loan_intent": "PERSONAL",
  "loan_grade": "A",
  "loan_int_rate": 5.5,
  "loan_percent_income": 0.125,
  "cb_person_cred_hist_length": 15,
  "credit_score": 780,
  "cb_person_default_on_file": "N",
  "previous_loan_defaults_on_file": "N"
}
```

**Note:** Income and loan amount are in USD and will be converted to VND (1 USD = 25,000 VND)

---

## ✅ Response Example (Approved)

```json
{
  "approved": true,
  "loan_amount_vnd": 250000000.0,
  "requested_amount_vnd": 250000000.0,
  "max_amount_vnd": 10000000000.0,
  "interest_rate": 8.5,
  "monthly_payment_vnd": 7891884.36,
  "loan_term_months": 36,
  "credit_score": 780,
  "risk_level": "Low",
  "approval_message": "Loan approved! Low risk applicant. Full amount granted."
}
```

---

## ❌ Response Example (Rejected)

```json
{
  "approved": false,
  "loan_amount_vnd": 0,
  "requested_amount_vnd": 500000000.0,
  "max_amount_vnd": 0,
  "interest_rate": 20.0,
  "monthly_payment_vnd": null,
  "loan_term_months": null,
  "credit_score": 580,
  "risk_level": "Very High",
  "approval_message": "Loan rejected. Very high default risk (65.2%). Unable to approve at this time."
}
```

---

## 🔑 Response Fields Explanation

| Field | Description |
|-------|-------------|
| `approved` | **true** if loan is approved, **false** if rejected |
| `loan_amount_vnd` | Approved loan amount in VND (0 if rejected) |
| `requested_amount_vnd` | Original requested amount in VND |
| `max_amount_vnd` | Maximum eligible loan amount based on income and risk |
| `interest_rate` | Annual interest rate (%) |
| `monthly_payment_vnd` | Estimated monthly payment in VND (null if rejected) |
| `loan_term_months` | Loan term in months (default: 36 months) |
| `credit_score` | Customer's credit score (300-850) |
| `risk_level` | Risk assessment: Low, Medium, High, Very High |
| `approval_message` | Detailed message explaining the decision |

---

## 📱 Frontend Integration Examples

### JavaScript/React

```javascript
async function getLoanOffer(applicationData) {
  const response = await fetch('http://localhost:8000/api/loan-offer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(applicationData),
  });
  
  const offer = await response.json();
  
  if (offer.approved) {
    console.log(`✅ Loan Approved: ${offer.loan_amount_vnd.toLocaleString()} VND`);
    console.log(`Credit Score: ${offer.credit_score}`);
    console.log(`Monthly Payment: ${offer.monthly_payment_vnd.toLocaleString()} VND`);
  } else {
    console.log(`❌ Loan Rejected: ${offer.approval_message}`);
    console.log(`Credit Score: ${offer.credit_score}`);
  }
  
  return offer;
}
```

### Python

```python
import requests

def get_loan_offer(application_data):
    response = requests.post(
        'http://localhost:8000/api/loan-offer',
        json=application_data
    )
    
    offer = response.json()
    
    if offer['approved']:
        print(f"✅ Loan Approved: {offer['loan_amount_vnd']:,.0f} VND")
        print(f"Credit Score: {offer['credit_score']}")
        print(f"Monthly Payment: {offer['monthly_payment_vnd']:,.0f} VND")
    else:
        print(f"❌ Loan Rejected: {offer['approval_message']}")
        print(f"Credit Score: {offer['credit_score']}")
    
    return offer
```

---

## 🎯 Approval Logic

### Risk Levels & Interest Rates

| Risk Level | Default Probability | Interest Rate | Approval Factor |
|-----------|-------------------|---------------|-----------------|
| **Low** | < 15% | 8.5% | 100% of requested |
| **Medium** | 15-30% | 12.0% | 75% of requested |
| **High** | 30-50% | 16.0% | 50% of requested |
| **Very High** | > 50% | 20.0% | **Rejected** |

### Approval Threshold

- **Approved** if default probability < 30%
- **Rejected** if default probability ≥ 30%

### Maximum Loan Amount

- Base formula: **5× Annual Income**
- Adjusted by risk level
- Example: 
  - Income: 80,000 USD (2,000,000,000 VND/year)
  - Low risk: Max = 10,000,000,000 VND
  - Medium risk: Max = 7,500,000,000 VND
  - High risk: Max = 5,000,000,000 VND

---

## 📊 Batch Processing

Process multiple applications at once:

**Endpoint:** `/api/batch-loan-offers`

```javascript
const applications = [
  { person_age: 30, person_income: 60000, ... },
  { person_age: 45, person_income: 95000, ... }
];

const response = await fetch('http://localhost:8000/api/batch-loan-offers', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(applications),
});

const result = await response.json();
console.log(`Processed: ${result.count} applications`);
console.log(`Approved: ${result.summary.approved}`);
console.log(`Total Amount: ${result.summary.total_approved_amount_vnd.toLocaleString()} VND`);
```

---

## 💡 Display Tips for Your App

### Show the Offer

```javascript
function displayOffer(offer) {
  if (offer.approved) {
    return `
      ✅ APPROVED
      
      Credit Score: ${offer.credit_score}
      Loan Amount: ${offer.loan_amount_vnd.toLocaleString()} VND
      Interest Rate: ${offer.interest_rate}%
      Monthly Payment: ${offer.monthly_payment_vnd.toLocaleString()} VND
      Loan Term: ${offer.loan_term_months} months
      
      ${offer.approval_message}
    `;
  } else {
    return `
      ❌ NOT APPROVED
      
      Credit Score: ${offer.credit_score}
      ${offer.approval_message}
      
      Maximum you may qualify for: ${offer.max_amount_vnd.toLocaleString()} VND
    `;
  }
}
```

---

## 🧪 Test the API

```bash
curl -X POST "http://localhost:8000/api/loan-offer" \
  -H "Content-Type: application/json" \
  -d '{
    "person_age": 35,
    "person_income": 80000,
    "person_emp_length": 10.0,
    "person_home_ownership": "OWN",
    "loan_amnt": 10000,
    "loan_intent": "PERSONAL",
    "loan_grade": "A",
    "loan_int_rate": 5.5,
    "loan_percent_income": 0.125,
    "cb_person_cred_hist_length": 15,
    "credit_score": 780,
    "cb_person_default_on_file": "N",
    "previous_loan_defaults_on_file": "N"
  }'
```

---

## 📝 Notes

- **Currency conversion:** 1 USD = 25,000 VND (hardcoded, can be updated in `loan_offer_service.py`)
- **Default loan term:** 36 months (can be customized)
- **All amounts in VND** for easy integration with Vietnamese apps
- **Risk-based pricing:** Lower risk = lower interest rate
- **Instant decision:** No need for separate prediction call

---

## 🎉 Ready to Integrate!

Your app can now:
1. ✅ Collect customer information
2. ✅ Send to `/api/loan-offer`
3. ✅ Display approval status
4. ✅ Show loan amount in VND
5. ✅ Show monthly payment
6. ✅ Provide clear approval/rejection message
