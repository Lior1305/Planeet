// Profile Page Controller
class ProfilePageController {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    async init() {
        // Load user data without requiring authentication
        this.currentUser = commonUtils.getCurrentUser();
        
        // Load components
        await commonUtils.loadHeader();
        if (this.currentUser) {
            await commonUtils.loadSettingsModal();
            // Setup profile display for authenticated users
            this.updateProfileInfo();
        } else {
            // Show login prompt for unauthenticated users
            this.showLoginPrompt();
        }
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('Profile Page Controller initialized');
    }

    showLoginPrompt() {
        const profileContent = document.querySelector('.profile-content');
        if (profileContent) {
            profileContent.innerHTML = `
                <div class="login-required">
                    <div class="login-required-content">
                        <span class="icon">🔒</span>
                        <h2>Profile Access Required</h2>
                        <p>You need to be logged in to view and manage your profile.</p>
                        <div class="login-actions">
                            <a href="welcome.html" class="btn btn-primary">Login / Sign Up</a>
                            <a href="plan.html" class="btn btn-ghost">Explore Planning</a>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    setupEventListeners() {
        // Add any page-specific event listeners here
        console.log('Profile page event listeners setup');
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

        // Update profile stats (placeholder values for now)
        this.updateProfileStats();
    }

    updateProfileStats() {
        // These would typically come from the backend
        // For now, using placeholder values
        const totalOutings = document.getElementById('totalOutings');
        if (totalOutings) {
            totalOutings.textContent = '0'; // Would be fetched from backend
        }

        const favoriteCity = document.getElementById('favoriteCity');
        if (favoriteCity) {
            favoriteCity.textContent = '-'; // Would be calculated from user's plans
        }

        const memberSince = document.getElementById('memberSince');
        if (memberSince) {
            memberSince.textContent = '2024'; // Would come from user registration date
        }
    }
}

// Initialize the profile page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.profilePageController = new ProfilePageController();
});
