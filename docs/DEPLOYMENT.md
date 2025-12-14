# GanaPortal Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [SSL Certificate Setup](#ssl-certificate-setup)
5. [Database Setup](#database-setup)
6. [Monitoring](#monitoring)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Server Requirements
- **OS**: Ubuntu 22.04 LTS or later
- **CPU**: 4 cores minimum (8 recommended)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 100GB SSD minimum
- **Network**: Public IP with ports 80, 443 open

### Software Requirements
- Docker 24.0+
- Docker Compose 2.20+
- Git
- Nginx (for SSL termination)

### Install Docker
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

---

## Environment Setup

### 1. Clone Repository
```bash
cd /opt
sudo git clone https://github.com/ganakys/ganaportal.git
sudo chown -R $USER:$USER ganaportal
cd ganaportal
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_USER` | PostgreSQL username | `ganaportal` |
| `DB_PASSWORD` | PostgreSQL password | `SecureP@ssw0rd!` |
| `DB_NAME` | Database name | `ganaportal` |
| `REDIS_PASSWORD` | Redis password | `RedisP@ssw0rd!` |
| `SECRET_KEY` | JWT signing key (32+ chars) | `openssl rand -hex 32` |
| `ENCRYPTION_KEY` | Data encryption key | `openssl rand -hex 32` |
| `CORS_ORIGINS` | Allowed origins | `https://ganaportal.com` |

### Generate Secure Keys
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY
openssl rand -hex 32
```

---

## Docker Deployment

### 1. Build Images
```bash
# Build all services
docker compose build

# Or build specific service
docker compose build backend
docker compose build frontend
```

### 2. Start Services
```bash
# Start all services in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Check service status
docker compose ps
```

### 3. Verify Deployment
```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check database connection
docker compose exec backend python -c "from app.db.session import engine; print('DB OK')"
```

### Service Ports
| Service | Internal Port | External Port |
|---------|--------------|---------------|
| Frontend | 3000 | - |
| Backend | 8000 | - |
| PostgreSQL | 5432 | - |
| Redis | 6379 | - |
| Nginx | 80, 443 | 80, 443 |

---

## SSL Certificate Setup

### Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d ganaportal.com -d www.ganaportal.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/ganaportal.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/ganaportal.com/privkey.pem nginx/ssl/

# Set permissions
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem
```

### Auto-Renewal Setup
```bash
# Add to crontab
sudo crontab -e

# Add this line (renews at 2:30 AM daily)
30 2 * * * certbot renew --quiet --post-hook "docker compose restart nginx"
```

---

## Database Setup

### Initial Setup
```bash
# Run database migrations
docker compose exec backend alembic upgrade head

# Create superadmin user
docker compose exec backend python -m app.scripts.create_superadmin
```

### Database Backup
```bash
# Manual backup
docker compose exec db pg_dump -U ganaportal ganaportal > backup_$(date +%Y%m%d).sql

# Compressed backup
docker compose exec db pg_dump -U ganaportal ganaportal | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Database Restore
```bash
# Stop application services
docker compose stop backend celery-worker celery-beat

# Restore from backup
docker compose exec -T db psql -U ganaportal -d ganaportal < backup.sql

# Restart services
docker compose start backend celery-worker celery-beat
```

### Automated Backup Script
```bash
#!/bin/bash
# /opt/ganaportal/scripts/backup.sh

BACKUP_DIR="/opt/backups/ganaportal"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup
docker compose exec -T db pg_dump -U ganaportal ganaportal | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Remove old backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Optional: Upload to S3
# aws s3 cp "$BACKUP_DIR/db_$TIMESTAMP.sql.gz" s3://your-bucket/backups/
```

---

## Monitoring

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f nginx

# Last 100 lines
docker compose logs --tail=100 backend
```

### Resource Monitoring
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -af
```

### Health Checks
```bash
# Backend health
curl -s http://localhost:8000/health | jq

# Database health
docker compose exec db pg_isready -U ganaportal

# Redis health
docker compose exec redis redis-cli ping
```

### Log Rotation
Create `/etc/logrotate.d/ganaportal`:
```
/opt/ganaportal/nginx/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 www-data www-data
    postrotate
        docker compose exec nginx nginx -s reopen
    endscript
}
```

---

## Backup & Recovery

### Full System Backup
```bash
#!/bin/bash
# Full backup script

BACKUP_DIR="/opt/backups/ganaportal"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup
docker compose exec -T db pg_dump -U ganaportal ganaportal | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Redis backup
docker compose exec redis redis-cli BGSAVE
docker cp ganaportal-redis:/data/dump.rdb "$BACKUP_DIR/redis_$TIMESTAMP.rdb"

# Upload files backup
tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" /opt/ganaportal/uploads

echo "Backup completed: $TIMESTAMP"
```

### Disaster Recovery
1. Restore database from backup
2. Restore Redis dump
3. Restore uploaded files
4. Run migrations: `docker compose exec backend alembic upgrade head`
5. Verify application health

---

## Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
docker compose logs backend

# Common fixes:
# 1. Database not ready - wait and restart
docker compose restart backend

# 2. Migration issues
docker compose exec backend alembic upgrade head
```

#### Database Connection Issues
```bash
# Verify database is running
docker compose ps db

# Check connectivity
docker compose exec backend python -c "
from app.db.session import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database OK')
"
```

#### Out of Memory
```bash
# Check memory usage
docker stats --no-stream

# Increase swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### SSL Certificate Issues
```bash
# Test SSL
openssl s_client -connect ganaportal.com:443 -servername ganaportal.com

# Check certificate expiry
openssl x509 -enddate -noout -in /etc/letsencrypt/live/ganaportal.com/fullchain.pem
```

### Useful Commands
```bash
# Restart all services
docker compose restart

# Rebuild and restart specific service
docker compose up -d --build backend

# Shell into container
docker compose exec backend bash

# View real-time logs
docker compose logs -f --tail=100

# Check container resource usage
docker stats ganaportal-backend ganaportal-frontend ganaportal-db
```

---

## Updates & Maintenance

### Updating Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose build
docker compose up -d

# Run new migrations
docker compose exec backend alembic upgrade head
```

### Scaling Services
```bash
# Scale Celery workers
docker compose up -d --scale celery-worker=3

# Scale backend (requires load balancer config)
docker compose up -d --scale backend=2
```

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS certificates
- [ ] Configure firewall (UFW)
- [ ] Set up fail2ban
- [ ] Enable automatic security updates
- [ ] Configure backup rotation
- [ ] Set up monitoring alerts
- [ ] Review CORS settings
- [ ] Enable rate limiting
- [ ] Configure log retention

---

## Support

For technical support, contact:
- Email: support@ganakys.com
- Documentation: https://docs.ganaportal.com
