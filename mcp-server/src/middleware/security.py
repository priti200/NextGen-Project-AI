"""
Security middleware and authentication for MCP Server
"""
from fastapi import HTTPException, Security, status, Request
from fastapi.security import APIKeyHeader
from typing import Optional
import time
from collections import defaultdict
from datetime import datetime, timedelta

from config import get_settings

settings = get_settings()

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_period: int = 100, period_seconds: int = 60):
        self.requests_per_period = requests_per_period
        self.period_seconds = period_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limits"""
        now = time.time()
        cutoff = now - self.period_seconds
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.requests_per_period:
            return False
        
        # Add new request
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client"""
        now = time.time()
        cutoff = now - self.period_seconds
        
        recent_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
        
        return max(0, self.requests_per_period - len(recent_requests))


# Global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_period=settings.rate_limit_requests,
    period_seconds=settings.rate_limit_period
)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key from request header.
    Returns client identifier if valid, raises HTTPException otherwise.
    """
    # Skip authentication if no API key is configured
    if not hasattr(settings, 'api_key') or not settings.api_key:
        return "anonymous"
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Get client identifier (IP or API key)
    client_id = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(settings.rate_limit_requests),
                "X-RateLimit-Period": str(settings.rate_limit_period),
                "Retry-After": str(settings.rate_limit_period)
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    remaining = rate_limiter.get_remaining(client_id)
    
    response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Period"] = str(settings.rate_limit_period)
    
    return response


def add_security_headers(response):
    """Add security headers to response"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


async def security_headers_middleware(request: Request, call_next):
    """Middleware to add security headers"""
    response = await call_next(request)
    return add_security_headers(response)
