#!/bin/bash

# English AI Agent - Production Deployment Script
# This script automates the deployment process

set -e

echo "🚀 Starting English AI Agent deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
print_status "Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx git curl htop ufw

# Install PM2
print_status "Installing PM2..."
sudo npm install -g pm2

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p /opt/english-ai-agent
sudo chown $USER:$USER /opt/english-ai-agent

# Check if git repository exists
if [ ! -d "/opt/english-ai-agent/.git" ]; then
    print_status "Cloning repository..."
    echo "Please enter your repository URL:"
    read -r REPO_URL
    cd /opt/english-ai-agent
    git clone "$REPO_URL" .
else
    print_status "Repository already exists, pulling latest changes..."
    cd /opt/english-ai-agent
    git pull origin main
fi

# Setup backend
print_status "Setting up backend..."
cd /opt/english-ai-agent/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Setup frontend
print_status "Setting up frontend..."
cd /opt/english-ai-agent/frontend
npm install
npm run build

# Create production environment file
cd /opt/english-ai-agent
if [ ! -f ".env.production" ]; then
    print_status "Creating production environment file..."
    cp backend/env.example .env.production
    print_warning "Please edit .env.production with your production values"
    print_warning "Required: AWS credentials, ElevenLabs API key, and secure secret key"
    read -p "Press enter to edit the environment file..."
    nano .env.production
fi

# Create start script
print_status "Creating production scripts..."
cat > backend/start-production.sh << 'EOF'
#!/bin/bash
cd /opt/english-ai-agent/backend
source venv/bin/activate
export $(cat ../.env.production | grep -v '^#' | xargs)
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
EOF

chmod +x backend/start-production.sh

# Create logs directory
mkdir -p logs

# Configure nginx
print_status "Configuring nginx..."
echo "Please enter your domain name (e.g., example.com):"
read -r DOMAIN_NAME

sudo tee /etc/nginx/sites-available/english-ai-agent << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

    # Frontend (React App)
    location / {
        root /opt/english-ai-agent/frontend/build;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)\$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Increase timeout for AI responses
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # File upload limits
    client_max_body_size 10M;
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/english-ai-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Configure firewall
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Start application with PM2
print_status "Starting application..."
pm2 start ecosystem.config.js
pm2 save
pm2 startup

# Setup SSL
print_status "Setting up SSL certificate..."
echo "Do you want to setup SSL with Let's Encrypt? (y/n)"
read -r setup_ssl

if [[ $setup_ssl == "y" || $setup_ssl == "Y" ]]; then
    sudo apt install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d "$DOMAIN_NAME" -d "www.$DOMAIN_NAME"
    
    # Test auto-renewal
    sudo certbot renew --dry-run
fi

# Create maintenance scripts
print_status "Creating maintenance scripts..."

# Update script
cat > update.sh << 'EOF'
#!/bin/bash
cd /opt/english-ai-agent

echo "🔄 Updating English AI Agent..."

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

echo "✅ Update completed successfully!"
EOF

chmod +x update.sh

# Backup script
cat > backup.sh << 'EOF'
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

echo "✅ Backup completed: $BACKUP_DIR/app_$DATE.tar.gz"
EOF

chmod +x backup.sh

print_status "🎉 Deployment completed successfully!"
print_status "Your English AI Agent is now running on:"
print_status "  - HTTP: http://$DOMAIN_NAME"
if [[ $setup_ssl == "y" || $setup_ssl == "Y" ]]; then
    print_status "  - HTTPS: https://$DOMAIN_NAME"
fi

print_status ""
print_status "📋 Useful commands:"
print_status "  - Check status: pm2 status"
print_status "  - View logs: pm2 logs english-ai-backend"
print_status "  - Update app: ./update.sh"
print_status "  - Create backup: ./backup.sh"
print_status "  - Restart app: pm2 restart english-ai-backend"
print_status ""
print_status "🔧 Configuration files:"
print_status "  - Environment: .env.production"
print_status "  - Nginx: /etc/nginx/sites-available/english-ai-agent"
print_status "  - PM2: ecosystem.config.js"
print_status ""
print_warning "Make sure to:"
print_warning "1. Point your domain DNS to this server's IP"
print_warning "2. Test the application at your domain"
print_warning "3. Set up automated backups with cron"
print_warning "4. Monitor logs and performance"

echo ""
echo "🚀 Your English AI Agent is ready for production!" 