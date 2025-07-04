#!/usr/bin/env powershell

param(
    [int]$RefreshInterval = 30,
    [switch]$Compact
)

function Test-Endpoint {
    param([string]$Url, [string]$Name)
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 5
        return @{
            Name = $Name
            Status = "✅"
            Code = $response.StatusCode
            ResponseTime = $response.Headers.'X-Response-Time'
        }
    } catch {
        return @{
            Name = $Name
            Status = "❌"
            Code = "Error"
            ResponseTime = "-"
        }
    }
}

function Get-ContainerStats {
    try {
        $stats = docker stats --no-stream --format "{{.Container}};{{.CPUPerc}};{{.MemUsage}};{{.NetIO}};{{.BlockIO}}" 2>$null
        $results = @()
        
        foreach ($line in $stats) {
            if ($line) {
                $parts = $line -split ';'
                $results += @{
                    Container = $parts[0]
                    CPU = $parts[1]
                    Memory = $parts[2]
                    Network = $parts[3]
                    Disk = $parts[4]
                }
            }
        }
        return $results
    } catch {
        return @()
    }
}

function Show-CompactStatus {
    $backend = Test-Endpoint "http://localhost:5000/api/health" "Backend"
    $frontend = Test-Endpoint "http://localhost" "Frontend"
    
    $status = "$($backend.Status) Backend | $($frontend.Status) Frontend"
    Write-Host "$(Get-Date -Format 'HH:mm:ss') - $status" -ForegroundColor $(if ($backend.Status -eq "✅" -and $frontend.Status -eq "✅") { "Green" } else { "Red" })
}

function Show-DetailedStatus {
    Clear-Host
    
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "English AI Agent - Status Monitor" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "Time: $(Get-Date)" -ForegroundColor Yellow
    Write-Host "Refresh: Every $RefreshInterval seconds" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "📊 Container Status:" -ForegroundColor Cyan
    try {
        $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=english-ai"
        if ($containers) {
            Write-Host $containers
        } else {
            Write-Host "No containers running" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Docker not available" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "💻 Resource Usage:" -ForegroundColor Cyan
    $stats = Get-ContainerStats
    if ($stats.Count -gt 0) {
        Write-Host "Container`t`tCPU`t`tMemory`t`t`tNetwork" -ForegroundColor Gray
        Write-Host "--------`t`t---`t`t------`t`t`t-------" -ForegroundColor Gray
        foreach ($stat in $stats) {
            $containerName = $stat.Container -replace "english-ai-", ""
            Write-Host "$containerName`t`t$($stat.CPU)`t`t$($stat.Memory)`t`t$($stat.Network)"
        }
    } else {
        Write-Host "No container stats available" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🌐 Endpoint Health:" -ForegroundColor Cyan
    $backend = Test-Endpoint "http://localhost:5000/api/health" "Backend"
    $frontend = Test-Endpoint "http://localhost" "Frontend"
    
    Write-Host "Backend API:`t$($backend.Status) (HTTP $($backend.Code))" -ForegroundColor $(if ($backend.Status -eq "✅") { "Green" } else { "Red" })
    Write-Host "Frontend:`t$($frontend.Status) (HTTP $($frontend.Code))" -ForegroundColor $(if ($frontend.Status -eq "✅") { "Green" } else { "Red" })
    
    Write-Host ""
    Write-Host "🔗 Quick Links:" -ForegroundColor Cyan
    Write-Host "Frontend: http://localhost" -ForegroundColor Blue
    Write-Host "Backend API: http://localhost:5000" -ForegroundColor Blue
    Write-Host "Health Check: http://localhost:5000/api/health" -ForegroundColor Blue
    
    Write-Host ""
    Write-Host "💡 Commands:" -ForegroundColor Cyan
    Write-Host "Ctrl+C: Exit monitor" -ForegroundColor Gray
    Write-Host "docker-compose -f docker-compose.windows.yml logs -f: View logs" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "📈 System Info:" -ForegroundColor Cyan
    try {
        $diskUsage = docker system df --format "table {{.Type}}\t{{.Total}}\t{{.Active}}\t{{.Reclaimable}}" 2>$null
        if ($diskUsage) {
            Write-Host "Docker Disk Usage:"
            Write-Host $diskUsage
        }
    } catch {
        Write-Host "Disk usage info not available" -ForegroundColor Yellow
    }
}

Write-Host "🖥️  Starting English AI Agent Monitor..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

try {
    while ($true) {
        if ($Compact) {
            Show-CompactStatus
        } else {
            Show-DetailedStatus
        }
        
        Start-Sleep -Seconds $RefreshInterval
    }
} catch {
    Write-Host ""
    Write-Host "Monitor stopped." -ForegroundColor Yellow
} 