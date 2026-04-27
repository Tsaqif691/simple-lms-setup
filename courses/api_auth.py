from ninja import Router
from ninja.errors import HttpError
from ninja import Schema
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
import jwt

from config.security import create_access_token, create_refresh_token, JWTAuth
from .schemas import RegisterIn, LoginIn, TokenOut, UserOut, ProfileUpdateIn

User = get_user_model()
auth_router = Router(tags=["Authentication"])

class RefreshIn(Schema):
    refresh_token: str

@auth_router.post("/register", response=UserOut)
def register(request, payload: RegisterIn):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username sudah digunakan")
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email sudah digunakan")
        
    user = User.objects.create(
        username=payload.username,
        email=payload.email,
        password=make_password(payload.password), # Hashing password untuk keamanan
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    # Jika custom User modelmu butuh default role, set di sini
    if hasattr(user, 'role'):
        user.role = 'student'
        user.save()
        
    return user

@auth_router.post("/login", response=TokenOut)
def login(request, payload: LoginIn):
    try:
        user = User.objects.get(username=payload.username)
        # Verifikasi password
        if check_password(payload.password, user.password):
            return {
                "access_token": create_access_token(user.id),
                "refresh_token": create_refresh_token(user.id)
            }
    except User.DoesNotExist:
        pass
    raise HttpError(401, "Username atau password salah")

@auth_router.post("/refresh", response=TokenOut)
def refresh_token(request, payload: RefreshIn):
    try:
        decoded = jwt.decode(payload.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        if decoded.get("type") != "refresh":
            raise HttpError(401, "Tipe token tidak valid")
        
        user_id = decoded.get("sub")
        return {
            "access_token": create_access_token(user_id),
            "refresh_token": create_refresh_token(user_id)
        }
    except Exception:
        raise HttpError(401, "Refresh token kadaluarsa atau tidak valid")

# Endpoint yang dilindungi JWTAuth()
@auth_router.get("/me", response=UserOut, auth=JWTAuth())
def get_me(request):
    return request.auth # request.auth diisi otomatis oleh middleware JWTAuth

@auth_router.put("/me", response=UserOut, auth=JWTAuth())
def update_me(request, payload: ProfileUpdateIn):
    user = request.auth
    user.first_name = payload.first_name
    user.last_name = payload.last_name
    user.email = payload.email
    user.save()
    return user