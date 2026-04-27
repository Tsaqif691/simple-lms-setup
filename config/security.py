import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja.security import HttpBearer
from functools import wraps
from ninja.errors import HttpError

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Fungsi mencetak Access Token (Berlaku 1 jam)
def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

# Fungsi mencetak Refresh Token (Berlaku 7 hari)
def create_refresh_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

# Middleware untuk mengecek keaslian token pada endpoint yang dilindungi
class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Membongkar isi token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            
            # Pastikan yang dipakai adalah access token, bukan refresh token
            if payload.get("type") != "access":
                return None
                
            user_id = payload.get("sub")
            user = get_object_or_404(User, id=user_id)
            return user
            
        except jwt.ExpiredSignatureError:
            return None # Token sudah kadaluarsa
        except jwt.PyJWTError:
            return None # Token palsu / rusak
        
# --- DECORATOR UNTUK ROLE-BASED ACCESS CONTROL (RBAC) ---
def is_instructor(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # Asumsi field role ada pada user model
        if getattr(request.auth, 'role', '') != 'instructor':
            raise HttpError(403, "Akses ditolak: Membutuhkan role Instructor")
        return func(request, *args, **kwargs)
    return wrapper

def is_student(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if getattr(request.auth, 'role', '') != 'student':
            raise HttpError(403, "Akses ditolak: Membutuhkan role Student")
        return func(request, *args, **kwargs)
    return wrapper

def is_admin(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.auth.is_superuser:
            raise HttpError(403, "Akses ditolak: Membutuhkan role Admin")
        return func(request, *args, **kwargs)
    return wrapper