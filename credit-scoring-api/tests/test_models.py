import pytest
from pydantic import ValidationError
from app.models.schemas import PredictionRequest, PredictionResponse


class TestPredictionRequest:
    """Test PredictionRequest schema"""
    
    def test_valid_request(self):
        """Test valid prediction request"""
        data = {
            "person_age": 30,
            "person_income": 60000,
            "person_emp_length": 5.0,
            "loan_amnt": 15000,
            "loan_int_rate": 8.5,
            "loan_percent_income": 0.25,
            "cb_person_cred_hist_length": 8,
            "credit_score": 720,
            "person_home_ownership": "MORTGAGE",
            "loan_intent": "PERSONAL",
            "loan_grade": "B",
            "cb_person_default_on_file": "N",
            "previous_loan_defaults_on_file": "N"
        }
        request = PredictionRequest(**data)
        assert request.person_age == 30
        assert request.person_income == 60000
    
    def test_missing_required_field(self):
        """Test missing required field"""
        data = {
            "person_age": 30,
            "person_income": 60000
            # Missing other required fields
        }
        with pytest.raises(ValidationError):
            PredictionRequest(**data)  # type: ignore  # Intentionally incomplete for testing
    
    def test_invalid_age(self):
        """Test invalid age value (should raise validation error)"""
        data = {
            "person_age": 150,  # Too old
            "person_income": 60000,
            "person_emp_length": 5.0,
            "loan_amnt": 15000,
            "loan_int_rate": 8.5,
            "loan_percent_income": 0.25,
            "cb_person_cred_hist_length": 8,
            "credit_score": 720,
            "person_home_ownership": "MORTGAGE",
            "loan_intent": "PERSONAL",
            "loan_grade": "B",
            "cb_person_default_on_file": "N",
            "previous_loan_defaults_on_file": "N"
        }
        with pytest.raises(ValidationError):
            PredictionRequest(**data)
    
    def test_negative_income(self):
        """Test negative income (should raise validation error)"""
        data = {
            "person_age": 30,
            "person_income": -5000,  # Negative
            "person_emp_length": 5.0,
            "loan_amnt": 15000,
            "loan_int_rate": 8.5,
            "loan_percent_income": 0.25,
            "cb_person_cred_hist_length": 8,
            "credit_score": 720,
            "person_home_ownership": "MORTGAGE",
            "loan_intent": "PERSONAL",
            "loan_grade": "B",
            "cb_person_default_on_file": "N",
            "previous_loan_defaults_on_file": "N"
        }
        with pytest.raises(ValidationError):
            PredictionRequest(**data)


class TestPredictionResponse:
    """Test PredictionResponse schema"""
    
    def test_valid_response(self):
        """Test valid prediction response"""
        data = {
            "prediction": 0,
            "probability": 0.25,
            "risk_level": "Low"
        }
        response = PredictionResponse(**data)
        assert response.prediction == 0
        assert response.probability == 0.25
        assert response.risk_level == "Low"
    
    def test_response_with_all_fields(self):
        """Test response with optional fields"""
        data = {
            "prediction": 1,
            "probability": 0.85,
            "risk_level": "Very High",
            "confidence": 0.95,
            "message": "High default risk detected"
        }
        response = PredictionResponse(**data)
        assert response.prediction == 1
        assert response.probability == 0.85