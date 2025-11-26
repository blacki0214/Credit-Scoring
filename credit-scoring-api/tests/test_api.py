import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "models_loaded" in data
    
    def test_ping(self):
        """Test ping endpoint"""
        response = client.get("/api/ping")
        assert response.status_code == 200
        assert response.json() == {"message": "pong"}


class TestModelInfoEndpoints:
    """Test model info endpoints"""
    
    def test_model_info(self):
        """Test model info endpoint"""
        response = client.get("/api/model-info")
        assert response.status_code == 200
        data = response.json()
        assert "model_type" in data
        assert "models_loaded" in data
        assert data["model_type"] == "LightGBM"


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Credit Scoring API"
        assert "version" in data
        assert "docs" in data