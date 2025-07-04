#!/usr/bin/env powershell

param(
    [switch]$SkipInstall,
    [switch]$Dev
)

Write-Host "🪟 English AI Agent - Windows Setup" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Prerequisites {
    if (!(Test-Admin)) {
        Write-Host "❌ Please run as Administrator to install prerequisites" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "📦 Installing prerequisites..." -ForegroundColor Yellow
    
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Chocolatey..." -ForegroundColor Cyan
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }
    
    Write-Host "Installing required packages..." -ForegroundColor Cyan
    choco install docker-desktop git nodejs python -y
    
    Write-Host "✅ Prerequisites installed. Please restart your computer." -ForegroundColor Green
}

function Setup-Environment {
    Write-Host "🔧 Setting up environment..." -ForegroundColor Yellow
    
    if (!(Test-Path ".env.production")) {
        if (Test-Path "backend/env.example") {
            Copy-Item "backend/env.example" ".env.production"
            Write-Host "✅ Created .env.production from template" -ForegroundColor Green
            Write-Host "⚠️  Please edit .env.production with your AWS credentials" -ForegroundColor Yellow
        } else {
            Write-Host "❌ backend/env.example not found" -ForegroundColor Red
            return $false
        }
    }
    
    return $true
}

function Test-DockerRunning {
    try {
        docker version | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Start-Application {
    Write-Host "🚀 Starting application..." -ForegroundColor Yellow
    
    if (!(Test-DockerRunning)) {
        Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
        return $false
    }
    
    $composeFile = if ($Dev) { "docker-compose.yml" } else { "docker-compose.windows.yml" }
    
    if (!(Test-Path $composeFile)) {
        $composeFile = "docker-compose.prod.yml"
    }
    
    Write-Host "Using compose file: $composeFile" -ForegroundColor Cyan
    
    docker-compose -f $composeFile down
    docker-compose -f $composeFile build
    docker-compose -f $composeFile up -d
    
    Write-Host "✅ Application started!" -ForegroundColor Green
    Write-Host "🌐 Frontend: http://localhost" -ForegroundColor Cyan
    Write-Host "🔌 Backend API: http://localhost:5000" -ForegroundColor Cyan
    
    Start-Sleep 5
    Test-ApplicationHealth
}

function Test-ApplicationHealth {
    Write-Host "🏥 Checking application health..." -ForegroundColor Yellow
    
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Backend is healthy!" -ForegroundColor Green
                break
            }
        } catch {
            Write-Host "⏳ Waiting for backend... ($attempt/$maxAttempts)" -ForegroundColor Yellow
            Start-Sleep 2
            $attempt++
        }
    }
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Frontend is healthy!" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Frontend not responding yet" -ForegroundColor Yellow
    }
}

function Show-Usage {
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\setup-windows.ps1           # Full setup and start" -ForegroundColor White
    Write-Host "  .\setup-windows.ps1 -SkipInstall   # Skip prerequisite installation" -ForegroundColor White
    Write-Host "  .\setup-windows.ps1 -Dev           # Start in development mode" -ForegroundColor White
}

if (!$SkipInstall) {
    Install-Prerequisites
}

if (Setup-Environment) {
    Start-Application
} else {
    Write-Host "❌ Setup failed" -ForegroundColor Red
    Show-Usage
} 