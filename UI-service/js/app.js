// Planeet UI Application Logic
class PlaneetApp {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showPage('home');
    }

    setupEventListeners() {
        // Add any global event listeners here
        console.log('Planeet App initialized');
    }

    showPage(page) {
        // Hide all pages
        ['home', 'login', 'register'].forEach(p => {
            const el = document.getElementById(p);
            if (el) el.classList.add('hidden');
        });
        
        // Show target page
        const target = document.getElementById(page);
        if (target) target.classList.remove('hidden');
    }

    goHome() {
        this.showPage('home');
        this.currentUser = null;
    }

    async validateRegister() {
        const username = document.getElementById('regUsername').value.trim();
        const password = document.getElementById('regPassword').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const phone = document.getElementById('regPhone').value.trim();
        
        // Validation
        if (!username || !password || !email) {
            alert("Please fill in username, password, and email.");
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert("Please enter a valid email address.");
            return;
        }

        // Phone validation (optional)
        if (phone && !/^05\d{8}$/.test(phone)) {
            alert("Please enter a valid Israeli phone number (e.g., 05XXXXXXXX) or leave it empty.");
            return;
        }

        try {
            console.log('Attempting to register user:', username);
            
            // Create user
            const userData = {
                username: username,
                email: email,
                password: password,
                phone: phone
            };

            const userResponse = await fetch(`${window.appConfig.getUsersServiceUrl()}/users`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });

            if (userResponse.ok) {
                const user = await userResponse.json();
                console.log('Registration successful:', user);
                this.currentUser = user;
                this.redirectToDashboard();
            } else {
                const errorText = await userResponse.text();
                console.error('User creation failed:', errorText);
                alert('Registration failed. Please try again.');
            }
        } catch (error) {
            console.error('Registration error:', error);
            alert('Connection error. Please check if all services are running.');
        }
    }

    async login() {
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value.trim();
        
        if (!username || !password) {
            alert("Please enter both username and password.");
            return;
        }

        try {
            console.log('Attempting to login user:', username);
            
            // Get all users and find the matching one
            const response = await fetch(`${window.appConfig.getUsersServiceUrl()}/users`);
            if (response.ok) {
                const users = await response.json();
                console.log('Retrieved users:', users);
                
                const user = users.find(u => u.username === username && u.password === password);
                
                if (user) {
                    console.log('Login successful:', user);
                    this.currentUser = user;
                    this.redirectToDashboard();
                } else {
                    console.log('Login failed: Invalid credentials');
                    alert("Invalid username or password.");
                }
            } else {
                console.error('Login failed: API error');
                alert("Login failed. Please try again.");
            }
        } catch (error) {
            console.error('Login error:', error);
            alert("Connection error. Please check if all services are running.");
        }
    }

    redirectToDashboard() {
        console.log('Redirecting to plan page...');
        console.log('Current user:', this.currentUser);
        
        // Save user data to localStorage
        localStorage.setItem('planeetUser', JSON.stringify(this.currentUser));
        console.log('User data saved to localStorage');
        
        // Try multiple redirect approaches
        console.log('Current URL:', window.location.href);
        console.log('Current pathname:', window.location.pathname);
        
        // Check if we're on the root path (localhost:3000)
        if (window.location.pathname === '/' || window.location.pathname === '') {
            console.log('On root path, redirecting to plan.html');
            window.location.href = 'plan.html';
        } else {
            // Get the base URL
            const baseUrl = window.location.origin + window.location.pathname.replace('index.html', '');
            console.log('Base URL:', baseUrl);
            
            const planUrl = baseUrl + 'plan.html';
            console.log('Plan URL:', planUrl);
            
            // Try the redirect
            try {
                window.location.href = planUrl;
            } catch (error) {
                console.error('Redirect error:', error);
                // Fallback
                window.location.replace(planUrl);
            }
        }
    }

    // Test function to debug redirect issues
    testRedirect() {
        console.log('Testing redirect...');
        console.log('Current URL:', window.location.href);
        
        localStorage.setItem('planeetUser', JSON.stringify({
            username: 'testuser',
            email: 'test@example.com',
            phone: '+972 50-123-4567'
        }));
        
        // Check if we're on the root path (localhost:3000)
        if (window.location.pathname === '/' || window.location.pathname === '') {
            console.log('On root path, redirecting to plan.html');
            window.location.href = 'plan.html';
        } else {
            // Get the base URL
            const baseUrl = window.location.origin + window.location.pathname.replace('test-redirect.html', '');
            const planUrl = baseUrl + 'plan.html';
            console.log('Attempting redirect to:', planUrl);
            
            window.location.href = planUrl;
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.planeetApp = new PlaneetApp();
});

// Global functions for HTML onclick handlers
function showPage(page) {
    window.planeetApp.showPage(page);
}

function goHome() {
    window.planeetApp.goHome();
}

function validateRegister() {
    window.planeetApp.validateRegister();
}

function login() {
    window.planeetApp.login();
}

// Test function for debugging
function testRedirect() {
    window.planeetApp.testRedirect();
} 