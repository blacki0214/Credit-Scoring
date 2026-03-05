import firebase_admin
from firebase_admin import auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Initialize once at startup — uses GCP Application Default Credentials on Cloud Run
# No service account JSON needed when deployed; works locally with `gcloud auth application-default login`
if not firebase_admin._apps:
    firebase_admin.initialize_app()

security = HTTPBearer()


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """
    FastAPI dependency: validates Firebase ID token from Authorization header.

    Usage in route:
        user: dict = Depends(verify_firebase_token)

    Returns decoded token payload (uid, email, etc.) on success.
    """
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
