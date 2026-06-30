from django.core.cache import cache
from django.http import JsonResponse

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Satpam ini hanya mengecek jalur /api/
        if request.path.startswith('/api/'):
            # Ambil IP Address user
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            cache_key = f"rate_limit_{ip}"
            
            # Cek sudah berapa kali IP ini mengakses API
            req_count = cache.get(cache_key, 0)
            
            if req_count >= 60:
                return JsonResponse({"detail": "Too Many Requests. Limit 60/menit."}, status=429)
                
            if req_count == 0:
                cache.set(cache_key, 1, 60) # Beri waktu 60 detik
            else:
                cache.incr(cache_key) # Tambah hitungan
                
        return self.get_response(request)