from functools import lru_cache

import jwt
from jwt import PyJWKClient

from app.core.config import Settings
from app.core.errors import APIError


@lru_cache(maxsize=4)
def _jwks_client(url: str):
    return PyJWKClient(url, cache_keys=True, lifespan=300)


def verify_access_token(token: str, settings: Settings) -> dict:
    try:
        if settings.supabase_jwks_url:
            key = _jwks_client(settings.supabase_jwks_url).get_signing_key_from_jwt(token).key
            algorithms = ["RS256", "ES256"]
        elif settings.supabase_jwt_secret:
            key = settings.supabase_jwt_secret.get_secret_value()
            algorithms = ["HS256"]
        else:
            raise APIError(503, "AUTH_CONFIGURATION_ERROR", "Authentication is not configured.")
        options = {"require": ["exp", "sub"]}
        kwargs = {
            "issuer": settings.supabase_jwt_issuer,
            "audience": settings.supabase_jwt_audience,
            "algorithms": algorithms,
            "options": options,
        }
        if not settings.supabase_jwt_issuer:
            kwargs["options"]["verify_iss"] = False
        return jwt.decode(token, key, **kwargs)
    except APIError:
        raise
    except jwt.ExpiredSignatureError:
        raise APIError(401, "TOKEN_EXPIRED", "The access token has expired.") from None
    except jwt.PyJWTError:
        raise APIError(401, "INVALID_TOKEN", "The access token is invalid.") from None
