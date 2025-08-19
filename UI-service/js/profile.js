// Profile Page Controller
class ProfilePageController {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    async init() {
        // Load user and redirect if not authenticated
        this.currentUser = commonUtils.getCurrentUserOrRedirect();
        if (!this.currentUser) return;

        // Load components
        await commonUtils.loadHeader();
        await commonUtils.loadSettingsModal();
        
        // Setup profile display
        this.updateProfileInfo();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('Profile Page Controller initialized');
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
