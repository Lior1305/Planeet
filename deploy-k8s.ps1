# PowerShell script to deploy Kubernetes resources and set up port forwarding

Write-Host "Deploying Kubernetes resources..." -ForegroundColor Green
kubectl apply -f k8s-all.yaml

Write-Host "Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=outing-profile-service --timeout=120s
kubectl wait --for=condition=ready pod -l app=users-service --timeout=120s
kubectl wait --for=condition=ready pod -l app=mongo --timeout=120s
kubectl wait --for=condition=ready pod -l app=ui-service --timeout=120s
kubectl wait --for=condition=ready pod -l app=planning-service --timeout=120s
kubectl wait --for=condition=ready pod -l app=venues-service --timeout=120s
kubectl wait --for=condition=ready pod -l app=booking-service --timeout=120s

Write-Host "All pods are ready!" -ForegroundColor Green

Write-Host "Starting port forwarding..." -ForegroundColor Cyan

# Start port forwarding jobs
Write-Host "Forwarding users-service (8080:80)..." -ForegroundColor Blue
$userJob = Start-Job -ScriptBlock { kubectl port-forward svc/users-service 8080:80 }

Write-Host "Forwarding outing-profile-service (5000:80)..." -ForegroundColor Blue
$outingJob = Start-Job -ScriptBlock { kubectl port-forward svc/outing-profile-service 5000:80 }

Write-Host "Forwarding mongo (27017:27017)..." -ForegroundColor Blue
$mongoJob = Start-Job -ScriptBlock { kubectl port-forward svc/mongo 27017:27017 }

Write-Host "Forwarding ui-service (3000:80)..." -ForegroundColor Blue
$uiJob = Start-Job -ScriptBlock { kubectl port-forward svc/ui-service 3000:80 }

Write-Host "Forwarding planning-service (8001:8001)..." -ForegroundColor Blue
$planningJob = Start-Job -ScriptBlock { kubectl port-forward svc/planning-service 8001:8001 }

Write-Host "Forwarding venues-service (8000:8000)..." -ForegroundColor Blue
$venuesJob = Start-Job -ScriptBlock { kubectl port-forward svc/venues-service 8000:8000 }

Write-Host "Forwarding booking-service (8004:8004)..." -ForegroundColor Blue
$bookingJob = Start-Job -ScriptBlock { kubectl port-forward svc/booking-service 8004:8004 }

Write-Host ""
Write-Host "All services are now accessible:" -ForegroundColor Green
Write-Host "   UI Service:            http://localhost:3000 (local)" -ForegroundColor White
Write-Host "   UI Service (Phone):    http://<localhost_ip_address>:30000" -ForegroundColor Cyan
Write-Host "   Users Service:        http://localhost:8080" -ForegroundColor White
Write-Host "   Outing Profile Service: http://localhost:5000" -ForegroundColor White
Write-Host "   MongoDB:              localhost:27017" -ForegroundColor White
Write-Host "   Planning Service:     http://localhost:8001" -ForegroundColor White
Write-Host "   Venues Service:       http://localhost:8000" -ForegroundColor White
Write-Host "   Booking Service:      http://localhost:8004" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all port forwarding" -ForegroundColor Yellow

try {
    # Wait for user to press Ctrl+C
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "Stopping port forwarding..." -ForegroundColor Red
    
    # Immediate aggressive shutdown
    $jobs = @($userJob, $outingJob, $mongoJob, $uiJob, $planningJob, $venuesJob, $bookingJob)
    
    # Force kill all kubectl processes immediately
    Write-Host "Force killing kubectl processes..." -ForegroundColor Yellow
    Get-Process | Where-Object { $_.ProcessName -like "*kubectl*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Stop all jobs with force
    Write-Host "Force stopping jobs..." -ForegroundColor Yellow
    Stop-Job $jobs -Force -ErrorAction SilentlyContinue
    
    # Wait max 1 second for cleanup
    $timeout = 1
    $elapsed = 0
    
    while ($elapsed -lt $timeout) {
        $runningJobs = Get-Job -State Running | Where-Object { $jobs -contains $_ }
        if ($runningJobs.Count -eq 0) {
            break
        }
        Start-Sleep -Milliseconds 100
        $elapsed += 0.1
    }
    
    # Final cleanup - remove all jobs regardless of state
    Write-Host "Cleaning up jobs..." -ForegroundColor Yellow
    Remove-Job $jobs -Force -ErrorAction SilentlyContinue
    
    # Kill any remaining processes that might be hanging
    Get-Process | Where-Object { $_.ProcessName -like "*kubectl*" -or $_.ProcessName -like "*port-forward*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "Port forwarding stopped in $([math]::Round($elapsed, 1)) seconds." -ForegroundColor Green
}


### On powershell run this : .\deploy-k8s.ps1
