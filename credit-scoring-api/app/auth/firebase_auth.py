import firebase_admin
from firebase_admin import auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Initialize once at startup — specify projectId so SDK knows which Firebase project
# to verify tokens against. Uses GCP Application Default Credentials on Cloud Run.
if not firebase_admin._apps:
    firebase_admin.initialize_app(options={
        'projectId': 'creditscore-c560f'
    })

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
