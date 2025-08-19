// History Page Controller
class HistoryPageController {
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
            // Setup outings display for authenticated users
            this.loadOutingsHistory();
        } else {
            // Show login prompt for unauthenticated users
            this.showLoginPrompt();
        }
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('History Page Controller initialized');
    }

    setupEventListeners() {
        // Add any page-specific event listeners here
        console.log('History page event listeners setup');
    }

    async loadOutingsHistory() {
        // This would typically fetch from the backend
        // For now, showing empty state
        this.showEmptyState();
        
        // TODO: Implement actual outings loading when backend is available
        // try {
        //     const outings = await commonUtils.apiFetch(`http://localhost:8001/v1/plans/user/${this.currentUser.id}`);
        //     if (outings && outings.length > 0) {
        //         this.displayOutings(outings);
        //     } else {
        //         this.showEmptyState();
        //     }
        // } catch (error) {
        //     console.error('Failed to load outings:', error);
        //     this.showEmptyState();
        // }
    }

    showEmptyState() {
        const outingsList = document.getElementById('outingsList');
        if (outingsList) {
            outingsList.innerHTML = `
                <div class="no-outings">
                    <span class="icon">📋</span>
                    <h3>No outings yet</h3>
                    <p>Start planning your first adventure!</p>
                    <a href="plan.html" class="btn btn-primary">
                        Plan Your First Outing
                    </a>
                </div>
            `;
        }
    }

    showLoginPrompt() {
        const outingsList = document.getElementById('outingsList');
        if (outingsList) {
            outingsList.innerHTML = `
                <div class="login-required">
                    <div class="login-required-content">
                        <span class="icon">🔒</span>
                        <h2>History Access Required</h2>
                        <p>You need to be logged in to view your outing history.</p>
                        <div class="login-actions">
                            <a href="welcome.html" class="btn btn-primary">Login / Sign Up</a>
                            <a href="plan.html" class="btn btn-ghost">Start Planning</a>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    displayOutings(outings) {
        const outingsList = document.getElementById('outingsList');
        if (!outingsList) return;

        const outingsHtml = outings.map(outing => `
            <div class="outing-item">
                <div class="outing-header">
                    <h3>${outing.plan_name || 'Untitled Plan'}</h3>
                    <span class="outing-date">${new Date(outing.date).toLocaleDateString()}</span>
                </div>
                <div class="outing-details">
                    <p><strong>Location:</strong> ${outing.location?.city || 'Unknown'}</p>
                    <p><strong>Group Size:</strong> ${outing.group_size || 'Unknown'}</p>
                    <p><strong>Venue Types:</strong> ${(outing.venue_types || []).join(', ')}</p>
                </div>
                <div class="outing-actions">
                    <button class="btn btn-secondary" onclick="viewOutingDetails('${outing.plan_id}')">
                        View Details
                    </button>
                </div>
            </div>
        `).join('');

        outingsList.innerHTML = outingsHtml;
    }
}

// Initialize the history page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.historyPageController = new HistoryPageController();
});

// Global function for viewing outing details (placeholder)
function viewOutingDetails(planId) {
    console.log('Viewing details for plan:', planId);
    // TODO: Implement outing details view
    alert('Outing details view not yet implemented');
}
