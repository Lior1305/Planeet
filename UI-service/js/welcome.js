// Planeet Welcome Page Logic
class WelcomeApp {
    constructor() {
        console.log('WelcomeApp constructor called');
        console.log('appConfig available in constructor:', window.appConfig);
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showPage('home');
        console.log('Welcome App initialized at:', window.location.href);
    }

    setupEventListeners() {
        console.log('Welcome App event listeners setup');
    }

    showPage(page) {
        console.log('Showing page:', page);
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
        console.log('validateRegister called');
        console.log('window.appConfig:', window.appConfig);
        console.log('typeof window.appConfig:', typeof window.appConfig);
        
        if (!window.appConfig) {
            console.error('appConfig is not available!');
            alert('Configuration not loaded. Please refresh the page.');
            return;
        }
        
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
            console.log('Using service URL:', window.appConfig.getUsersServiceUrl());
            
            // Create user
            const userData = {
                username: username,
                email: email,
                password: password,
                phone: phone
            };

            const userResponse = await fetch(`${window.appConfig.getUsersServiceUrl()}`, {
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
        console.log('login called');
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value.trim();
        
        if (!username || !password) {
            alert("Please enter both username and password.");
            return;
        }

        try {
            console.log('Attempting to login user:', username);
            
            // Get all users and find the matching one
            const response = await fetch(`${window.appConfig.getUsersServiceUrl()}`);
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
        console.log('=== REDIRECT TO PLAN PAGE ===');
        console.log('Current user:', this.currentUser);
        console.log('Current URL:', window.location.href);
        console.log('Current pathname:', window.location.pathname);
        
        // Save user data to localStorage
        localStorage.setItem('planeetUser', JSON.stringify(this.currentUser));
        console.log('User data saved to localStorage');
        
        // Force redirect to plan.html
        const planUrl = window.location.origin + '/plan.html';
        console.log('Redirecting to:', planUrl);
        
        // Try multiple redirect methods
        try {
            window.location.href = planUrl;
        } catch (error) {
            console.error('Redirect error:', error);
            try {
                window.location.replace(planUrl);
            } catch (error2) {
                console.error('Replace error:', error2);
                // Last resort - try relative path
                window.location.href = 'plan.html';
            }
        }
    }

    // Test function to debug redirect issues
    testRedirect() {
        console.log('=== TEST REDIRECT ===');
        console.log('Current URL:', window.location.href);
        
        localStorage.setItem('planeetUser', JSON.stringify({
            username: 'testuser',
            email: 'test@example.com',
            phone: '+972 50-123-4567'
        }));
        
        const planUrl = window.location.origin + '/plan.html';
        console.log('Test redirecting to:', planUrl);
        
        window.location.href = planUrl;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Welcome App');
    window.welcomeApp = new WelcomeApp();
});

// Global functions for HTML onclick handlers
function showPage(page) {
    console.log('Global showPage called with:', page);
    window.welcomeApp.showPage(page);
}

function goHome() {
    console.log('Global goHome called');
    window.welcomeApp.goHome();
}

function validateRegister() {
    console.log('Global validateRegister called');
    window.welcomeApp.validateRegister();
}

function login() {
    console.log('Global login called');
    window.welcomeApp.login();
}

// Test function for debugging
function testRedirect() {
    console.log('Global testRedirect called');
    window.welcomeApp.testRedirect();
} 