# 🚀 Azure Kubernetes Service (AKS) Manual Deployment Guide

This guide explains how to manually deploy your Planeet application to Azure Kubernetes Service (AKS) through the Azure Portal UI.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Existing AKS Cluster** - You mentioned you already created one
2. **kubectl** - [Installation Guide](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
3. **Docker Images** - Your application images should be available in container registries
4. **Azure Portal Access** - Access to your AKS cluster

## 🏗️ Architecture Overview

The deployment creates the following components:

```
Internet → Azure Load Balancer → NGINX Ingress → Services → Pods
```

- **NGINX Ingress Controller** - Routes external traffic to services
- **UI Service** - React frontend accessible at root path `/`
- **API Services** - Backend services accessible at `/api/*` paths
- **MongoDB** - Database with persistent storage
- **Load Balancer** - Azure-managed load balancer for external access

## 📁 Files Overview

- `azure-k8s-deployment.yaml` - Complete Kubernetes manifests for Azure deployment
- `AZURE-DEPLOYMENT-README.md` - This deployment guide

## 🚀 Manual Deployment Steps

### Step 1: Access Your AKS Cluster

1. **Open Azure Portal** and navigate to your AKS cluster
2. **Click on "Connect"** in the cluster overview
3. **Copy the kubectl command** provided (it will look like):
   ```bash
   az aks get-credentials --resource-group <your-rg> --name <your-cluster> --overwrite-existing
   ```

### Step 2: Connect to Your Cluster

1. **Open your terminal/command prompt**
2. **Run the kubectl command** you copied from Azure Portal
3. **Verify connection**:
   ```bash
   kubectl cluster-info
   ```

### Step 3: Prepare the YAML File

1. **Open `azure-k8s-deployment.yaml`** in a text editor
2. **Update the domain name** in the Ingress configuration:
   ```yaml
   spec:
     rules:
       - host: your-actual-domain.com  # Replace planeet.azure.com with your domain
   ```
3. **Update secrets** if needed (Google API key, MongoDB URI)

### Step 4: Deploy Through Azure Portal

#### Option A: Using kubectl (Recommended)

1. **Apply the YAML file**:
   ```bash
   kubectl apply -f azure-k8s-deployment.yaml
   ```

2. **Monitor deployment**:
   ```bash
   kubectl get pods -n planeet
   kubectl get services -n planeet
   kubectl get ingress -n planeet
   ```

#### Option B: Using Azure Portal UI

1. **Go to your AKS cluster** in Azure Portal
2. **Click on "Kubernetes resources"** in the left menu
3. **Click "Add"** and select "YAML"
4. **Copy and paste** the contents of `azure-k8s-deployment.yaml`
5. **Click "Add"** to deploy

### Step 5: Verify Deployment

1. **Check pod status**:
   ```bash
   kubectl get pods -n planeet
   ```

2. **Check services**:
   ```bash
   kubectl get services -n planeet
   ```

3. **Check ingress**:
   ```bash
   kubectl get ingress -n planeet
   ```

4. **Get external IP**:
   ```bash
   kubectl get service nginx-ingress-controller -n ingress-nginx
   ```

## 🔧 Configuration

### Environment Variables

The deployment uses ConfigMaps and Secrets for configuration:

**ConfigMap (`planeet-config`):**
- Service URLs for inter-service communication
- Environment settings

**Secret (`planeet-secrets`):**
- Google Places API key
- MongoDB connection string

### Updating Secrets

Before deployment, update the secrets in `azure-k8s-deployment.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: planeet-secrets
  namespace: planeet
type: Opaque
data:
  # Base64 encoded values
  GOOGLE_PLACES_API_KEY: "YOUR_BASE64_ENCODED_API_KEY"
  MONGO_URI: "YOUR_BASE64_ENCODED_MONGO_URI"
```

To encode values:
```bash
# Linux/macOS
echo -n "your-api-key" | base64

# Windows PowerShell
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("your-api-key"))
```

### Domain Configuration

Update the domain name in the Ingress configuration:

```yaml
spec:
  rules:
    - host: your-domain.com  # Replace with your actual domain
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ui-service
                port:
                  number: 80
```

## 🌐 Accessing Your Application

### External Access

After deployment, your application will be accessible at:

- **UI**: `http://your-domain.com`
- **Planning API**: `http://your-domain.com/api/planning`
- **Users API**: `http://your-domain.com/api/users`
- **Venues API**: `http://your-domain.com/api/venues`
- **Outing Profile API**: `http://your-domain.com/api/outing`

### Getting External IP

```bash
kubectl get service nginx-ingress-controller -n ingress-nginx
```

### Local Testing

For local testing, add the external IP to your hosts file:

```bash
# Linux/macOS
echo "EXTERNAL_IP your-domain.com" | sudo tee -a /etc/hosts

# Windows (run as Administrator)
echo "EXTERNAL_IP your-domain.com" >> C:\Windows\System32\drivers\etc\hosts
```

## 📊 Monitoring and Management

### Check Deployment Status

```bash
# View all resources
kubectl get all -n planeet

# Check pod status
kubectl get pods -n planeet

# Check service status
kubectl get services -n planeet

# Check ingress status
kubectl get ingress -n planeet
```

### View Logs

```bash
# UI service logs
kubectl logs -f deployment/ui-service -n planeet

# Planning service logs
kubectl logs -f deployment/planning-service -n planeet

# All pods logs
kubectl logs -f -l app=ui-service -n planeet
```

### Scaling

```bash
# Scale UI service
kubectl scale deployment ui-service -n planeet --replicas=5

# Scale planning service
kubectl scale deployment planning-service -n planeet --replicas=3
```

### Access Pod Shell

```bash
# Access UI service pod
kubectl exec -it deployment/ui-service -n planeet -- /bin/bash

# Access planning service pod
kubectl exec -it deployment/planning-service -n planeet -- /bin/bash
```

## 🔒 Security Considerations

1. **Secrets Management**: Use Azure Key Vault for production secrets
2. **Network Policies**: Implement network policies to restrict pod-to-pod communication
3. **RBAC**: Configure proper role-based access control
4. **TLS/SSL**: Enable HTTPS with proper certificates
5. **Resource Limits**: Monitor and adjust resource limits based on usage

## 💰 Cost Optimization

1. **Node Sizing**: Use appropriate VM sizes for your workload
2. **Auto-scaling**: Enable cluster auto-scaling
3. **Spot Instances**: Use spot instances for non-critical workloads
4. **Resource Monitoring**: Monitor resource usage and optimize accordingly

## 🚨 Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name> -n planeet
   kubectl logs <pod-name> -n planeet
   ```

2. **Services not accessible**
   ```bash
   kubectl get endpoints -n planeet
   kubectl describe service <service-name> -n planeet
   ```

3. **Ingress not working**
   ```bash
   kubectl describe ingress planeet-ingress -n planeet
   kubectl get events -n planeet
   ```

4. **External IP not assigned**
   ```bash
   kubectl get service nginx-ingress-controller -n ingress-nginx
   # Wait for Azure to assign external IP (can take 5-10 minutes)
   ```

### Health Checks

The deployment includes health checks for all services:

- **Liveness Probe**: Restarts pods if they become unresponsive
- **Readiness Probe**: Ensures pods are ready to receive traffic

### Resource Issues

```bash
# Check resource usage
kubectl top pods -n planeet
kubectl top nodes

# Check resource limits
kubectl describe pod <pod-name> -n planeet | grep -A 10 "Limits:"
```

## 🔄 Updates and Rollbacks

### Updating Images

```bash
# Update UI service image
kubectl set image deployment/ui-service ui-service=nikaklimenchuk/planeet-ui:react-v1.5 -n planeet

# Update planning service image
kubectl set image deployment/planning-service planning-service=dartoledano/planning-service:v1.0.4 -n planeet
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/ui-service -n planeet

# Check rollout status
kubectl rollout status deployment/ui-service -n planeet
```

## 🗑️ Cleanup

To remove the deployment:

```bash
# Remove all resources
kubectl delete namespace planeet
kubectl delete namespace ingress-nginx

# Or remove individual resources
kubectl delete -f azure-k8s-deployment.yaml
```

## 📚 Additional Resources

- [Azure Kubernetes Service Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Azure Portal Kubernetes Resources](https://docs.microsoft.com/en-us/azure/aks/kubernetes-portal)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Kubernetes events: `kubectl get events -n planeet`
3. Check Azure portal for AKS cluster status
4. Review service logs for specific error messages

---

**Happy Deploying! 🎉**
