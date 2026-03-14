FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (dibutuhkan cryptography & pymysql)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip dulu
RUN pip install --upgrade pip

# Install dependencies (copy requirements dulu agar layer cache efisien)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh project
COPY . .

# Railway inject $PORT secara otomatis saat runtime
# Gunakan shell form CMD agar $PORT bisa di-expand
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}