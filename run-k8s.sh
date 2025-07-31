#!/bin/bash

echo "🚀 Applying Kubernetes resources..."
kubectl apply -f k8s-all.yaml

echo "⏳ Waiting for pods to start..."
sleep 7  # Optional: increase if pods take longer

echo "🔌 Starting port forwarding..."

# Forward users-service: 8080 -> 80
kubectl port-forward svc/users-service 8080:80 &
USER_PID=$!

# Forward outing-profile-service: 5000 -> 80
kubectl port-forward svc/outing-profile-service 5000:80 &
OUTING_PID=$!

kubectl port-forward svc/mongo 27017:27017 &
MONGO_PID=$!

echo "✅ Port forwarding started."
echo "Users Service: http://localhost:8080"
echo "Outing Profile Service: http://localhost:5000"
echo "Press Ctrl+C to stop."

wait $USER_PID $OUTING_PID $MONGO_PID