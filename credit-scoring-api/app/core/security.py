"""
Security utilities for API authentication and authorization
"""
from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# API Key Header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from X-API-Key header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    # Skip API key check in development if not set
    if settings.ENVIRONMENT == "development" and not settings.API_KEY:
        logger.warning("API_KEY not set in development mode - skipping authentication")
        return "dev-mode"
    
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Include 'X-API-Key' header in your request.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != settings.API_KEY:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key


async def get_api_key_optional(api_key: str = Security(api_key_header)) -> str | None:
    """
    Optional API key verification for endpoints that can work with or without auth.
    
    Args:
        api_key: API key from X-API-Key header
        
    Returns:
        API key if provided and valid, None otherwise
    """
    if not api_key:
        return None
    
    try:
        return await verify_api_key(api_key)
    except HTTPException:
        return None


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    Handles proxies and load balancers.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for X-Forwarded-For header (from proxies)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain
        return forwarded.split(",")[0].strip()
    
    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"
