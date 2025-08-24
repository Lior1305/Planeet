// Common utilities for Planeet UI
class CommonUtils {
    constructor() {
        this.currentUser = null;
    }

    // Get current user without redirecting
    getCurrentUser() {
        const userData = localStorage.getItem('planeetUser');
        if (userData) {
            this.currentUser = JSON.parse(userData);
            return this.currentUser;
        }
        return null;
    }

    // Get current user or redirect to login (for backward compatibility)
    getCurrentUserOrRedirect() {
        const userData = localStorage.getItem('planeetUser');
        if (userData) {
            this.currentUser = JSON.parse(userData);
            return this.currentUser;
        } else {
            // Redirect to login if no user data
            window.location.href = 'index.html';
            return null;
        }
    }

    // Check if user is authenticated for protected features
    isAuthenticated() {
        return this.currentUser !== null;
    }

    // Show login prompt for protected features
    showLoginPrompt(featureName = 'this feature') {
        const modal = document.createElement('div');
        modal.className = 'login-prompt-modal';
        modal.innerHTML = `
            <div class="login-prompt-content">
                <div class="login-prompt-header">
                    <h3>🔒 Login Required</h3>
                    <button class="close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
                </div>
                <div class="login-prompt-body">
                    <p>You need to be logged in to use ${featureName}.</p>
                    <div class="login-prompt-actions">
                        <a href="welcome.html" class="btn btn-primary">Login / Sign Up</a>
                        <button class="btn btn-ghost" onclick="this.parentElement.parentElement.parentElement.remove()">Maybe Later</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (modal.parentElement) {
                modal.remove();
            }
        }, 5000);
    }

    // Save user to localStorage
    saveUser(user) {
        this.currentUser = user;
        localStorage.setItem('planeetUser', JSON.stringify(user));
    }

    // API fetch wrapper with error handling
    async apiFetch(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API fetch error:', error);
            throw error;
        }
    }

    // Helper method to get service URL from config
    getServiceUrl(serviceName) {
        if (window.appConfig) {
            return window.appConfig.getServiceUrl(serviceName);
        }
        // Fallback to localhost if config is not available
        const fallbackUrls = {
            planning: 'http://localhost:8001',
            users: 'http://localhost:8080',
            venues: 'http://localhost:8000',
            outingProfile: 'http://localhost:5000'
        };
        return fallbackUrls[serviceName] || null;
    }

    // Helper method to make API calls to specific services
    async callService(serviceName, endpoint, options = {}) {
        const baseUrl = this.getServiceUrl(serviceName);
        if (!baseUrl) {
            throw new Error(`Service ${serviceName} not configured`);
        }
        
        const url = `${baseUrl}${endpoint}`;
        return this.apiFetch(url, options);
    }

    // Specific service call methods
    async callPlanningService(endpoint, options = {}) {
        return this.callService('planning', endpoint, options);
    }

    async callUsersService(endpoint, options = {}) {
        return this.callService('users', endpoint, options);
    }

    async callVenuesService(endpoint, options = {}) {
        return this.callService('venues', endpoint, options);
    }

    async callOutingProfileService(endpoint, options = {}) {
        return this.callService('outingProfile', endpoint, options);
    }

    // Update header with user info
    updateHeader() {
        const headerActions = document.getElementById('headerActions');
        if (headerActions) {
            if (this.currentUser) {
                // User is logged in - show settings and logout
                headerActions.innerHTML = `
                    <button class="btn btn-ghost" onclick="openSettings()">
                        <span class="icon">⚙️</span> Settings
                    </button>
                    <button class="btn btn-ghost" onclick="logout()">
                        <span class="icon">🚪</span> Logout
                    </button>
                `;
            } else {
                // User is not logged in - show login button
                headerActions.innerHTML = `
                    <a href="welcome.html" class="btn btn-primary">
                        <span class="icon">🔑</span> Login / Sign Up
                    </a>
                `;
            }
        }

        // Highlight active nav tab based on current page
        this.highlightActiveNav();
    }

    // Highlight active navigation tab
    highlightActiveNav() {
        const currentPath = window.location.pathname;
        const navTabs = document.querySelectorAll('.nav-tab');
        
        navTabs.forEach(tab => {
            tab.classList.remove('active');
            if (tab.getAttribute('href') === currentPath.split('/').pop()) {
                tab.classList.add('active');
            }
        });
    }

    // Load and inject header component
    async loadHeader() {
        try {
            const headerResponse = await fetch('components/header.html');
            const headerHtml = await headerResponse.text();
            
            const headerMount = document.getElementById('appHeader');
            if (headerMount) {
                headerMount.innerHTML = headerHtml;
                this.updateHeader();
            }
        } catch (error) {
            console.error('Failed to load header:', error);
        }
    }

    // Load and inject settings modal component
    async loadSettingsModal() {
        try {
            const modalResponse = await fetch('components/settings-modal.html');
            const modalHtml = await modalResponse.text();
            
            const modalMount = document.getElementById('settingsModalMount');
            if (modalMount) {
                modalMount.innerHTML = modalHtml;
            }
        } catch (error) {
            console.error('Failed to load settings modal:', error);
        }
    }

    // Logout function
    logout() {
        localStorage.removeItem('planeetUser');
        window.location.href = 'plan.html';
    }

    // Open settings modal
    openSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.classList.add('active');
            this.populateSettings();
        }
    }

    // Close settings modal
    closeSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    // Populate settings form with current user data
    populateSettings() {
        if (!this.currentUser) return;

        const settingsUsername = document.getElementById('settingsUsername');
        const settingsEmail = document.getElementById('settingsEmail');
        const settingsPhone = document.getElementById('settingsPhone');

        if (settingsUsername) settingsUsername.value = this.currentUser.username || '';
        if (settingsEmail) settingsEmail.value = this.currentUser.email || '';
        if (settingsPhone) settingsPhone.value = this.currentUser.phone || '';
    }

    // Save settings
    async saveSettings() {
        if (!this.currentUser) return;

        const username = document.getElementById('settingsUsername').value.trim();
        const email = document.getElementById('settingsEmail').value.trim();
        const phone = document.getElementById('settingsPhone').value.trim();
        const password = document.getElementById('settingsPassword').value.trim();

        // Basic validation
        if (!username || !email) {
            alert("Username and email are required.");
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert("Please enter a valid email address.");
            return;
        }

        try {
            // Update user data
            const updatedUser = {
                ...this.currentUser,
                username: username,
                email: email,
                phone: phone
            };

            // If password is provided, update it
            if (password) {
                updatedUser.password = password;
            }

            // Update local user object
            this.saveUser(updatedUser);

            alert('Settings saved successfully!');
            this.closeSettings();
            
            // Refresh page to show updated info
            window.location.reload();
        } catch (error) {
            console.error('Settings save error:', error);
            alert('Failed to save settings. Please try again.');
        }
    }
}

// Global instance
window.commonUtils = new CommonUtils();

// Global functions for HTML onclick handlers
function logout() {
    window.commonUtils.logout();
}

function openSettings() {
    window.commonUtils.openSettings();
}

function closeSettings() {
    window.commonUtils.closeSettings();
}

function saveSettings() {
    window.commonUtils.saveSettings();
}
