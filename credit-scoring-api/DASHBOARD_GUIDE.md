# 📊 Dashboard Integration Guide

## Credit Score Endpoint for Analytics

**Endpoint:** `/api/credit-score`  
**Method:** POST  
**Purpose:** Get detailed credit score calculation for dashboard analytics

---

## 🎯 Use Cases

✅ **Customer Dashboard** - Show credit score to users  
✅ **Credit Score Tracking** - Track improvements over time  
✅ **Analytics & Reporting** - Understand customer segments  
✅ **Score Breakdown** - Explain how score is calculated  
✅ **Financial Health Monitoring** - Monitor customer creditworthiness  

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

## ✅ Response Example

```json
{
  "full_name": "Nguyen Van A",
  "credit_score": 785,
  "loan_grade": "A",
  "risk_level": "Low",
  "score_breakdown": {
    "base_score": 650,
    "age_adjustment": 30,
    "income_adjustment": 30,
    "employment_adjustment": 30,
    "home_ownership_adjustment": 5,
    "credit_history_adjustment": 20,
    "employment_status_adjustment": 20,
    "defaults_adjustment": 0,
    "debt_to_income_adjustment": 0,
    "final_score": 785
  }
}
```

---

## 📊 Score Breakdown Explained

| Factor | Description | Range |
|--------|-------------|-------|
| **base_score** | Starting point for all customers | 650 |
| **age_adjustment** | Older = more stable | +10 to +50 |
| **income_adjustment** | Higher income = better | +10 to +50 |
| **employment_adjustment** | Longer employment = stable | +10 to +40 |
| **home_ownership_adjustment** | Own > Mortgage > Rent | +5 to +30 |
| **credit_history_adjustment** | Longer history = better | 0 to +40 |
| **employment_status_adjustment** | Employed > Self-employed | -30 to +20 |
| **defaults_adjustment** | Penalty for defaults | -150 to 0 |
| **debt_to_income_adjustment** | High DTI = penalty | -50 to 0 |
| **final_score** | Total credit score | 300-850 |

---

## 💡 Dashboard Examples

### React Credit Score Dashboard

```jsx
import React, { useState, useEffect } from 'react';
import { Gauge } from '@ant-design/plots';

const CreditScoreDashboard = ({ customerData }) => {
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchCreditScore = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/credit-score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customerData),
      });
      const data = await response.json();
      setScoreData(data);
    } catch (error) {
      console.error('Error fetching credit score:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (customerData) {
      fetchCreditScore();
    }
  }, [customerData]);

  if (loading) return <div>Đang tính điểm tín dụng...</div>;
  if (!scoreData) return null;

  const getScoreColor = (score) => {
    if (score >= 800) return '#52c41a'; // Green
    if (score >= 700) return '#1890ff'; // Blue
    if (score >= 600) return '#faad14'; // Orange
    return '#f5222d'; // Red
  };

  return (
    <div className="credit-score-dashboard">
      <h2>Điểm Tín Dụng của {scoreData.full_name}</h2>
      
      {/* Credit Score Gauge */}
      <div className="score-gauge">
        <Gauge
          percent={scoreData.credit_score / 850}
          range={{
            color: getScoreColor(scoreData.credit_score),
          }}
          startAngle={Math.PI}
          endAngle={2 * Math.PI}
          indicator={{
            pointer: { style: { stroke: '#D0D0D0' } },
            pin: { style: { stroke: '#D0D0D0' } },
          }}
          statistic={{
            content: {
              style: { fontSize: '48px', fontWeight: 'bold' },
              content: scoreData.credit_score.toString(),
            },
          }}
        />
        <div className="score-details">
          <p>Hạng: <strong>{scoreData.loan_grade}</strong></p>
          <p>Rủi ro: <strong>{scoreData.risk_level}</strong></p>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="score-breakdown">
        <h3>Chi Tiết Tính Điểm</h3>
        <table>
          <thead>
            <tr>
              <th>Yếu Tố</th>
              <th>Điểm</th>
              <th>Ảnh Hưởng</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Điểm cơ bản</td>
              <td>{scoreData.score_breakdown.base_score}</td>
              <td>—</td>
            </tr>
            <tr>
              <td>Độ tuổi</td>
              <td>+{scoreData.score_breakdown.age_adjustment}</td>
              <td>{getImpact(scoreData.score_breakdown.age_adjustment, 50)}</td>
            </tr>
            <tr>
              <td>Thu nhập</td>
              <td>+{scoreData.score_breakdown.income_adjustment}</td>
              <td>{getImpact(scoreData.score_breakdown.income_adjustment, 50)}</td>
            </tr>
            <tr>
              <td>Thời gian làm việc</td>
              <td>+{scoreData.score_breakdown.employment_adjustment}</td>
              <td>{getImpact(scoreData.score_breakdown.employment_adjustment, 40)}</td>
            </tr>
            <tr>
              <td>Tình trạng sở hữu nhà</td>
              <td>+{scoreData.score_breakdown.home_ownership_adjustment}</td>
              <td>{getImpact(scoreData.score_breakdown.home_ownership_adjustment, 30)}</td>
            </tr>
            <tr>
              <td>Lịch sử tín dụng</td>
              <td>+{scoreData.score_breakdown.credit_history_adjustment}</td>
              <td>{getImpact(scoreData.score_breakdown.credit_history_adjustment, 40)}</td>
            </tr>
            <tr>
              <td>Tình trạng việc làm</td>
              <td>{scoreData.score_breakdown.employment_status_adjustment >= 0 ? '+' : ''}{scoreData.score_breakdown.employment_status_adjustment}</td>
              <td>{getImpact(Math.abs(scoreData.score_breakdown.employment_status_adjustment), 20)}</td>
            </tr>
            {scoreData.score_breakdown.defaults_adjustment < 0 && (
              <tr className="negative">
                <td>Vỡ nợ</td>
                <td>{scoreData.score_breakdown.defaults_adjustment}</td>
                <td>❌ Tiêu cực</td>
              </tr>
            )}
            {scoreData.score_breakdown.debt_to_income_adjustment < 0 && (
              <tr className="negative">
                <td>Nợ/Thu nhập</td>
                <td>{scoreData.score_breakdown.debt_to_income_adjustment}</td>
                <td>⚠️ Cảnh báo</td>
              </tr>
            )}
          </tbody>
          <tfoot>
            <tr>
              <td><strong>Tổng điểm</strong></td>
              <td colSpan="2"><strong>{scoreData.score_breakdown.final_score}</strong></td>
            </tr>
          </tfoot>
        </table>
      </div>

      {/* Improvement Tips */}
      <div className="improvement-tips">
        <h3>💡 Cách Cải Thiện Điểm Tín Dụng</h3>
        <ul>
          {scoreData.score_breakdown.age_adjustment < 50 && (
            <li>Điểm sẽ tự động tăng khi bạn già hơn</li>
          )}
          {scoreData.score_breakdown.income_adjustment < 50 && (
            <li>Tăng thu nhập để cải thiện điểm</li>
          )}
          {scoreData.score_breakdown.employment_adjustment < 40 && (
            <li>Làm việc lâu hơn để chứng minh sự ổn định</li>
          )}
          {scoreData.score_breakdown.home_ownership_adjustment < 30 && (
            <li>Sở hữu nhà sẽ cải thiện điểm tín dụng</li>
          )}
          {scoreData.score_breakdown.credit_history_adjustment < 40 && (
            <li>Xây dựng lịch sử tín dụng lâu hơn</li>
          )}
          {scoreData.score_breakdown.defaults_adjustment < 0 && (
            <li className="critical">⚠️ Thanh toán đầy đủ các khoản nợ hiện tại</li>
          )}
          {scoreData.score_breakdown.debt_to_income_adjustment < 0 && (
            <li>Giảm tỷ lệ nợ so với thu nhập</li>
          )}
        </ul>
      </div>
    </div>
  );
};

// Helper function
const getImpact = (value, max) => {
  const percentage = (value / max) * 100;
  if (percentage >= 80) return '⭐⭐⭐ Rất tốt';
  if (percentage >= 60) return '⭐⭐ Tốt';
  if (percentage >= 40) return '⭐ Trung bình';
  return '⚠️ Cần cải thiện';
};

export default CreditScoreDashboard;
```

---

### Python Dashboard (Streamlit)

```python
import streamlit as st
import requests
import plotly.graph_objects as go

st.title("🏦 Bảng Điểm Tín Dụng")

# Customer input form
with st.form("customer_form"):
    full_name = st.text_input("Họ và tên", "Nguyen Van A")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Tuổi", 18, 100, 30)
        monthly_income = st.number_input("Thu nhập hàng tháng (VND)", 0, 100000000, 15000000, step=1000000)
        employment_status = st.selectbox("Tình trạng việc làm", ["EMPLOYED", "SELF_EMPLOYED", "UNEMPLOYED"])
        years_employed = st.number_input("Số năm làm việc", 0.0, 50.0, 5.0)
    
    with col2:
        home_ownership = st.selectbox("Sở hữu nhà", ["RENT", "OWN", "MORTGAGE", "LIVING_WITH_PARENTS"])
        loan_amount = st.number_input("Số tiền vay (VND)", 0, 1000000000, 100000000, step=10000000)
        loan_purpose = st.selectbox("Mục đích vay", ["PERSONAL", "EDUCATION", "MEDICAL", "BUSINESS", "HOME_IMPROVEMENT"])
        years_credit_history = st.number_input("Lịch sử tín dụng (năm)", 0, 50, 3)
    
    has_previous_defaults = st.checkbox("Từng vỡ nợ trước đây?")
    currently_defaulting = st.checkbox("Đang trong tình trạng vỡ nợ?")
    
    submitted = st.form_submit_button("Tính Điểm Tín Dụng")

if submitted:
    # Call API
    response = requests.post(
        "http://localhost:8000/api/credit-score",
        json={
            "full_name": full_name,
            "age": age,
            "monthly_income": monthly_income,
            "employment_status": employment_status,
            "years_employed": years_employed,
            "home_ownership": home_ownership,
            "loan_amount": loan_amount,
            "loan_purpose": loan_purpose,
            "years_credit_history": years_credit_history,
            "has_previous_defaults": has_previous_defaults,
            "currently_defaulting": currently_defaulting,
        }
    )
    
    data = response.json()
    
    # Display score gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=data['credit_score'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Điểm Tín Dụng"},
        gauge={
            'axis': {'range': [300, 850]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [300, 579], 'color': "red"},
                {'range': [580, 669], 'color': "orange"},
                {'range': [670, 739], 'color': "yellow"},
                {'range': [740, 799], 'color': "lightgreen"},
                {'range': [800, 850], 'color': "green"},
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': data['credit_score']
            }
        }
    ))
    
    st.plotly_chart(fig)
    
    # Display details
    col1, col2, col3 = st.columns(3)
    col1.metric("Điểm Tín Dụng", data['credit_score'])
    col2.metric("Hạng Vay", data['loan_grade'])
    col3.metric("Mức Rủi ro", data['risk_level'])
    
    # Score breakdown
    st.subheader("📊 Chi Tiết Tính Điểm")
    breakdown = data['score_breakdown']
    
    df_breakdown = {
        "Yếu Tố": [
            "Điểm cơ bản",
            "Độ tuổi",
            "Thu nhập",
            "Thời gian làm việc",
            "Sở hữu nhà",
            "Lịch sử tín dụng",
            "Tình trạng việc làm",
            "Vỡ nợ",
            "Nợ/Thu nhập"
        ],
        "Điểm": [
            breakdown['base_score'],
            f"+{breakdown['age_adjustment']}",
            f"+{breakdown['income_adjustment']}",
            f"+{breakdown['employment_adjustment']}",
            f"+{breakdown['home_ownership_adjustment']}",
            f"+{breakdown['credit_history_adjustment']}",
            f"+{breakdown['employment_status_adjustment']}" if breakdown['employment_status_adjustment'] >= 0 else str(breakdown['employment_status_adjustment']),
            str(breakdown['defaults_adjustment']),
            str(breakdown['debt_to_income_adjustment'])
        ]
    }
    
    st.table(df_breakdown)
    st.success(f"**Tổng điểm:** {breakdown['final_score']}")
```

---

## 📈 Sample Test Cases

### Excellent Customer (Score: 850)
```json
{
  "full_name": "Tran Thi B",
  "age": 45,
  "monthly_income": 35000000,
  "employment_status": "EMPLOYED",
  "years_employed": 12.0,
  "home_ownership": "OWN",
  "loan_amount": 200000000,
  "loan_purpose": "HOME_IMPROVEMENT",
  "years_credit_history": 15,
  "has_previous_defaults": false,
  "currently_defaulting": false
}
```
**Result:** Credit Score = 850 (Grade A, Low Risk)

### Average Customer (Score: 785)
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
**Result:** Credit Score = 785 (Grade A, Low Risk)

### Risky Customer (Score: 615)
```json
{
  "full_name": "Le Van C",
  "age": 22,
  "monthly_income": 8000000,
  "employment_status": "SELF_EMPLOYED",
  "years_employed": 1.0,
  "home_ownership": "LIVING_WITH_PARENTS",
  "loan_amount": 50000000,
  "loan_purpose": "PERSONAL",
  "years_credit_history": 0,
  "has_previous_defaults": true,
  "currently_defaulting": false
}
```
**Result:** Credit Score = 615 (Grade F, Low Risk)

---

## 🎨 Visualization Ideas

### 1. Credit Score Gauge
- Show score 300-850 with color-coded ranges
- Red (300-579): Poor
- Orange (580-669): Fair
- Yellow (670-739): Good
- Light Green (740-799): Very Good
- Green (800-850): Excellent

### 2. Score Breakdown Chart
- Bar chart showing each factor's contribution
- Positive factors in green
- Negative factors in red

### 3. Score Trend Over Time
- Line chart tracking customer's score history
- Show improvements month-by-month

### 4. Factor Comparison
- Radar chart comparing customer to average
- Show strengths and weaknesses

---

## 🔄 Integration Flow

```
Customer Dashboard
      ↓
   Input Data
      ↓
POST /api/credit-score
      ↓
  Get Response
      ↓
Display:
- Score gauge
- Grade badge
- Risk level
- Breakdown table
- Improvement tips
```

---

## ✅ Benefits

1. **Transparent Scoring** - Customers see exactly how score is calculated
2. **Actionable Insights** - Know what to improve
3. **Real-time Updates** - Instant recalculation as data changes
4. **Educational** - Helps customers understand credit
5. **Dashboard Ready** - Perfect for analytics and monitoring

---

## 🚀 Ready to Use!

Your credit score endpoint is live at:
```
http://localhost:8000/api/credit-score
```

Perfect for building customer dashboards and analytics! 📊
