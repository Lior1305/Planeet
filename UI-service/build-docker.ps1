# Build and push React Docker image for Planeet UI
Write-Host "Building React Docker image..." -ForegroundColor Green

# Build the React app first
Write-Host "Building React app..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "React build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "React build successful!" -ForegroundColor Green

# Build Docker image
$IMAGE_TAG = "nikaklimenchuk/planeet-ui:react-v1.9.67"
Write-Host "Building Docker image: $IMAGE_TAG" -ForegroundColor Yellow

docker build -f Dockerfile-React -t $IMAGE_TAG .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Docker build successful!" -ForegroundColor Green

# Push to Docker Hub
Write-Host "Pushing to Docker Hub..." -ForegroundColor Yellow
docker push $IMAGE_TAG

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker push failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Docker image pushed successfully!" -ForegroundColor Green
Write-Host "New image tag: $IMAGE_TAG" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update k8s-all.yaml to use: $IMAGE_TAG"
Write-Host "2. Apply the updated Kubernetes configuration"
Write-Host "3. Restart the UI service deployment"
