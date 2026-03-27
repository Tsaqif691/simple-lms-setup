# Menggunakan base image Python versi 3.11 yang ringan
FROM python:3.11-slim

# Menentukan folder kerja di dalam container Docker
WORKDIR /app

# Menginstal dependensi sistem yang dibutuhkan agar bisa nyambung ke PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Menyalin daftar belanjaan (requirements) ke dalam container
COPY requirements.txt .

# Mengeksekusi instalasi Django dan Psycopg2
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh sisa file dari komputermu ke dalam container
COPY . .

# Membuka port 8000
EXPOSE 8000