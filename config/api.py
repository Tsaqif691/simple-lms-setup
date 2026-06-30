from ninja import NinjaAPI
from courses.api_auth import auth_router
from courses.api_courses import course_router
from courses.api_enrollments import enrollment_router 

# --- TAMBAHKAN IMPORT INI ---
from courses.tasks import export_course_report
# ----------------------------

api = NinjaAPI(
    title="Simple LMS API",
    description="REST API untuk aplikasi Simple LMS dengan JWT dan RBAC",
    version="1.0.0"
)

@api.get("/ping", tags=["System"])
def ping(request):
    return {"message": "pong! Simple LMS API is alive and kicking"}

# --- TAMBAHKAN ENDPOINT INI UNTUK CELERY ---
@api.post("/export-report", tags=["System"])
def trigger_export_report(request):
    # Memanggil tugas Celery untuk dikerjakan di background (menggunakan .delay())
    export_course_report.delay()
    return {"message": "Proses ekspor CSV sedang berjalan di latar belakang (Celery). File akan segera tersedia."}
# ------------------------------------------

# Daftarkan semua router
api.add_router("/auth", auth_router)
api.add_router("/courses", course_router)
api.add_router("/enrollments", enrollment_router)