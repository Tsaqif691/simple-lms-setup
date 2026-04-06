from django.db import models
from django.contrib.auth.models import AbstractUser

class CourseQuerySet(models.QuerySet):
    def for_listing(self):
        # Menggunakan select_related karena instructor dan category adalah ForeignKey
        # Ini akan menggabungkan (JOIN) tabel dalam satu query SQL saja
        return self.select_related('instructor', 'category').only(
            'title', 'instructor__username', 'category__name', 'created_at'
        )

class EnrollmentQuerySet(models.QuerySet):
    def for_student_dashboard(self):
        # Menggunakan prefetch_related karena lesson_progress adalah relasi balik (reverse lookup)
        # Ini akan melakukan 2 query efektif dan menggabungkannya di level Python
        return self.prefetch_related('lesson_progress', 'course__lessons')

# 1. Custom User Model (Sudah kita buat sebelumnya, tetap di sini)
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"

# 2. Category Model (Self-referencing untuk Hierarchy)
class Category(models.Model):
    name = models.CharField(max_length=100)
    # 'self' artinya kategori bisa punya parent yang juga seorang kategori
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name

# 3. Course Model
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'}, related_name='courses_taught')
    created_at = models.DateTimeField(auto_now_add=True)
    objects = CourseQuerySet.as_manager()

    def __str__(self):
        return self.title

# 4. Lesson Model (dengan Ordering)
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order'] # Menjamin lesson muncul berurutan berdasarkan field 'order'

    def __str__(self):
        return f"{self.course.title} - {self.title}"

# 5. Enrollment Model (dengan Unique Constraint)
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    objects = EnrollmentQuerySet.as_manager()

    class Meta:
        # Mencegah satu student mendaftar ke course yang sama lebih dari sekali
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

# 6. Progress Model (Tracking lesson completion)
class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.enrollment.student.username} - {self.lesson.title} [{status}]"