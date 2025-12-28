# 🎯 Customer-Friendly Loan Application API

## Simple Loan Application Endpoint

**Endpoint:** `/api/apply`  
**Method:** POST  
**URL:** `https://credit-scoring-h7mv.onrender.com/docs#/`

This is the **recommended endpoint** for customer-facing applications. It uses simple, customer-friendly fields and automatically calculates credit scores.

---

## ✨ Why Use This Endpoint?

✅ **Customer-friendly** - No technical jargon  
✅ **Auto-calculated credit score** - Customers don't need to know their score  
✅ **Simple questions** - Easy yes/no questions  
✅ **VND currency** - All amounts in Vietnamese Dong  
✅ **Instant decision** - Get approval/rejection immediately  

---

## 📋 Request Example

```json
{
  "full_name": "Nguyen Van A",
  "age": 30,
  "monthly_income": 15000000,
  "employment_status": "EMPLOYED",
  "years_employed": 5.0,
  "home_ownership": "RENT",
  "loan_amount": 100000000,
  "loan_purpose": "PERSONAL",
  "years_credit_history": 3,
  "has_previous_defaults": false,
  "currently_defaulting": false
}
```

---

## 📝 Request Fields

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `full_name` | string | Customer's full name | e.g., "Nguyen Van A" |
| `age` | number | Age (18-100) | e.g., 30 |
| `monthly_income` | number | Monthly income in VND | e.g., 15000000 (15 million VND) |
| `employment_status` | string | Employment status | `EMPLOYED`, `SELF_EMPLOYED`, `UNEMPLOYED` |
| `years_employed` | number | Years in current job | e.g., 5.0 |
| `home_ownership` | string | Living situation | `RENT`, `OWN`, `MORTGAGE`, `LIVING_WITH_PARENTS` |
| `loan_amount` | number | Requested loan in VND | e.g., 100000000 (100 million VND) |
| `loan_purpose` | string | Why need loan? | `PERSONAL`, `EDUCATION`, `MEDICAL`, `BUSINESS`, `HOME_IMPROVEMENT`, `DEBT_CONSOLIDATION` |
| `years_credit_history` | number | Years with credit/loans | e.g., 3 (or 0 if none) |
| `has_previous_defaults` | boolean | Ever defaulted before? | `true` or `false` |
| `currently_defaulting` | boolean | Currently in default? | `true` or `false` |

---

## ✅ Response Example

```json
{
  "approved": true,
  "loan_amount_vnd": 100000000.0,
  "requested_amount_vnd": 100000000.0,
  "max_amount_vnd": 900000000.0,
  "interest_rate": 8.5,
  "monthly_payment_vnd": 3156753.74,
  "loan_term_months": 36,
  "credit_score": 785,
  "risk_level": "Low",
  "approval_message": "Loan approved! Low risk applicant. Full amount granted."
}
```

---

## 🔍 How Credit Score is Calculated

The system automatically calculates credit score (300-850) based on:

| Factor | Impact | Points |
|--------|--------|--------|
| **Age** | Older = more stable | Up to +50 |
| **Income** | Higher = better | Up to +50 |
| **Employment length** | Longer = stable | Up to +40 |
| **Home ownership** | Own > Mortgage > Rent | Up to +30 |
| **Credit history** | Longer = better | Up to +40 |
| **Employment status** | Employed > Self-employed | Up to +20 |
| **No defaults** | Clean record | No penalty |
| **Has defaults** | Previous defaults | -80 to -150 |
| **Debt-to-income** | Lower is better | -0 to -50 |

**Starting score:** 650  
**Final score:** 300-850 range

---

## 💡 Integration Examples

### React/Next.js

```javascript
async function applyForLoan(customerData) {
  const response = await fetch('https://credit-scoring-h7mv.onrender.com/api/apply', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      full_name: customerData.fullName,
      age: customerData.age,
      monthly_income: customerData.monthlyIncome, // in VND
      employment_status: customerData.employmentStatus,
      years_employed: customerData.yearsEmployed,
      home_ownership: customerData.homeOwnership,
      loan_amount: customerData.loanAmount, // in VND
      loan_purpose: customerData.loanPurpose,
      years_credit_history: customerData.yearsCreditHistory || 0,
      has_previous_defaults: customerData.hasPreviousDefaults || false,
      currently_defaulting: customerData.currentlyDefaulting || false,
    }),
  });
  
  const result = await response.json();
  
  if (result.approved) {
    console.log('✅ APPROVED!');
    console.log(`Loan Amount: ${result.loan_amount_vnd.toLocaleString('vi-VN')} VND`);
    console.log(`Credit Score: ${result.credit_score}`);
    console.log(`Monthly Payment: ${result.monthly_payment_vnd.toLocaleString('vi-VN')} VND`);
  } else {
    console.log('❌ Not approved');
    console.log(result.approval_message);
  }
  
  return result;
}
```

### Python

```python
import requests

def apply_for_loan(customer_data):
    response = requests.post(
        'https://credit-scoring-h7mv.onrender.com/api/apply',
        json={
            'full_name': customer_data['full_name'],
            'age': customer_data['age'],
            'monthly_income': customer_data['monthly_income'],  # VND
            'employment_status': customer_data['employment_status'],
            'years_employed': customer_data['years_employed'],
            'home_ownership': customer_data['home_ownership'],
            'loan_amount': customer_data['loan_amount'],  # VND
            'loan_purpose': customer_data['loan_purpose'],
            'years_credit_history': customer_data.get('years_credit_history', 0),
            'has_previous_defaults': customer_data.get('has_previous_defaults', False),
            'currently_defaulting': customer_data.get('currently_defaulting', False),
        }
    )
    
    result = response.json()
    
    if result['approved']:
        print(f"✅ APPROVED for {result['full_name']}")
        print(f"Amount: {result['loan_amount_vnd']:,.0f} VND")
        print(f"Credit Score: {result['credit_score']}")
        print(f"Monthly: {result['monthly_payment_vnd']:,.0f} VND")
    else:
        print(f"❌ Not approved: {result['approval_message']}")
    
    return result
```

---

## 📱 Simple Form Example

Here's how to collect customer information in a user-friendly form:

```javascript
const LoanApplicationForm = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    age: '',
    monthlyIncome: '',
    employmentStatus: 'EMPLOYED',
    yearsEmployed: '',
    homeOwnership: 'RENT',
    loanAmount: '',
    loanPurpose: 'PERSONAL',
    yearsCreditHistory: 0,
    hasPreviousDefaults: false,
    currentlyDefaulting: false,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const application = {
      full_name: formData.fullName,
      age: parseInt(formData.age),
      monthly_income: parseFloat(formData.monthlyIncome),
      employment_status: formData.employmentStatus,
      years_employed: parseFloat(formData.yearsEmployed),
      home_ownership: formData.homeOwnership,
      loan_amount: parseFloat(formData.loanAmount),
      loan_purpose: formData.loanPurpose,
      years_credit_history: parseInt(formData.yearsCreditHistory),
      has_previous_defaults: formData.hasPreviousDefaults,
      currently_defaulting: formData.currentlyDefaulting,
    };

    const result = await applyForLoan(application);
    // Handle result...
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Personal Info */}
      <input 
        type="text" 
        placeholder="Họ và tên"
        value={formData.fullName}
        onChange={(e) => setFormData({...formData, fullName: e.target.value})}
      />
      
      <input 
        type="number" 
        placeholder="Tuổi"
        value={formData.age}
        onChange={(e) => setFormData({...formData, age: e.target.value})}
      />
      
      <input 
        type="number" 
        placeholder="Thu nhập hàng tháng (VND)"
        value={formData.monthlyIncome}
        onChange={(e) => setFormData({...formData, monthlyIncome: e.target.value})}
      />
      
      {/* Employment */}
      <select 
        value={formData.employmentStatus}
        onChange={(e) => setFormData({...formData, employmentStatus: e.target.value})}
      >
        <option value="EMPLOYED">Đang làm việc</option>
        <option value="SELF_EMPLOYED">Tự kinh doanh</option>
        <option value="UNEMPLOYED">Không có việc làm</option>
      </select>
      
      {/* Loan Amount */}
      <input 
        type="number" 
        placeholder="Số tiền vay (VND)"
        value={formData.loanAmount}
        onChange={(e) => setFormData({...formData, loanAmount: e.target.value})}
      />
      
      {/* Simple Yes/No Questions */}
      <label>
        <input 
          type="checkbox"
          checked={formData.hasPreviousDefaults}
          onChange={(e) => setFormData({...formData, hasPreviousDefaults: e.target.checked})}
        />
        Đã từng vỡ nợ trước đây?
      </label>
      
      <button type="submit">Nộp đơn vay</button>
    </form>
  );
};
```

---

## 🧪 Test with cURL

```bash
curl -X POST "https://credit-scoring-h7mv.onrender.com/api/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Nguyen Van A",
    "age": 30,
    "monthly_income": 15000000,
    "employment_status": "EMPLOYED",
    "years_employed": 5.0,
    "home_ownership": "RENT",
    "loan_amount": 100000000,
    "loan_purpose": "PERSONAL",
    "years_credit_history": 3,
    "has_previous_defaults": false,
    "currently_defaulting": false
  }'
```

## 💼 Business Logic

### Approval Rules
- **Approved** if calculated default risk < 30%
- **Rejected** if risk ≥ 30%

### Interest Rates by Credit Score
- **780+:** 5.5% (Grade A)
- **740-779:** 8.5% (Grade B)
- **700-739:** 11.5% (Grade C)
- **660-699:** 14.5% (Grade D)
- **620-659:** 17.5% (Grade E)
- **< 620:** 20.0% (Grade F)

### Maximum Loan Amount
- Base: **5× Annual Income**
- Adjusted by risk level
- Example: Monthly income 15M VND = Annual 180M VND
  - Max loan = 900M VND (for low risk)

---

## 🎉 Benefits

1. **No technical knowledge needed** - Customers answer simple questions
2. **Automatic credit assessment** - System calculates everything
3. **Instant decision** - No waiting
4. **Clear messaging** - Easy to understand approval/rejection
5. **Vietnamese-friendly** - All amounts in VND

---

## 🔄 Migration Guide

If you're using the old `/api/loan-offer` endpoint:

**Old way (technical):**
```json
{
  "person_age": 30,
  "person_income": 60000,
  "credit_score": 720,  // Customer doesn't know this
  "loan_grade": "B",    // Customer doesn't know this
  ...13 fields total
}
```

**New way (simple):**
```json
{
  "full_name": "Nguyen Van A",
  "age": 30,
  "monthly_income": 15000000,  // Direct VND
  "employment_status": "EMPLOYED",
  ...11 simple fields
  // Credit score auto-calculated!
}
```

---

## ✅ Ready to Use!

Your app can now provide a **much better user experience** with:
- ✅ Simple, clear questions
- ✅ No confusing technical terms
- ✅ Automatic credit scoring
- ✅ All amounts in VND
- ✅ Instant loan decisions

Start using `/api/apply` today!
