# GanaPortal Deployment Guide for Hostinger VPS

## 📋 Prerequisites

Before starting, you'll need:
- Hostinger VPS access (SSH credentials)
- A domain name pointed to your VPS IP
- About 30-45 minutes

---

## 🔑 Step 1: Connect to Your VPS

### On Windows:
1. Download and install [PuTTY](https://www.putty.org/)
2. Open PuTTY
3. Enter your VPS IP address in "Host Name"
4. Click "Open"
5. Login with username: `root` and your password

### On Mac/Linux:
Open Terminal and run:
```bash
ssh root@YOUR_VPS_IP
```

---

## 📦 Step 2: Install Required Software

Copy and paste these commands one by one:

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install PostgreSQL
apt install -y postgresql postgresql-contrib

# Install Redis
apt install -y redis-server

# Install Nginx
apt install -y nginx

# Install Git
apt install -y git

# Install Certbot for SSL
apt install -y certbot python3-certbot-nginx
```

---

## 🗄️ Step 3: Set Up Database

```bash
# Start PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

In the PostgreSQL prompt, type these commands (replace YOUR_PASSWORD with a strong password):
```sql
CREATE DATABASE ganaportal;
CREATE USER ganaportal_user WITH ENCRYPTED PASSWORD 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE ganaportal TO ganaportal_user;
ALTER DATABASE ganaportal OWNER TO ganaportal_user;
\q
```

---

## 🔴 Step 4: Set Up Redis

```bash
# Start Redis
systemctl start redis-server
systemctl enable redis-server

# Verify Redis is running
redis-cli ping
# Should respond: PONG
```

---

## 📥 Step 5: Clone Your Project

```bash
# Create app directory
mkdir -p /var/www
cd /var/www

# Clone repository (replace with your actual repo URL)
git clone https://github.com/YOUR_USERNAME/GanakysPortal.git
cd GanakysPortal
```

---

## ⚙️ Step 6: Configure Backend

```bash
# Go to backend directory
cd /var/www/GanakysPortal/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
nano .env
```

Paste this content in the .env file (press Ctrl+O to save, Ctrl+X to exit):
```env
# Application
APP_NAME=GanaPortal
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Security - GENERATE NEW KEYS!
# Run: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=PASTE_YOUR_GENERATED_KEY_HERE
ENCRYPTION_KEY=PASTE_YOUR_GENERATED_KEY_HERE

# Database
DATABASE_URL=postgresql+asyncpg://ganaportal_user:YOUR_PASSWORD@localhost:5432/ganaportal

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS - Replace with your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email (Optional - for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

### Generate Secure Keys:
```bash
# Run this twice to generate two different keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy each output and paste into SECRET_KEY and ENCRYPTION_KEY in the .env file.

---

## 🗃️ Step 7: Run Database Migrations

```bash
cd /var/www/GanakysPortal/backend
source venv/bin/activate

# Run migrations
alembic upgrade head

# If you have existing data to encrypt:
# python scripts/migrate_encrypt_pii.py --dry-run
# python scripts/migrate_encrypt_pii.py
```

---

## 🖥️ Step 8: Configure Frontend

```bash
cd /var/www/GanakysPortal/frontend

# Install dependencies
npm install

# Create environment file
nano .env.local
```

Paste this content:
```env
NEXT_PUBLIC_API_URL=https://yourdomain.com/api/v1
```

Build the frontend:
```bash
npm run build
```

---

## 🔧 Step 9: Create System Services

### Backend Service:
```bash
nano /etc/systemd/system/ganaportal-backend.service
```

Paste this content:
```ini
[Unit]
Description=GanaPortal Backend API
After=network.target postgresql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/GanakysPortal/backend
Environment="PATH=/var/www/GanakysPortal/backend/venv/bin"
ExecStart=/var/www/GanakysPortal/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Frontend Service:
```bash
nano /etc/systemd/system/ganaportal-frontend.service
```

Paste this content:
```ini
[Unit]
Description=GanaPortal Frontend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/GanakysPortal/frontend
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=5
Environment=NODE_ENV=production
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
```

### Set permissions and start services:
```bash
# Set ownership
chown -R www-data:www-data /var/www/GanakysPortal

# Reload systemd
systemctl daemon-reload

# Start services
systemctl start ganaportal-backend
systemctl start ganaportal-frontend

# Enable auto-start on boot
systemctl enable ganaportal-backend
systemctl enable ganaportal-frontend

# Check status
systemctl status ganaportal-backend
systemctl status ganaportal-frontend
```

---

## 🌐 Step 10: Configure Nginx

```bash
nano /etc/nginx/sites-available/ganaportal
```

Paste this content (replace `yourdomain.com` with your actual domain):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;

        # Increase timeout for long requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # File upload limit
    client_max_body_size 50M;
}
```

Enable the site:
```bash
# Create symbolic link
ln -s /etc/nginx/sites-available/ganaportal /etc/nginx/sites-enabled/

# Remove default site
rm /etc/nginx/sites-enabled/default

# Test configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

---

## 🔒 Step 11: Set Up SSL (HTTPS)

```bash
# Get SSL certificate (replace with your domain)
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts:
1. Enter your email
2. Agree to terms (Y)
3. Choose whether to share email (your choice)
4. Select option 2 to redirect HTTP to HTTPS

---

## ✅ Step 12: Verify Deployment

1. Open your browser and go to: `https://yourdomain.com`
2. You should see the GanaPortal login page
3. Check the API: `https://yourdomain.com/api/v1/`

---

## 🔍 Troubleshooting

### Check service logs:
```bash
# Backend logs
journalctl -u ganaportal-backend -f

# Frontend logs
journalctl -u ganaportal-frontend -f

# Nginx logs
tail -f /var/log/nginx/error.log
```

### Restart services:
```bash
systemctl restart ganaportal-backend
systemctl restart ganaportal-frontend
systemctl restart nginx
```

### Check if services are running:
```bash
systemctl status ganaportal-backend
systemctl status ganaportal-frontend
systemctl status nginx
systemctl status postgresql
systemctl status redis-server
```

---

## 🔄 Updating the Application

When you need to update:
```bash
cd /var/www/GanakysPortal

# Pull latest changes
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Update frontend
cd ../frontend
npm install
npm run build

# Restart services
systemctl restart ganaportal-backend
systemctl restart ganaportal-frontend
```

---

## 📞 Support

If you encounter issues:
1. Check the logs (see Troubleshooting section)
2. Make sure all services are running
3. Verify your domain DNS is pointing to your VPS IP

---

*Document created: 2024-12-15*
*GanaPortal v1.0.0*
