# 🚀 English AI Agent - Production Deployment Guide

This guide covers deploying the English AI Agent application to production servers.

## 📋 Table of Contents
1. [Server Requirements](#server-requirements)
2. [Quick Deployment](#quick-deployment)
3. [Manual Setup](#manual-setup)
4. [Docker Deployment](#docker-deployment)
5. [Security & SSL](#security--ssl)
6. [Monitoring](#monitoring)

## 🖥️ Server Requirements

### Minimum Specifications
- **CPU**: 2 cores (4 cores recommended)
- **RAM**: 4GB (8GB recommended)  
- **Storage**: 20GB SSD (50GB recommended)
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Amazon Linux 2

### Recommended Cloud Providers
- **AWS**: EC2 t3.medium or larger
- **DigitalOcean**: Droplet $20/month or larger
- **Google Cloud**: e2-standard-2 or larger
- **Azure**: Standard B2s or larger

## 🚀 Quick Deployment

### 1. Prepare Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx git curl

# Install PM2 for process management
sudo npm install -g pm2
```

### 2. Setup Application
```bash
# Create application directory
sudo mkdir -p /opt/english-ai-agent
sudo chown $USER:$USER /opt/english-ai-agent
cd /opt/english-ai-agent

# Clone repository (replace with your repo URL)
git clone https://github.com/your-username/english-ai-agent.git .

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Setup frontend
cd ../frontend
npm install
npm run build
```

### 3. Configure Environment
```bash
# Create production environment file
cp backend/env.example .env.production

# Edit with your production values
nano .env.production
```

Add your production values:
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_production_access_key
AWS_SECRET_ACCESS_KEY=your_production_secret_key

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_production_elevenlabs_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_very_secure_secret_key_here

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

### 4. Create Production Scripts
```bash
# Create start script
cat > backend/start-production.sh << 'EOF'
#!/bin/bash
cd /opt/english-ai-agent/backend
source venv/bin/activate
export $(cat ../.env.production | grep -v '^#' | xargs)
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
EOF

chmod +x backend/start-production.sh

# Create PM2 configuration
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'english-ai-backend',
    script: '/opt/english-ai-agent/backend/start-production.sh',
    cwd: '/opt/english-ai-agent/backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    error_file: '/opt/english-ai-agent/logs/backend-error.log',
    out_file: '/opt/english-ai-agent/logs/backend-out.log',
    log_file: '/opt/english-ai-agent/logs/backend.log',
    time: true
  }]
};
EOF

# Create logs directory
mkdir -p logs
```

### 5. Configure Nginx
```bash
# Create nginx configuration
sudo tee /etc/nginx/sites-available/english-ai-agent << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend (React App)
    location / {
        root /opt/english-ai-agent/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for AI responses
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # File upload limits
    client_max_body_size 10M;
}
EOF

# Replace 'your-domain.com' with your actual domain
sudo sed -i 's/your-domain.com/YOUR_ACTUAL_DOMAIN/g' /etc/nginx/sites-available/english-ai-agent

# Enable site
sudo ln -s /etc/nginx/sites-available/english-ai-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Start Application
```bash
# Start backend with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the instructions shown by PM2
```

## 🔒 Security & SSL

### 1. Setup SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### 2. Configure Firewall
```bash
# Enable UFW firewall
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw status
```

### 3. Security Headers (automatic with Certbot)
After SSL setup, your nginx config will include security headers automatically.

## 🐳 Docker Deployment (Alternative)

### 1. Create Dockerfiles

Backend Dockerfile (`backend/Dockerfile`):
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

Frontend Dockerfile (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2. Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: english-ai-backend
    restart: unless-stopped
    env_file: .env.production
    ports:
      - "5000:5000"
    volumes:
      - ./logs:/app/logs

  frontend:
    build: ./frontend
    container_name: english-ai-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  logs:
```

### 3. Deploy with Docker
```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## 📊 Monitoring

### 1. Check Application Status
```bash
# PM2 status
pm2 status
pm2 logs english-ai-backend

# Nginx status
sudo systemctl status nginx

# Check processes
ps aux | grep gunicorn
```

### 2. Health Monitoring
```bash
# Test API health
curl https://your-domain.com/api/health

# Check SSL certificate
sudo certbot certificates

# Monitor resources
htop
df -h
```

### 3. Log Monitoring
```bash
# Application logs
tail -f /opt/english-ai-agent/logs/backend.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u nginx -f
```

## 🔧 Maintenance

### 1. Update Application
```bash
# Create update script
cat > /opt/english-ai-agent/update.sh << 'EOF'
#!/bin/bash
cd /opt/english-ai-agent

# Pull latest changes
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend
cd ../frontend
npm install
npm run build

# Restart services
pm2 restart english-ai-backend
sudo systemctl reload nginx

echo "Application updated successfully!"
EOF

chmod +x /opt/english-ai-agent/update.sh

# Run updates
./update.sh
```

### 2. Backup Script
```bash
# Create backup script
cat > /opt/english-ai-agent/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/english-ai-agent"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup application
tar -czf $BACKUP_DIR/app_$DATE.tar.gz \
    -C /opt/english-ai-agent \
    --exclude=node_modules \
    --exclude=venv \
    --exclude=logs \
    .

# Backup environment
cp /opt/english-ai-agent/.env.production $BACKUP_DIR/env_$DATE

# Keep only last 7 backups
find $BACKUP_DIR -name "app_*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "env_*" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/app_$DATE.tar.gz"
EOF

chmod +x /opt/english-ai-agent/backup.sh
```

### 3. Automated Tasks
```bash
# Setup cron jobs
crontab -e

# Add these lines:
# Daily backup at 2 AM
0 2 * * * /opt/english-ai-agent/backup.sh

# Weekly SSL renewal check
0 3 * * 1 sudo certbot renew --quiet

# Monthly restart (first Sunday at 4 AM)
0 4 1-7 * 0 pm2 restart all
```

## 🆘 Troubleshooting

### Common Issues

1. **500 Error**: Check backend logs with `pm2 logs`
2. **SSL Issues**: Run `sudo certbot renew`
3. **Memory Issues**: Restart with `pm2 restart all`
4. **Port Conflicts**: Check with `sudo netstat -tulpn | grep :5000`
5. **Permission Issues**: Check file ownership with `ls -la`

### Emergency Commands
```bash
# Quick restart everything
pm2 restart all && sudo systemctl restart nginx

# Check if ports are available
sudo netstat -tulpn | grep -E ':80|:443|:5000'

# Check disk space
df -h

# Check memory usage
free -h
```

## 🎯 Domain Configuration

Before deployment, make sure your domain DNS points to your server:

```
A Record: yourdomain.com -> YOUR_SERVER_IP
A Record: www.yourdomain.com -> YOUR_SERVER_IP
```

## ✅ Final Checklist

- [ ] Server meets minimum requirements
- [ ] Domain DNS configured
- [ ] Application cloned and built
- [ ] Production environment configured
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Application running with PM2
- [ ] Nginx proxy configured
- [ ] Health check working
- [ ] Backup script created
- [ ] Monitoring setup

Your English AI Agent should now be running in production! 🎉 