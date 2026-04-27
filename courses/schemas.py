from ninja import Schema
from pydantic import EmailStr
from typing import List, Optional

# --- SKEMA OUTPUT ---
class UserOut(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str

class TokenOut(Schema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# --- SKEMA INPUT ---
class RegisterIn(Schema):
    username: str
    email: EmailStr  
    password: str
    first_name: str = ""
    last_name: str = ""

class LoginIn(Schema):
    username: str
    password: str

class ProfileUpdateIn(Schema):
    first_name: str
    last_name: str
    email: EmailStr  

class CourseOut(Schema):
    id: int
    title: str
    description: str
    # Mengambil nama instruktur dari relasi database
    instructor_name: str = None

    @staticmethod
    def resolve_instructor_name(obj):
        return obj.instructor.username if obj.instructor else "Unknown"

class CourseIn(Schema):
    title: str
    description: str
    category_id: int

class EnrollIn(Schema):
    course_id: int