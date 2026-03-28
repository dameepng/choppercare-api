# Deploy ke VPS

## Requirement sistem

- Ubuntu/Debian server
- Python 3.11+ dengan `python3-venv`
- Node.js 20+ atau 22 LTS
- PM2
- PostgreSQL dengan extension `pgvector`
- Outbound internet untuk download package Python dan model Hugging Face saat pertama kali load

Contoh install dasar:

```bash
sudo apt update
sudo apt install -y git curl python3 python3-venv python3-pip build-essential
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2
```

Untuk PostgreSQL dan `pgvector`, nama paket extension bisa beda per distro/versi PostgreSQL. Pastikan database Anda bisa menjalankan:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Deploy aplikasi

Clone repo ke VPS:

```bash
cd /var/www
git clone https://github.com/dameepng/choppercare-api.git
cd choppercare-api
```

Siapkan env:

```bash
cp .env.example .env
nano .env
```

Minimal isi yang wajib benar:

- `GROQ_API_KEY`
- `DATABASE_URL`
- `ALLOWED_ORIGINS`

Jalankan deploy:

```bash
chmod +x deploy.sh
./deploy.sh
```

Kalau mau ingest dokumen BNPB setelah deploy:

```bash
RUN_INGEST=1 ./deploy.sh
```

API berjalan di port `8001` via PM2.

## Update berikutnya

```bash
cd /var/www/choppercare-api
./deploy.sh
```

## Nginx reverse proxy

Kalau frontend dan API pakai domain yang sama, proxy `/api/` dan `/health` ke backend:

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    chunked_transfer_encoding off;
}

location /health {
    proxy_pass http://127.0.0.1:8001;
    proxy_set_header Host $host;
}
```
