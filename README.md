# 🏦 Credit Scoring System - AI-Powered Loan Approval

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![LightGBM](https://img.shields.io/badge/LightGBM-4.1-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Overview

An end-to-end machine learning system for credit risk assessment and loan approval prediction. This project uses **LightGBM** and **XGBoost** models to predict default probability and estimate maximum loan amounts for customers.

### 🎯 Key Features

- **AI-Powered Predictions**: Using state-of-the-art gradient boosting algorithms
- **Loan Amount Estimation**: Calculate maximum eligible loan based on risk profile
- **Risk Analysis**: Detailed breakdown of risk factors
- **RESTful API**: Easy integration with frontend applications
- **Docker Support**: Containerized deployment ready
- **Comprehensive Documentation**: Full API docs and usage examples

---

## 🏗️ Project Structure

```
Credit-Scoring/
├── 📊 notebooks/                     # Jupyter notebooks for analysis
│   ├── parquet_files/
│   │   ├── 01_data_integration.ipynb
│   │   ├── 02_eda_visualization.ipynb
│   │   ├── 03_feature_engineering.ipynb
│   │   ├── 04a_baseline_model.ipynb
│   │   ├── 04b_baseline_model_LightGBM_improved.ipynb
│   │   ├── 04c_ensemble_comparison_RF_XGB.ipynb
│   │   ├── 04d_XGBoost.ipynb
│   │   └── 05_cli_demo.ipynb
│
├── 🐳 credit-scoring-api/            # FastAPI Backend (See API README)
│   ├── app/
│   ├── models/
│   ├── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
│
├── 💾 data/                          # Data files
│   ├── raw/                          # Original datasets
│   ├── data-processing/              # Processed datasets
│   │   └── flat_table/
│   └── external/                     # External data sources
│
├── 📈 output/                        # Model artifacts
│   ├── models/                       # Trained models (.pkl files)
│   │   ├── lgbm_model_optimized.pkl
│   │   ├── xgboost_final.pkl
│   │   └── ensemble_comparison_metadata.pkl
│   ├── plots/                        # Visualizations
│   └── reports/                      # Analysis reports
│
├── 📚 docs/                          # Documentation
│   ├── API_GUIDE.md
│   ├── MODEL_DOCUMENTATION.md
│   └── DEPLOYMENT_GUIDE.md
│
├── 🧪 tests/                         # Unit tests
│
├── .gitignore
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)
- Git

### Installation

#### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/Credit-Scoring.git
cd Credit-Scoring
```

#### 2️⃣ Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4️⃣ Run Jupyter Notebooks (Optional)

```bash
jupyter notebook
# Navigate to notebooks/parquet_files/
```

#### 5️⃣ Run API Server

```bash
cd credit-scoring-api
uvicorn app.main:app --reload
```

Access API documentation: http://localhost:8000/api/docs

---

## 📊 Data Pipeline

### Data Flow

```
Raw Data (Application, Bureau, Credit Card, etc.)
    ↓
Data Integration & Cleaning
    ↓
Feature Engineering
    ↓
Train/Test Split
    ↓
Model Training (LightGBM, XGBoost)
    ↓
Hyperparameter Tuning
    ↓
Model Evaluation
    ↓
Deployment (FastAPI + Docker)
```

### Dataset Statistics

- **Total Records**: ~300,000 loan applications
- **Features**: 120+ engineered features
- **Target Variable**: Binary (0 = No Default, 1 = Default)
- **Class Imbalance**: ~92% no default, ~8% default

---

## 🤖 Models

### 1. LightGBM Classifier
- **ROC-AUC**: 0.72+
- **F1-Score**: 0.35+
- **Precision**: 45%+
- **Recall**: 55%+

### 2. XGBoost Classifier
- **ROC-AUC**: 0.70+
- **F1-Score**: 0.26+
- **Precision**: 20%+
- **Recall**: 36%+

### 3. Ensemble Model (Coming Soon)
- Combines both models for better predictions

---

## 🔌 API Usage

### Example Request

```python
import requests

url = "http://localhost:8000/api/predict"
data = {
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

response = requests.post(url, json=data)
result = response.json()

print(f"Decision: {result['decision']}")
print(f"Approved Amount: ${result['loan_estimation']['approved_amount']:,.2f}")
print(f"Interest Rate: {result['loan_estimation']['interest_rate']}%")
```

### Example Response

```json
{
  "customer_id": "CUST12345",
  "default_probability": 0.23,
  "risk_level": "LOW",
  "decision": "APPROVE",
  "loan_estimation": {
    "requested_amount": 150000,
    "approved_amount": 150000,
    "max_eligible_amount": 200000,
    "interest_rate": 6.5,
    "monthly_payment": 2567.89
  }
}
```

---

## 🐳 Docker Deployment

### Build and Run

```bash
cd credit-scoring-api
docker-compose up -d
```

### Check Status

```bash
docker ps
docker logs credit-scoring-api
```

### Stop

```bash
docker-compose down
```

---

## 📈 Performance Metrics

### Business Impact

| Metric | Value | Description |
|--------|-------|-------------|
| **Defaults Caught** | 55%+ | Percentage of actual defaults detected |
| **False Alarms** | ~45% | Good customers incorrectly rejected |
| **Business Cost** | $2.5M+ | Estimated financial impact |
| **Processing Time** | <100ms | Average prediction latency |

### Model Comparison

| Model | ROC-AUC | F1-Score | Precision | Recall |
|-------|---------|----------|-----------|--------|
| LightGBM | **0.72** | **0.35** | **45%** | **55%** |
| XGBoost | 0.70 | 0.26 | 20% | 36% |

---

## 🧪 Testing

### Run Unit Tests

```bash
cd credit-scoring-api
pytest tests/
```

### Test Coverage

```bash
pytest --cov=app tests/
```

---

## 📚 Documentation

- **API Documentation**: [API_GUIDE.md](docs/API_GUIDE.md)
- **Model Details**: [MODEL_DOCUMENTATION.md](docs/MODEL_DOCUMENTATION.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Interactive API Docs**: http://localhost:8000/api/docs (when running)

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Machine Learning
- **LightGBM** - Gradient boosting
- **XGBoost** - Gradient boosting
- **Scikit-learn** - ML utilities
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing

### Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

### Development
- **Jupyter** - Interactive notebooks
- **Pytest** - Testing framework
- **Black** - Code formatting

---

## 🗺️ Roadmap

- [x] Data pipeline
- [x] Feature engineering
- [x] Baseline models
- [x] LightGBM optimization
- [x] XGBoost implementation
- [x] FastAPI backend
- [x] Docker deployment
- [ ] Ensemble model
- [ ] Frontend dashboard
- [ ] A/B testing framework
- [ ] Model monitoring
- [ ] Auto-retraining pipeline
- [ ] Multi-cloud deployment

---

## 📊 Notebooks Overview

| Notebook | Description | Status |
|----------|-------------|--------|
| `01_data_integration.ipynb` | Data loading and merging | ✅ Complete |
| `02_eda_visualization.ipynb` | Exploratory data analysis | ✅ Complete |
| `03_feature_engineering.ipynb` | Feature creation | ✅ Complete |
| `04a_baseline_model.ipynb` | Initial model | ✅ Complete |
| `04b_baseline_model_LightGBM_improved.ipynb` | LightGBM optimization | ✅ Complete |
| `04c_ensemble_comparison_RF_XGB.ipynb` | Model comparison | ✅ Complete |
| `04d_XGBoost.ipynb` | XGBoost deep dive | ✅ Complete |
| `05_cli_demo.ipynb` | Interactive demo | ✅ Complete |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- Nguyen Van Quoc - [blacki0214](https://github.com/blacki0214)

---

## 🙏 Acknowledgments

- Dataset: Home Credit Default Risk (Kaggle)
- Inspired by real-world credit scoring systems
- Built with open-source tools

---

## 📞 Contact

- **Email**: vanquoc11082004@gmail.com
- **GitHub**: [blacki0214](https://github.com/blacki0214)
- **LinkedIn**: [Nguyen Van Quoc](https://www.linkedin.com/in/quoc-nguyen-van-7898ba255/)

---

## ⚠️ Disclaimer

This is an educational project. For production use, consult with financial and legal experts to ensure compliance with regulations (FCRA, GDPR, etc.).

---

**Last Updated**: November 2024

**Version**: 1.0.0