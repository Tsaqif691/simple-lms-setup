from ninja import NinjaAPI
from courses.api_auth import auth_router
from courses.api_courses import course_router
from courses.api_enrollments import enrollment_router 
api = NinjaAPI(
    title="Simple LMS API",
    description="REST API untuk aplikasi Simple LMS dengan JWT dan RBAC",
    version="1.0.0"
)

@api.get("/ping", tags=["System"])
def ping(request):
    return {"message": "pong! Simple LMS API is alive and kicking"}

# Daftarkan semua router
api.add_router("/auth", auth_router)
api.add_router("/courses", course_router)
api.add_router("/enrollments", enrollment_router) 