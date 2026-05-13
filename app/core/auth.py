"""
Keycloak JWT authentication and role-based authorization.
"""
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError

from app.config.settings import settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

# JWKS cache
_jwks_cache: Optional[dict] = None
_jwks_last_fetch: float = 0
JWKS_CACHE_TTL = 3600


@dataclass
class UserContext:
    """User context extracted from a validated Keycloak JWT."""
    sub: str
    username: str
    email: str
    roles: list[str] = field(default_factory=list)

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles


async def _fetch_jwks() -> dict:
    """Fetch JWKS from Keycloak, caching for JWKS_CACHE_TTL seconds."""
    global _jwks_cache, _jwks_last_fetch
    now = time.time()
    if _jwks_cache and (now - _jwks_last_fetch) < JWKS_CACHE_TTL:
        return _jwks_cache

    jwks_uri = (
        f"{settings.keycloak_server_url}/realms/{settings.keycloak_realm}"
        f"/protocol/openid-connect/certs"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(jwks_uri)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_last_fetch = now
        logger.info("JWKS fetched from Keycloak")
        return _jwks_cache


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> UserContext:
    """FastAPI dependency: validates the Bearer token and returns the current user."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = credentials.credentials

    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        jwks = await _fetch_jwks()
        key = None
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                key = jwk
                break

        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: signing key not found",
            )

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False, "verify_iss": False, "verify_exp": True},
        )

        roles = payload.get("realm_access", {}).get("roles", [])

        return UserContext(
            sub=payload["sub"],
            username=payload.get("preferred_username", ""),
            email=payload.get("email", ""),
            roles=roles,
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except httpx.HTTPError:
        logger.exception("Failed to fetch JWKS from Keycloak")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )


def requires_role(role: str):
    """FastAPI dependency factory: requires a specific realm role."""

    async def role_checker(
        current_user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        if role not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required",
            )
        return current_user

    return role_checker
