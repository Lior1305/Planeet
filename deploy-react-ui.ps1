# Deploy React UI to Kubernetes
Write-Host "Deploying React UI to Kubernetes..." -ForegroundColor Green

# Apply the updated Kubernetes configuration
Write-Host "Applying Kubernetes configuration..." -ForegroundColor Yellow
kubectl apply -f k8s-all.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "Kubernetes apply failed!" -ForegroundColor Red
    exit 1
}

# Restart the UI service deployment to pull the new image
Write-Host "Restarting UI service deployment..." -ForegroundColor Yellow
kubectl rollout restart deployment/ui-service

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment restart failed!" -ForegroundColor Red
    exit 1
}

# Wait for the rollout to complete
Write-Host "Waiting for rollout to complete..." -ForegroundColor Yellow
kubectl rollout status deployment/ui-service

Write-Host ""
Write-Host "React UI deployment completed!" -ForegroundColor Green
Write-Host "The new React-based UI should now be available at your Kubernetes cluster." -ForegroundColor Cyan
Write-Host ""
Write-Host "To check the status:" -ForegroundColor Yellow
Write-Host "kubectl get pods -l app=ui-service" -ForegroundColor White
Write-Host "kubectl logs -l app=ui-service" -ForegroundColor White
