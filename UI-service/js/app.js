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
        ['home', 'login', 'register', 'landing', 'welcome', 'newPlan'].forEach(p => {
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
            // Create user
            const userData = {
                username: username,
                email: email,
                password: password
            };

            const userResponse = await fetch('http://localhost:8080/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });

            if (userResponse.ok) {
                const user = await userResponse.json();
                this.currentUser = user;
                this.showPage('welcome');
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
            // Get all users and find the matching one
            const response = await fetch('http://localhost:8080/users');
            if (response.ok) {
                const users = await response.json();
                const user = users.find(u => u.username === username && u.password === password);
                
                if (user) {
                    this.currentUser = user;
                    this.showPage('welcome');
                } else {
                    alert("Invalid username or password.");
                }
            } else {
                alert("Login failed. Please try again.");
            }
        } catch (error) {
            console.error('Login error:', error);
            alert("Connection error. Please check if all services are running.");
        }
    }

    validateNewPlan() {
        const inputs = document.querySelectorAll('#newPlan .input-field');
        let isValid = true;
        let missingFields = [];

        inputs.forEach((input) => {
            if (input.tagName !== 'TEXTAREA' && !input.value.trim()) {
                isValid = false;
                missingFields.push(input.placeholder || 'field');
            }
        });

        if (!isValid) {
            alert(`Please fill in all required fields: ${missingFields.join(', ')}`);
        } else {
            this.showPage('landing');
        }
    }

    logout() {
        this.currentUser = null;
        this.showPage('home');
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

function validateNewPlan() {
    window.planeetApp.validateNewPlan();
}

function logout() {
    window.planeetApp.logout();
} 