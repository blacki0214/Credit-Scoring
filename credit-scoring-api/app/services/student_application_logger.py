"""
Student Application Logger

Persists student scoring requests/results to Firestore for monitoring
and downstream labeling/retraining.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from firebase_admin import firestore

from app.core.config import settings

logger = logging.getLogger(__name__)


class StudentApplicationLogger:
    """Firestore logger for student scoring applications."""

    def __init__(self) -> None:
        self._db: Optional[Any] = None

    def _get_db(self):
        if self._db is None:
            self._db = firestore.client()
        return self._db

    def log_application(
        self,
        user_id: str,
        request_payload: Dict[str, Any],
        *,
        credit_score: int,
        loan_limit_vnd: float,
        risk_level: str,
        approved: bool,
        model_score: Optional[float],
        status: str,
        reason: Optional[str] = None,
    ) -> Optional[str]:
        """Write a student application record and return document id."""
        if not settings.STUDENT_APP_LOGGING_ENABLED:
            return None

        db = self._get_db()
        if db is None:
            raise RuntimeError("Firestore client is not available")
        collection = settings.STUDENT_APPLICATIONS_COLLECTION

        manual_review = (
            model_score is not None and 0.35 <= model_score <= 0.55
        )

        doc = {
            "userId": user_id,
            "gpa_latest": request_payload.get("gpa_latest"),
            "academic_year": request_payload.get("academic_year"),
            "major": request_payload.get("major", "other"),
            "program_level": request_payload.get("program_level", "undergraduate"),
            "living_status": request_payload.get("living_status", "dormitory"),
            "loan_amount": request_payload.get("loan_amount"),
            "has_buffer": bool(request_payload.get("has_buffer", False)),
            "support_sources": request_payload.get("support_sources", []),
            "monthly_income": request_payload.get("monthly_income"),
            "monthly_expenses": request_payload.get("monthly_expenses"),
            "model_score": model_score,
            "credit_score": credit_score,
            "loan_limit_vnd": loan_limit_vnd,
            "risk_level": risk_level,
            "approved": approved,
            "status": status,
            "reason": reason,
            "manual_review": manual_review,
            "repayment_status": None,
            "label": None,
            "createdAt": datetime.utcnow(),
        }

        ref = db.collection(collection).document()
        ref.set(doc)

        logger.info(
            "Student application logged: collection=%s doc=%s approved=%s score=%s",
            collection,
            ref.id,
            approved,
            credit_score,
        )
        return ref.id


student_application_logger = StudentApplicationLogger()
