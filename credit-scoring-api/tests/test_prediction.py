import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import PredictionRequest

client = TestClient(app)


class TestPredictionEndpoint:
    """Test prediction endpoints"""
    
    @pytest.fixture
    def valid_prediction_data(self):
        """Valid prediction request data"""
        return {
            "person_age": 25,
            "person_income": 50000,
            "person_emp_length": 3.0,
            "loan_amnt": 10000,
            "loan_int_rate": 10.5,
            "loan_percent_income": 0.2,
            "cb_person_cred_hist_length": 5,
            "credit_score": 700,
            "person_home_ownership": "RENT",
            "loan_intent": "PERSONAL",
            "loan_grade": "B",
            "cb_person_default_on_file": "N",
            "previous_loan_defaults_on_file": "N"
        }
    
    @pytest.fixture
    def invalid_prediction_data(self):
        """Invalid prediction request data (missing required fields)"""
        return {
            "person_age": 25,
            "person_income": 50000
        }
    
    def test_predict_success(self, valid_prediction_data):
        """Test successful prediction"""
        response = client.post("/api/predict", json=valid_prediction_data)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
        assert "risk_level" in data
        assert data["prediction"] in [0, 1]
        assert 0 <= data["probability"] <= 1
        assert data["risk_level"] in ["Low", "Medium", "High", "Very High"]
    
    def test_predict_validation_error(self, invalid_prediction_data):
        """Test prediction with invalid data"""
        response = client.post("/api/predict", json=invalid_prediction_data)
        assert response.status_code == 422  # Validation error
    
    def test_predict_high_risk(self):
        """Test prediction for high-risk profile"""
        high_risk_data = {
            "person_age": 22,
            "person_income": 20000,
            "person_emp_length": 0.5,
            "loan_amnt": 25000,
            "loan_int_rate": 20.0,
            "loan_percent_income": 0.8,
            "cb_person_cred_hist_length": 1,
            "credit_score": 550,
            "person_home_ownership": "RENT",
            "loan_intent": "DEBTCONSOLIDATION",
            "loan_grade": "F",
            "cb_person_default_on_file": "Y",
            "previous_loan_defaults_on_file": "Y"
        }
        response = client.post("/api/predict", json=high_risk_data)
        assert response.status_code == 200
        data = response.json()
        # Should be high risk
        assert data["probability"] > 0.5
    
    def test_predict_low_risk(self):
        """Test prediction for low-risk profile"""
        low_risk_data = {
            "person_age": 35,
            "person_income": 100000,
            "person_emp_length": 10.0,
            "loan_amnt": 15000,
            "loan_int_rate": 6.0,
            "loan_percent_income": 0.15,
            "cb_person_cred_hist_length": 15,
            "credit_score": 800,
            "person_home_ownership": "MORTGAGE",
            "loan_intent": "HOMEIMPROVEMENT",
            "loan_grade": "A",
            "cb_person_default_on_file": "N",
            "previous_loan_defaults_on_file": "N"
        }
        response = client.post("/api/predict", json=low_risk_data)
        assert response.status_code == 200
        data = response.json()
        # Should be low risk
        assert data["probability"] < 0.3


class TestPredictionEdgeCases:
    """Test edge cases for prediction"""
    
    def test_predict_min_values(self):
        """Test with minimum acceptable values"""
        min_data = {
            "person_age": 18,
            "person_income": 1000,
            "person_emp_length": 0.0,
            "loan_amnt": 1000,
            "loan_int_rate": 5.0,
            "loan_percent_income": 0.01,
            "cb_person_cred_hist_length": 0,
            "credit_score": 300,
            "person_home_ownership": "RENT",
            "loan_intent": "PERSONAL",
            "loan_grade": "G",
            "cb_person_default_on_file": "N",
            "previous_loan_defaults_on_file": "N"
        }
        response = client.post("/api/predict", json=min_data)
        assert response.status_code == 200
    
    def test_predict_max_values(self):
        """Test with maximum values"""
        max_data = {
            "person_age": 80,
            "person_income": 500000,
            "person_emp_length": 40.0,
            "loan_amnt": 100000,
            "loan_int_rate": 25.0,
            "loan_percent_income": 0.99,
            "cb_person_cred_hist_length": 50,
            "credit_score": 850,
            "person_home_ownership": "OWN",
            "loan_intent": "VENTURE",
            "loan_grade": "A",
            "cb_person_default_on_file": "Y",
            "previous_loan_defaults_on_file": "Y"
        }
        response = client.post("/api/predict", json=max_data)
        assert response.status_code == 200