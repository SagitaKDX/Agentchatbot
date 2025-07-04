# 🪟 Windows Setup Guide - English AI Agent

This guide will help you set up and deploy the English AI Agent application on Windows for development and testing.

## 📋 Prerequisites

### Required Software
1. **Docker Desktop for Windows** - [Download here](https://www.docker.com/products/docker-desktop/)
2. **Git for Windows** - [Download here](https://git-scm.com/download/win)
3. **Node.js (v16+)** - [Download here](https://nodejs.org/)
4. **Python 3.9+** - [Download here](https://www.python.org/downloads/)

### Optional but Recommended
- **Windows Terminal** - [Get from Microsoft Store](https://aka.ms/terminal)
- **Visual Studio Code** - [Download here](https://code.visualstudio.com/)

## 🚀 Quick Setup (Docker - Recommended)

### Step 1: Install Prerequisites
```powershell
# Open PowerShell as Administrator and install Chocolatey (package manager)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install required tools
choco install docker-desktop git nodejs python -y

# Restart your computer after installation
```

### Step 2: Clone and Setup Project
```powershell
# Open PowerShell in your desired directory
git clone <your-repo-url> english-ai-agent
cd english-ai-agent

# Create environment file
copy backend\env.example .env.production
```

### Step 3: Configure Environment
Edit `.env.production` with your credentials:
```env
# Server Configuration
PORT=5000
NODE_ENV=production
FRONTEND_URL=http://localhost

# AWS Configuration - REQUIRED
AWS_REGION=us-east-2
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# AWS Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# AWS S3 Configuration
AWS_S3_BUCKET=your-bucket-name
AWS_S3_PREFIX=knowledge-base/

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# File Upload Configuration
MAX_FILE_SIZE=10485760
MAX_FILES_PER_UPLOAD=5
```

### Step 4: Deploy with Docker
```powershell
# Start Docker Desktop first, then run:
docker-compose -f docker-compose.prod.yml up -d

# Check if services are running
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

Your application will be available at:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000

## 🛠️ Development Setup (Optional)

If you want to run the application locally for development:

### Backend Setup
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy env.example .env

# Run development server
python run.py
```

### Frontend Setup
```powershell
# Open new PowerShell window, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 🔧 Windows-Specific Docker Configuration

Create a `docker-compose.windows.yml` for Windows-optimized settings:

```yaml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: english-ai-backend
    restart: unless-stopped
    env_file:
      - .env.production
    ports:
      - "5000:5000"
    volumes:
      - logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: english-ai-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:5000

volumes:
  logs:
    driver: local
```

## 📱 Testing & Sustainability (1 Day)

### Resource Monitoring
```powershell
# Monitor Docker resource usage
docker stats

# Check disk usage
docker system df

# Clean up if needed
docker system prune -f
```

### Automated Health Checks
The application includes built-in health checks. Monitor them with:
```powershell
# Check backend health
curl http://localhost:5000/api/health

# View container health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Log Management
```powershell
# View real-time logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# Limit log size in docker-compose.yml (add to each service)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Performance Optimization for Testing

Add these optimizations to your environment:

```env
# Add to .env.production for better performance
FLASK_ENV=production
FLASK_DEBUG=False

# Reduce workers for testing environment
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=60
```

## 🚨 Troubleshooting

### Common Windows Issues

1. **Docker Desktop not starting**
   ```powershell
   # Enable Hyper-V and containers feature
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   Enable-WindowsOptionalFeature -Online -FeatureName containers -All
   ```

2. **Port conflicts**
   ```powershell
   # Check what's using port 80
   netstat -ano | findstr :80
   
   # Kill process if needed
   taskkill /F /PID <PID>
   ```

3. **PowerShell execution policy**
   ```powershell
   # Allow script execution
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Docker build fails**
   ```powershell
   # Clean Docker cache
   docker builder prune -a
   
   # Restart Docker Desktop
   Restart-Service com.docker.service
   ```

### AWS Configuration Issues
```powershell
# Test AWS credentials
aws configure list
aws bedrock list-foundation-models --region us-east-2
```

## 📊 Monitoring Dashboard

Create a simple monitoring script `monitor.ps1`:
```powershell
while ($true) {
    Clear-Host
    Write-Host "=== English AI Agent Status ===" -ForegroundColor Green
    Write-Host "Time: $(Get-Date)" -ForegroundColor Yellow
    
    # Check container status
    Write-Host "`nContainer Status:" -ForegroundColor Cyan
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    # Check resource usage
    Write-Host "`nResource Usage:" -ForegroundColor Cyan
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
    # Check endpoints
    Write-Host "`nEndpoint Health:" -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -TimeoutSec 5
        Write-Host "Backend: ✅ (Status: $($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "Backend: ❌ (Error)" -ForegroundColor Red
    }
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost" -TimeoutSec 5
        Write-Host "Frontend: ✅ (Status: $($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "Frontend: ❌ (Error)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 30
}
```

Run with: `.\monitor.ps1`

## 🎯 Quick Commands Cheat Sheet

```powershell
# Start application
docker-compose -f docker-compose.prod.yml up -d

# Stop application
docker-compose -f docker-compose.prod.yml down

# Restart application
docker-compose -f docker-compose.prod.yml restart

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Update application
git pull
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Cleanup
docker system prune -f
docker volume prune -f
```

## 🚀 Production Deployment (Cloud)

For cloud deployment on Windows-managed servers:

### AWS EC2 Windows Instance
1. Launch Windows Server 2019/2022 instance
2. Install Docker Desktop for Windows Server
3. Follow the Docker setup above
4. Configure Windows Firewall for ports 80, 443, 5000

### Azure Windows VM
1. Create Windows Server VM
2. Enable container features
3. Install Docker Desktop
4. Configure Network Security Groups

This setup will give you a robust, sustainable testing environment for your English AI Agent application on Windows! 