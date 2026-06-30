import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from ninja.errors import HttpError
from ninja.security import HttpBearer

# Mengambil Custom User Model yang didefinisikan di settings.py
User = get_user_model()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============================================================
# Membuat Access Token (Berlaku 1 jam)
# ============================================================
def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ============================================================
# Membuat Refresh Token (Berlaku 7 hari)
# ============================================================
def create_refresh_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ============================================================
# JWT Authentication
# ============================================================
class JWTAuth(HttpBearer):

    def authenticate(self, request, token):
        try:
            # Decode token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            # Pastikan token adalah access token
            if payload.get("type") != "access":
                return None

            user_id = payload.get("sub")

            if not user_id:
                return None

            # Mengambil user dari Custom User Model
            user = get_object_or_404(User, id=user_id)

            return user

        except jwt.ExpiredSignatureError:
            # Token kadaluarsa
            return None

        except jwt.InvalidTokenError:
            # Token tidak valid
            return None

        except Exception:
            # Error lain
            return None


# ============================================================
# ROLE BASED ACCESS CONTROL
# ============================================================

def is_instructor(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):

        if getattr(request.auth, "role", "") != "instructor":
            raise HttpError(
                403,
                "Akses ditolak: Membutuhkan role Instructor"
            )

        return func(request, *args, **kwargs)

    return wrapper


def is_student(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):

        if getattr(request.auth, "role", "") != "student":
            raise HttpError(
                403,
                "Akses ditolak: Membutuhkan role Student"
            )

        return func(request, *args, **kwargs)

    return wrapper


def is_admin(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):

        if not request.auth.is_superuser:
            raise HttpError(
                403,
                "Akses ditolak: Membutuhkan role Admin"
            )

        return func(request, *args, **kwargs)

    return wrapper