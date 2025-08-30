// Configuration service for Planeet UI
class ConfigService {
  constructor() {
    this.init();
  }

  init() {
    // Detect if we're running in Kubernetes or locally
    this.isKubernetes = this.detectKubernetesEnvironment();
    
    // Set service URLs based on environment
    this.setServiceUrls();
    
    console.log('Planeet UI Config initialized:', {
      environment: this.isKubernetes ? 'Kubernetes' : 'Local Development',
      services: this.services
    });
  }

  detectKubernetesEnvironment() {
    // Check if we're running in Kubernetes by looking for common indicators
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // If we're not on localhost, assume we're in Kubernetes
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return true;
    }
    
    // If we're on localhost but using a non-standard port (like 30000 from NodePort), 
    // we might be accessing Kubernetes from outside
    if (port && (port === '30000' || port === '30001' || port === '30002')) {
      return true;
    }
    
    // Check for environment variable (would be set in Kubernetes deployment)
    if (window.ENV && window.ENV.ENVIRONMENT === 'kubernetes') {
      return true;
    }
    
    return false;
  }

  getExternalServiceUrls() {
    // Get the current hostname and construct external URLs
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // If we have a port, use it (NodePort)
    if (port) {
      return {
        planning: `http://${hostname}:30001`,
        users: `http://${hostname}:30002`,
        venues: `http://${hostname}:30003`,
        outingProfile: `http://${hostname}:30004`
      };
    }
    
    // If no port, assume standard HTTP/HTTPS ports
    return {
      planning: `http://${hostname}:30001`,
      users: `http://${hostname}:30002`,
      venues: `http://${hostname}:30003`,
      outingProfile: `http://${hostname}:30004`
    };
  }

  isLocalKubernetes() {
    // Check if we're running local Kubernetes (Docker Desktop, Minikube, etc.)
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // Local Kubernetes: localhost + NodePort
    return hostname === 'localhost' && port && (port === '30000' || port === '30001' || port === '30002');
  }

  setServiceUrls() {
    if (this.isLocalKubernetes()) {
      // Local Kubernetes (Docker Desktop, Minikube) - use NodePort URLs
      this.services = {
        planning: 'http://localhost:30001',
        users: 'http://localhost:30002',
        venues: 'http://localhost:30003',
        outingProfile: 'http://localhost:30004'
      };
    } else if (this.isKubernetes) {
      // Production Kubernetes with LoadBalancer UI - use ingress paths
      // The UI service has its own LoadBalancer, APIs go through ingress
      const hostname = window.location.hostname;
      console.log('hostname', hostname);
      this.services = {
        planning: `http://${hostname}/api/planning`,
        users: `http://${hostname}/api`,
        venues: `http://${hostname}/api/venues`,
        outingProfile: `http://${hostname}/api/outing`
      };
    } else {
      // Local development
      this.services = {
        planning: 'http://localhost:8001',
        users: 'http://localhost:8080',
        venues: 'http://localhost:8000',
        outingProfile: 'http://localhost:5000'
      };
    }
  }
  
  // Get service URL by name
  getServiceUrl(serviceName) {
    const url = this.services[serviceName];
    if (!url) {
      console.error(`Unknown service: ${serviceName}`);
      return null;
    }
    return url;
  }

  // Get planning service URL
  getPlanningServiceUrl() {
    return this.getServiceUrl('planning');
  }

  // Get users service URL
  getUsersServiceUrl() {
    return this.getServiceUrl('users');
  }

  // Get venues service URL
  getVenuesServiceUrl() {
    return this.getServiceUrl('venues');
  }

  // Get outing profile service URL
  getOutingProfileServiceUrl() {
    return this.getServiceUrl('outingProfile');
  }

  // Get current environment info
  getEnvironmentInfo() {
    return {
      isKubernetes: this.isKubernetes,
      hostname: window.location.hostname,
      port: window.location.port,
      services: { ...this.services }
    };
  }

  // Override configuration (useful for testing or manual configuration)
  overrideConfig(overrides) {
    if (overrides.services) {
      this.services = { ...this.services, ...overrides.services };
    }
    if (overrides.isKubernetes !== undefined) {
      this.isKubernetes = overrides.isKubernetes;
    }
    console.log('Configuration overridden:', this.getEnvironmentInfo());
  }
}

// Create and export config instance
const configService = new ConfigService();

export default configService;
