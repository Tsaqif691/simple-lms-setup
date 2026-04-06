import os
import django
from django.db import connection, reset_queries

# 1. Setup environment Django agar script ini bisa berjalan mandiri
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Course

def demo_optimization():
    # Pastikan ada data di database
    if not Course.objects.exists():
        print("Data Course masih kosong! Silakan isi data di Admin terlebih dahulu.")
        return

    # A. DEMO N+1 PROBLEM (CARA BIASA)
    print("--- [1] MENGGUNAKAN QUERY STANDAR (N+1 Problem) ---")
    reset_queries()
    
    # Mengambil semua course tanpa optimasi
    courses_biasa = Course.objects.all()
    for c in courses_biasa:
        # Setiap kali memanggil .instructor atau .category, 
        # Django dipaksa melakukan query baru ke database (N+1)
        print(f"Course: {c.title} | Instructor: {c.instructor.username} | Category: {c.category.name}")
    
    query_count_biasa = len(connection.queries)
    print(f"Total Query yang dikirim ke Database: {query_count_biasa}\n")

    # B. DEMO OPTIMIZED QUERY (MENGGUNAKAN SELECT_RELATED)
    print("--- [2] MENGGUNAKAN OPTIMIZED QUERY (select_related) ---")
    reset_queries()
    
    # Memanggil model manager 'for_listing' yang sudah kita buat di models.py
    # Manager ini sudah menggunakan .select_related('instructor', 'category')
    courses_optimal = Course.objects.for_listing()
    for c in courses_optimal:
        # Data instructor dan category sudah terambil di awal (JOIN), tidak ada query tambahan
        print(f"Course: {c.title} | Instructor: {c.instructor.username} | Category: {c.category.name}")
    
    query_count_optimal = len(connection.queries)
    print(f"Total Query yang dikirim ke Database: {query_count_optimal}")
    
    # Hasil Perbandingan
    print("\n" + "="*50)
    print(f"ANALISIS: Dengan {courses_biasa.count()} data Course:")
    print(f"- Cara Biasa membutuhkan {query_count_biasa} query.")
    print(f"- Cara Optimal HANYA membutuhkan {query_count_optimal} query.")
    print(f"KESIMPULAN: Kamu berhasil menghemat {query_count_biasa - query_count_optimal} query!")
    print("="*50)

if __name__ == "__main__":
    demo_optimization()