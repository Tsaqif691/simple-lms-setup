from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from typing import List
from django.core.cache import cache
from .models import Course, Category
from .schemas import CourseOut, CourseIn
from config.security import JWTAuth, is_instructor, is_admin

course_router = Router(tags=["Courses"])

# 1. GET /api/courses
@course_router.get("/", response=List[CourseOut])
def list_courses(request):
    cached_courses = cache.get("course_list_all")
    if cached_courses:
        return cached_courses # Langsung lempar dari Redis!
    
    courses = list(Course.objects.select_related('instructor').all())
    cache.set("course_list_all", courses, 300) # Simpan 5 menit
    return courses

# 2. GET /api/courses/{id}
@course_router.get("/{course_id}", response=CourseOut)
def get_course(request, course_id: int):
    cache_key = f"course_detail_{course_id}"
    course = cache.get(cache_key)
    
    if not course:
        course = get_object_or_404(Course, id=course_id)
        cache.set(cache_key, course, 300) # Simpan 5 menit
        
    return course

# 3. POST /api/courses (Protected & RBAC - Hanya Instructor yang bisa buat)
@course_router.post("/", response=CourseOut, auth=JWTAuth())
@is_instructor
def create_course(request, payload: CourseIn):
    category = get_object_or_404(Category, id=payload.category_id)
    course = Course.objects.create(
        title=payload.title,
        description=payload.description,
        category=category,
        instructor=request.auth # request.auth berisi user yang sedang login
    )   
    # --- STRATEGI INVALIDASI CACHE ---
    cache.delete("course_list_all")
    return course

# 4. PATCH /api/courses/{id} (Protected - Hanya pemilik course yang bisa edit)
@course_router.patch("/{course_id}", response=CourseOut, auth=JWTAuth())
@is_instructor
def update_course(request, course_id: int, payload: CourseIn):
    course = get_object_or_404(Course, id=course_id)
    
    # Validasi Kepemilikan (Ownership)
    if course.instructor != request.auth:
        raise HttpError(403, "Anda bukan pemilik kursus ini")
        
    course.title = payload.title
    course.description = payload.description
    course.category = get_object_or_404(Category, id=payload.category_id)
    course.save()
    # --- STRATEGI INVALIDASI CACHE ---
    cache.delete("course_list_all")
    return course

# 5. DELETE /api/courses/{id} (Protected & RBAC - Hanya Admin yang bisa hapus)
@course_router.delete("/{course_id}", auth=JWTAuth())
@is_admin
def delete_course(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    # --- STRATEGI INVALIDASI CACHE ---
    cache.delete("course_list_all")
    return {"success": True, "message": "Kursus berhasil dihapus"}