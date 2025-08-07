// Dashboard Application Logic
class DashboardApp {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        this.loadUserData();
        this.populateDashboard();
        console.log('Dashboard App initialized');
    }

    loadUserData() {
        // Get user data from localStorage or URL parameters
        const userData = localStorage.getItem('planeetUser');
        if (userData) {
            this.currentUser = JSON.parse(userData);
        } else {
            // If no user data, redirect to login
            window.location.href = 'index.html';
        }
    }

    populateDashboard() {
        if (!this.currentUser) return;

        // Update user display name
        const userDisplayName = document.getElementById('userDisplayName');
        if (userDisplayName) {
            userDisplayName.textContent = this.currentUser.username || 'User';
        }

        // Update profile information
        this.updateProfileInfo();
    }

    updateProfileInfo() {
        if (!this.currentUser) return;

        // Update profile initials
        const profileInitials = document.getElementById('profileInitials');
        if (profileInitials) {
            const username = this.currentUser.username || 'U';
            profileInitials.textContent = username.charAt(0).toUpperCase();
        }

        // Update profile name
        const profileName = document.getElementById('profileName');
        if (profileName) {
            profileName.textContent = this.currentUser.username || 'User Name';
        }

        // Update profile email
        const profileEmail = document.getElementById('profileEmail');
        if (profileEmail) {
            profileEmail.textContent = this.currentUser.email || 'user@example.com';
        }

        // Update profile phone
        const profilePhone = document.getElementById('profilePhone');
        if (profilePhone) {
            profilePhone.textContent = this.currentUser.phone || '+972 50-123-4567';
        }
    }

    switchTab(tabName) {
        // Hide all tab panes
        const tabPanes = document.querySelectorAll('.tab-pane');
        tabPanes.forEach(pane => pane.classList.remove('active'));

        // Remove active class from all nav tabs
        const navTabs = document.querySelectorAll('.nav-tab');
        navTabs.forEach(tab => tab.classList.remove('active'));

        // Show selected tab pane
        const selectedPane = document.getElementById(`${tabName}-tab`);
        if (selectedPane) {
            selectedPane.classList.add('active');
        }

        // Add active class to selected nav tab
        const selectedTab = document.querySelector(`[onclick="switchTab('${tabName}')"]`);
        if (selectedTab) {
            selectedTab.classList.add('active');
        }
    }

    openSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.classList.add('active');
            this.populateSettings();
        }
    }

    closeSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    populateSettings() {
        if (!this.currentUser) return;

        // Populate settings form with current user data
        const settingsUsername = document.getElementById('settingsUsername');
        const settingsEmail = document.getElementById('settingsEmail');
        const settingsPhone = document.getElementById('settingsPhone');

        if (settingsUsername) settingsUsername.value = this.currentUser.username || '';
        if (settingsEmail) settingsEmail.value = this.currentUser.email || '';
        if (settingsPhone) settingsPhone.value = this.currentUser.phone || '';
    }

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

            // Here you would typically make an API call to update the user
            // For now, we'll just update the local user object
            this.currentUser = updatedUser;
            localStorage.setItem('planeetUser', JSON.stringify(updatedUser));

            alert('Settings saved successfully!');
            this.closeSettings();
            this.updateProfileInfo();
        } catch (error) {
            console.error('Settings save error:', error);
            alert('Failed to save settings. Please try again.');
        }
    }

    openPlanningForm() {
        // Placeholder for future planning functionality
        alert('Planning functionality will be implemented soon!');
    }

    logout() {
        // Clear user data and redirect to login
        localStorage.removeItem('planeetUser');
        window.location.href = 'index.html';
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardApp = new DashboardApp();
});

// Global functions for HTML onclick handlers
function switchTab(tabName) {
    window.dashboardApp.switchTab(tabName);
}

function openSettings() {
    window.dashboardApp.openSettings();
}

function closeSettings() {
    window.dashboardApp.closeSettings();
}

function saveSettings() {
    window.dashboardApp.saveSettings();
}

function openPlanningForm() {
    window.dashboardApp.openPlanningForm();
}

function logout() {
    window.dashboardApp.logout();
} 