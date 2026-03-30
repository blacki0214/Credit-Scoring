import firebase_admin
from firebase_admin import auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

# Initialize once at startup — specify projectId so SDK knows which Firebase project
# to verify tokens against. Uses GCP Application Default Credentials on Cloud Run.
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={
        'projectId': 'creditscore-c560f'
    })

security = HTTPBearer(auto_error=False)


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> dict:
    """
    FastAPI dependency: validates Firebase ID token from Authorization header.

    Usage in route:
        user: dict = Depends(verify_firebase_token)

    Returns decoded token payload (uid, email, etc.) on success.
    """
    # Demo bypass is only permitted in non-production environments and must be
    # explicitly enabled with DEMO_AUTH_BYPASS_ENABLED=true.
    if (
        settings.ENVIRONMENT != "production"
        and settings.DEMO_AUTH_BYPASS_ENABLED
        and credentials is None
    ):
        return {
            "uid": settings.DEMO_AUTH_BYPASS_USER_ID,
            "email": settings.DEMO_AUTH_BYPASS_EMAIL,
            "auth_provider": "demo_bypass",
        }

    if credentials is None:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    try:
        decoded = auth.verify_id_token(credentials.credentials)
        return decoded
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token expired")
    except auth.RevokedIdTokenError:
        raise HTTPException(status_code=401, detail="Token has been revoked")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
