from ninja import Router
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from typing import List
from .models import Course, Lesson 
from .schemas import CourseOut, EnrollIn
from config.security import JWTAuth, is_student

# ==========================================
# 1. IMPORT KEDUA TASK CELERY DI SINI
# ==========================================
from .tasks import send_enrollment_email, generate_certificate

enrollment_router = Router(tags=["Enrollments"])

# 1. POST /api/enrollments (Protected - Hanya Student yang bisa mendaftar)
@enrollment_router.post("/", auth=JWTAuth())
@is_student
def enroll_course(request, payload: EnrollIn):
    course = get_object_or_404(Course, id=payload.course_id)
    
    # Asumsi relasi ManyToMany bernama 'enrolled_students' pada model Course
    if request.auth in course.enrolled_students.all():
        raise HttpError(400, "Anda sudah terdaftar di kursus ini")
        
    course.enrolled_students.add(request.auth)
    
    # ==========================================
    # 2. TRIGGER TASK CELERY: KIRIM EMAIL (Background)
    # ==========================================
    # request.auth menyimpan data user yang sedang login, kita ambil email-nya
    send_enrollment_email.delay(request.auth.email, course.title)
    
    return {"success": True, "message": f"Berhasil mendaftar ke kursus: {course.title}"}

# 2. GET /api/enrollments/my-courses (Protected - Student melihat kursusnya)
@enrollment_router.get("/my-courses", response=List[CourseOut], auth=JWTAuth())
@is_student
def my_courses(request):
    # Mengambil semua kursus di mana user ini menjadi siswanya
    courses = Course.objects.filter(enrolled_students=request.auth)
    return courses

# 3. POST /api/enrollments/{id}/progress (Protected - Student menandai materi selesai)
@enrollment_router.post("/{lesson_id}/progress", auth=JWTAuth())
@is_student
def mark_progress(request, lesson_id: int):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Asumsi ada relasi ManyToMany 'completed_by' di model Lesson, atau logika sejenis
    # lesson.completed_by.add(request.auth)
    
    # ==========================================
    # 3. TRIGGER TASK CELERY: GENERATE SERTIFIKAT (Background)
    # ==========================================
    # (Untuk demonstrasi, kita asumsikan saat sebuah materi selesai, sertifikat langsung dibuat)
    # Kita butuh field 'course' dari Lesson untuk mengambil judul kursus (lesson.course.title)
    generate_certificate.delay(request.auth.username, lesson.course.title)
    
    return {"success": True, "message": f"Materi '{lesson.title}' berhasil ditandai selesai!"}