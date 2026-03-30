import pickle
from pathlib import Path

from app.services.student_feature_contract import STUDENT_MODEL_FEATURE_ORDER
from app.services.student_prediction_service import student_prediction_service


def test_student_engineered_feature_order_matches_contract():
    payload = {
        "age": 21,
        "gpa_latest": 3.2,
        "academic_year": 3,
        "major": "technology",
        "program_level": "undergraduate",
        "loan_amount": 8_000_000,
        "living_status": "dormitory",
        "has_buffer": True,
        "support_sources": ["family", "part_time"],
        "monthly_income": 2_000_000,
        "monthly_expenses": 3_000_000,
    }

    df = student_prediction_service._engineer(payload)
    assert list(df.columns) == STUDENT_MODEL_FEATURE_ORDER


def test_student_model_artifact_feature_order_parity():
    project_root = Path(__file__).resolve().parent.parent.parent
    model_path = project_root / "output" / "alternative_model" / "best_model_phase1.pkl"

    if not model_path.exists():
        raise AssertionError(f"Expected model artifact not found: {model_path}")

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    model_feature_names = list(model.get_booster().feature_names or [])
    assert model_feature_names == STUDENT_MODEL_FEATURE_ORDER


def test_student_preflight_reports_ok_with_current_artifacts():
    status = student_prediction_service.validate_runtime_assets(strict=False)
    assert "ok" in status
    assert "threshold" in status
    assert isinstance(status["threshold"], float)
