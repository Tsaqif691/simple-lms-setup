from django.contrib import admin
from .models import User, Category, Course, Lesson, Enrollment, Progress

# Mengatur tampilan Lesson agar bisa diinput langsung di dalam halaman Course
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1 # Jumlah form kosong yang muncul otomatis

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'created_at') # Kolom yang muncul di tabel
    list_filter = ('category', 'instructor') # Sidebar filter
    search_fields = ('title', 'description') # Kotak pencarian
    inlines = [LessonInline] # Memasukkan Lesson ke dalam Course

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ('parent',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course',)
    search_fields = ('student__username', 'course__title')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role',)

# Registrasi model lainnya secara standar
admin.site.register(Lesson)
admin.site.register(Progress)