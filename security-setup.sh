#!/bin/bash

echo "🔒 English Agent - Security Setup"
echo "================================="

setup_dev_https() {
    echo "📜 Setting up HTTPS for Development..."
    
    mkdir -p certs/dev
    
    # Generate self-signed certificate for development
    openssl req -x509 -newkey rsa:4096 -keyout certs/dev/key.pem -out certs/dev/cert.pem -days 365 -nodes \
        -subj "/C=US/ST=Development/L=Local/O=EnglishAgent/CN=localhost" \
        -config <(echo '[req]'; echo 'distinguished_name=req') \
        -extensions v3_req \
        -config <(cat <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = Development
L = Local
O = English Agent
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
)
    
    chmod 600 certs/dev/key.pem
    chmod 644 certs/dev/cert.pem
    
    echo "✅ Development HTTPS certificates created in certs/dev/"
}

setup_production_https() {
    echo "🌐 Setting up HTTPS for Production..."
    
    mkdir -p certs/prod
    mkdir -p nginx/sites-available
    mkdir -p nginx/sites-enabled
    
    echo "📝 Creating Let's Encrypt setup script..."
    
    cat > setup-letsencrypt.sh <<'EOF'
#!/bin/bash

DOMAIN=${1:-your-domain.com}
EMAIL=${2:-your-email@example.com}

echo "🔐 Setting up Let's Encrypt for domain: $DOMAIN"

# Install certbot if not installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Stop nginx if running
sudo systemctl stop nginx 2>/dev/null || true

# Get certificate
sudo certbot certonly --standalone \
    --preferred-challenges http \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

# Setup auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

echo "✅ Let's Encrypt certificate obtained for $DOMAIN"
echo "📁 Certificate location: /etc/letsencrypt/live/$DOMAIN/"
EOF
    
    chmod +x setup-letsencrypt.sh
    
    echo "✅ Let's Encrypt setup script created"
}

setup_security_configs() {
    echo "🛡️ Setting up security configurations..."
    
    # Create secure environment template
    cat > .env.secure.example <<'EOF'
# Security Configuration
NODE_ENV=production
SECRET_KEY=your-super-secure-secret-key-change-this-in-production
JWT_SECRET=your-jwt-secret-change-this-in-production

# HTTPS Configuration
SSL_CERT_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem
FORCE_HTTPS=true
SECURE_COOKIES=true

# CORS Configuration
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
CORS_CREDENTIALS=true

# Rate Limiting (Enhanced)
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=50
RATE_LIMIT_SKIP_FAILED_REQUESTS=true

# Session Security
SESSION_TIMEOUT=3600
SECURE_HEADERS=true

# Content Security Policy
CSP_ENABLED=true
CSP_REPORT_URI=/api/security/csp-report

# File Upload Security
MAX_FILE_SIZE=5242880
ALLOWED_FILE_TYPES=pdf,doc,docx,txt,png,jpg,jpeg
UPLOAD_SCAN_VIRUS=true

# Database Security (if using database)
DB_SSL_MODE=require
DB_CONNECTION_TIMEOUT=30000

# Logging & Monitoring
SECURITY_LOGGING=true
LOG_LEVEL=info
AUDIT_TRAIL=true
EOF
    
    echo "✅ Secure environment template created"
}

setup_firewall() {
    echo "🔥 Setting up UFW firewall rules..."
    
    cat > setup-firewall.sh <<'EOF'
#!/bin/bash

echo "🔥 Configuring UFW firewall..."

# Enable UFW
sudo ufw --force enable

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH (adjust port if needed)
sudo ufw allow 22/tcp

# HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Backend API (only from localhost for security)
sudo ufw allow from 127.0.0.1 to any port 5000

# Rate limiting for HTTP/HTTPS
sudo ufw limit 80/tcp
sudo ufw limit 443/tcp

# Log firewall activity
sudo ufw logging on

echo "✅ Firewall configured"
sudo ufw status verbose
EOF
    
    chmod +x setup-firewall.sh
    echo "✅ Firewall setup script created"
}

setup_fail2ban() {
    echo "🚫 Setting up Fail2Ban..."
    
    cat > setup-fail2ban.sh <<'EOF'
#!/bin/bash

echo "🚫 Installing and configuring Fail2Ban..."

# Install fail2ban
sudo apt update
sudo apt install -y fail2ban

# Create custom configuration
sudo tee /etc/fail2ban/jail.local > /dev/null <<'FAIL2BAN_EOF'
[DEFAULT]
# Ban time: 1 hour
bantime = 3600
# Find time: 10 minutes
findtime = 600
# Max retries: 3
maxretry = 3

# Email notifications (configure with your email)
destemail = admin@your-domain.com
sendername = Fail2Ban
mta = sendmail

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https
logpath = /var/log/nginx/access.log
FAIL2BAN_EOF

# Start and enable fail2ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

echo "✅ Fail2Ban configured and started"
sudo fail2ban-client status
EOF
    
    chmod +x setup-fail2ban.sh
    echo "✅ Fail2Ban setup script created"
}

setup_monitoring() {
    echo "📊 Setting up security monitoring..."
    
    cat > security-monitor.sh <<'EOF'
#!/bin/bash

echo "📊 Security Monitoring Dashboard"
echo "==============================="

echo "🔥 Firewall Status:"
sudo ufw status

echo -e "\n🚫 Fail2Ban Status:"
sudo fail2ban-client status 2>/dev/null || echo "Fail2Ban not running"

echo -e "\n🔐 SSL Certificate Status:"
if [ -f "/etc/letsencrypt/live/$(hostname)/cert.pem" ]; then
    openssl x509 -in /etc/letsencrypt/live/$(hostname)/cert.pem -text -noout | grep -A 2 "Validity"
else
    echo "No production SSL certificate found"
fi

echo -e "\n📈 Recent Security Events:"
echo "Failed SSH attempts (last 10):"
grep "Failed password" /var/log/auth.log | tail -10 2>/dev/null || echo "No failed SSH attempts"

echo -e "\nNginx errors (last 5):"
tail -5 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error log"

echo -e "\n🔍 Open Ports:"
ss -tulpn | grep LISTEN
EOF
    
    chmod +x security-monitor.sh
    echo "✅ Security monitoring script created"
}

main() {
    case "$1" in
        "dev")
            setup_dev_https
            ;;
        "prod")
            setup_production_https
            setup_security_configs
            setup_firewall
            setup_fail2ban
            setup_monitoring
            ;;
        "all")
            setup_dev_https
            setup_production_https
            setup_security_configs
            setup_firewall
            setup_fail2ban
            setup_monitoring
            ;;
        *)
            echo "Usage: $0 [dev|prod|all]"
            echo "  dev  - Setup development HTTPS only"
            echo "  prod - Setup production security"
            echo "  all  - Setup both development and production"
            exit 1
            ;;
    esac
    
    echo -e "\n🎉 Security setup completed!"
    echo "📖 Next steps:"
    echo "  1. Review and update .env.secure.example with your values"
    echo "  2. For production: run ./setup-letsencrypt.sh your-domain.com your-email@domain.com"
    echo "  3. For firewall: run ./setup-firewall.sh"
    echo "  4. For monitoring: run ./setup-fail2ban.sh"
    echo "  5. Monitor security: ./security-monitor.sh"
}

main "$@" 