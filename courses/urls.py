from django.urls import path
from . import views

urlpatterns = [
    # Route Kasus 1
    path('lab/course-list/baseline/', views.course_list_baseline),
    path('lab/course-list/optimized/', views.course_list_optimized),
    
    # Route Kasus 2
    path('lab/course-members/baseline/', views.course_members_baseline),
    path('lab/course-members/optimized/', views.course_members_optimized),
    
    # Route Kasus 3
    path('lab/course-dashboard/baseline/', views.course_dashboard_baseline),
    path('lab/course-dashboard/optimized/', views.course_dashboard_optimized),
]