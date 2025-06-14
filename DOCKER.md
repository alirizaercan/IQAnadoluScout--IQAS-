# TYFOR Docker Setup

Bu dosya TYFOR projesini Docker ile çalıştırmak için gerekli talimatları içerir.

## Gereksinimler

- Docker
- Docker Compose

## Hızlı Başlangıç

### Production Ortamı

```bash
# Projeyi klonlayın
git clone <repository-url>
cd TYFOR

# Uygulamayı build edin ve çalıştırın
docker-compose up --build

# Arka planda çalıştırmak için
docker-compose up -d --build
```

Uygulama `http://localhost:5056` adresinde çalışacaktır.

### Development Ortamı

```bash
# Development ortamı için
docker-compose -f docker-compose.dev.yml up --build

# Arka planda çalıştırmak için
docker-compose -f docker-compose.dev.yml up -d --build
```

Development ortamında:
- Backend: `http://localhost:5056`
- Frontend: `http://localhost:3000` (hot reload ile)

## Ortam Değişkenleri

Aşağıdaki ortam değişkenlerini `.env` dosyasında tanımlayabilirsiniz:

```env
# Database
DATABASE_URL=postgresql://tyfor_user:tyfor_password@db:5432/tyfor_db

# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Development için
FLASK_DEBUG=1
```

## Docker Komutları

### Build ve Run

```bash
# Sadece build
docker-compose build

# Run (build olmadan)
docker-compose up

# Arka planda run
docker-compose up -d

# Logları görüntüleme
docker-compose logs -f

# Belirli bir service'in logları
docker-compose logs -f app
docker-compose logs -f db
```

### Cleanup

```bash
# Container'ları durdur
docker-compose down

# Volume'ları da sil
docker-compose down -v

# Image'ları da sil
docker-compose down --rmi all

# Tüm Docker sistemini temizle
docker system prune -a
```

### Database

```bash
# Database container'ına bağlan
docker-compose exec db psql -U tyfor_user -d tyfor_db

# Database backup
docker-compose exec db pg_dump -U tyfor_user tyfor_db > backup.sql

# Database restore
docker-compose exec -T db psql -U tyfor_user -d tyfor_db < backup.sql
```

### Development

```bash
# Backend container'ına bağlan
docker-compose exec app bash

# Python shell
docker-compose exec app python

# Dependencies yükle
docker-compose exec app pip install new-package

# Frontend container'ında komut çalıştır
docker-compose exec app bash -c "cd frontend && npm install new-package"
```

## Volumes

Proje aşağıdaki volume'ları kullanır:

- `postgres_data`: PostgreSQL veritabanı verileri
- `./backend/uploads`: Yüklenen dosyalar
- `./backend/static/graphs`: Üretilen grafikler
- `./data`: Veri dosyaları

## Ports

- **5056**: Flask backend
- **3000**: React frontend (sadece development)
- **5432**: PostgreSQL database

## Troubleshooting

### Port Çakışması

Eğer portlar kullanımda ise, `docker-compose.yml` dosyasında port mapping'leri değiştirin:

```yaml
ports:
  - "8080:5056"  # 5056 yerine 8080 kullan
```

### Volume İzinleri

Linux/Mac'te volume izin sorunları yaşarsanız:

```bash
sudo chown -R $USER:$USER ./backend/uploads
sudo chown -R $USER:$USER ./backend/static/graphs
```

### Database Bağlantı Sorunu

Database'in hazır olmasını bekleyin:

```bash
docker-compose logs db
```

### Memory Sorunu

Eğer build sırasında memory hatası alırsanız, Docker'a daha fazla memory verin:

- Docker Desktop > Settings > Resources > Memory

## Production Deployment

Production'da deploy ederken:

1. `.env` dosyasında güvenli SECRET_KEY kullanın
2. Database şifrelerini değiştirin
3. SSL sertifikası ekleyin
4. Reverse proxy (nginx) kullanın

Örnek nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5056;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
