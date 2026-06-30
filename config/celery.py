import os
from celery import Celery

# Mengatur environment variabel untuk settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Membuat instance aplikasi Celery
app = Celery('config')

# Memuat konfigurasi dari settings.py Django (cari variabel berawalan CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Mencari file tasks.py di semua aplikasi Django secara otomatis
app.autodiscover_tasks()