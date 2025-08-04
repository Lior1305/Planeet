# PowerShell script to deploy Kubernetes resources and set up port forwarding

Write-Host "Deploying Kubernetes resources..." -ForegroundColor Green
kubectl apply -f k8s-all.yaml

Write-Host "Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=outing-profile-service --timeout=120s
kubectl wait --for=condition=ready pod -l app=users-service --timeout=120s
kubectl wait --for=condition=ready pod -l app=mongo --timeout=120s
kubectl wait --for=condition=ready pod -l app=ui-service --timeout=120s

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

Write-Host ""
Write-Host "All services are now accessible:" -ForegroundColor Green
Write-Host "   UI Service:            http://localhost:3000" -ForegroundColor White
Write-Host "   Users Service:        http://localhost:8080" -ForegroundColor White
Write-Host "   Outing Profile Service: http://localhost:5000" -ForegroundColor White
Write-Host "   MongoDB:              localhost:27017" -ForegroundColor White
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
    Stop-Job $userJob, $outingJob, $mongoJob, $uiJob -ErrorAction SilentlyContinue
    Remove-Job $userJob, $outingJob, $mongoJob, $uiJob -ErrorAction SilentlyContinue
    Write-Host "Port forwarding stopped." -ForegroundColor Green
} 


### On powershell run this : .\deploy-k8s.ps1
