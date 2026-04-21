from django.http import JsonResponse
from django.db.models import Count
from .models import Course, Enrollment, Lesson

# ==========================================
# KASUS 1: Course + Teacher (select_related)
# ==========================================
def course_list_baseline(request):
    courses = Course.objects.all()
    data = []
    for c in courses:
        data.append({
            'course': c.title,
            'teacher': c.instructor.username # Ini memicu N+1 Problem
        })
    return JsonResponse({'data': data})

def course_list_optimized(request):
    courses = Course.objects.select_related('instructor').all()
    data = []
    for c in courses:
        data.append({
            'course': c.title,
            'teacher': c.instructor.username
        })
    return JsonResponse({'data': data})

# ==========================================
# KASUS 2: Course + Members + Konten (prefetch_related)
# ==========================================
def course_members_baseline(request):
    courses = Course.objects.all()
    data = []
    for c in courses:
        data.append({
            'course': c.title,
            'member_count': c.enrolled_students.count(), # Memicu N+1
            'lesson_count': c.lessons.count() # Memicu N+1
        })
    return JsonResponse({'data': data})

def course_members_optimized(request):
    # Menggunakan prefetch_related & annotate agar jauh lebih cepat
    courses = Course.objects.prefetch_related('enrolled_students', 'lessons').annotate(
        member_count=Count('enrolled_students', distinct=True),
        lesson_count=Count('lessons', distinct=True)
    )
    data = []
    for c in courses:
        data.append({
            'course': c.title,
            'member_count': c.member_count,
            'lesson_count': c.lesson_count
        })
    return JsonResponse({'data': data})

# ==========================================
# KASUS 3: Dashboard Statistik (aggregate)
# ==========================================
def course_dashboard_baseline(request):
    courses = Course.objects.all()
    total_courses = 0
    total_lessons = 0
    for c in courses:
        total_courses += 1
        total_lessons += c.lessons.count() # Sangat tidak efisien di dalam loop
        
    return JsonResponse({
        'total_courses': total_courses,
        'total_lessons': total_lessons
    })

def course_dashboard_optimized(request):
    stats = Course.objects.aggregate(
        total_courses=Count('id', distinct=True),
        total_lessons=Count('lessons')
    )
    return JsonResponse(stats)