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
        console.log('🔍 openPlanningForm() called in DashboardApp class');
        console.log('🔍 Looking for planningModal element...');
        
        const modal = document.getElementById('planningModal');
        console.log('🔍 Modal element found:', modal);
        
        if (modal) {
            console.log('🔍 Adding active class to modal');
            modal.classList.add('active');
            console.log('🔍 Modal classes after adding active:', modal.className);
            this.setupPlanningForm();
        } else {
            console.error('❌ planningModal element not found!');
            console.error('❌ Available elements with "planning" in ID:');
            const allElements = document.querySelectorAll('[id*="planning"]');
            allElements.forEach(el => console.log('   -', el.id, el.tagName));
        }
    }

    closePlanningForm() {
        const modal = document.getElementById('planningModal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    setupPlanningForm() {
        // Set default date to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dateInput = document.getElementById('planDate');
        if (dateInput) {
            dateInput.value = tomorrow.toISOString().split('T')[0];
        }

        // Set default time to current time + 1 hour
        const timeInput = document.getElementById('planTime');
        if (timeInput) {
            const now = new Date();
            now.setHours(now.getHours() + 1);
            timeInput.value = now.toTimeString().slice(0, 5);
        }

        // Initialize multi-step form
        this.currentStep = 1;
        this.totalSteps = 6;
        this.updateProgressIndicator();

        // Add form submit handler
        const form = document.getElementById('planningForm');
        if (form) {
            form.onsubmit = (e) => this.handlePlanningFormSubmit(e);
        }

        // Add city input handler for geocoding
        const cityInput = document.getElementById('city');
        if (cityInput) {
            cityInput.addEventListener('blur', () => this.handleCityInput(cityInput.value));
        }
    }

    updateProgressIndicator() {
        const progressSteps = document.querySelectorAll('.progress-step');
        progressSteps.forEach((step, index) => {
            const stepNumber = index + 1;
            step.classList.remove('active', 'completed');
            
            if (stepNumber === this.currentStep) {
                step.classList.add('active');
            } else if (stepNumber < this.currentStep) {
                step.classList.add('completed');
            }
        });
    }

    showStep(stepNumber) {
        console.log(`🔍 showStep(${stepNumber}) called`);
        
        // Hide all steps
        const formSteps = document.querySelectorAll('.form-step');
        console.log(`🔍 Found ${formSteps.length} form steps`);
        formSteps.forEach(step => {
            step.classList.remove('active');
            console.log(`🔍 Step ${step.dataset.step}: removed active class`);
        });
        
        // Show current step
        const currentStepElement = document.querySelector(`[data-step="${stepNumber}"]`);
        console.log(`🔍 Looking for step ${stepNumber}, found:`, currentStepElement);
        
        if (currentStepElement) {
            currentStepElement.classList.add('active');
            console.log(`🔍 Step ${stepNumber} now has active class`);
        } else {
            console.error(`❌ Could not find step element with data-step="${stepNumber}"`);
            // Debug: show all available steps
            const allSteps = document.querySelectorAll('.form-step');
            allSteps.forEach((step, index) => {
                console.log(`   Step ${index + 1}: data-step="${step.dataset.step}"`);
            });
        }
        
        // Update progress indicator
        this.currentStep = stepNumber;
        this.updateProgressIndicator();
        console.log(`🔍 Current step updated to: ${this.currentStep}`);
    }

    nextStep() {
        console.log(`🔍 nextStep() called from step ${this.currentStep}`);
        if (this.currentStep < this.totalSteps) {
            console.log(`🔍 Validating step ${this.currentStep} before proceeding...`);
            // Validate current step before proceeding
            if (this.validateCurrentStep()) {
                console.log(`🔍 Validation passed, moving to step ${this.currentStep + 1}`);
                this.showStep(this.currentStep + 1);
            } else {
                console.log(`❌ Validation failed for step ${this.currentStep}`);
            }
        } else {
            console.log(`🔍 Already at last step (${this.currentStep}/${this.totalSteps})`);
        }
    }

    // Temporary test function to bypass validation
    nextStepNoValidation() {
        console.log(`🧪 nextStepNoValidation() called from step ${this.currentStep}`);
        if (this.currentStep < this.totalSteps) {
            console.log(`🧪 Bypassing validation, moving to step ${this.currentStep + 1}`);
            this.showStep(this.currentStep + 1);
        }
    }

    // Test function to show specific step
    showStepTest(stepNumber) {
        console.log(`🧪 showStepTest(${stepNumber}) called`);
        this.showStep(stepNumber);
    }

    prevStep() {
        console.log(`🔍 prevStep() called from step ${this.currentStep}`);
        if (this.currentStep > 1) {
            console.log(`🔍 Moving to step ${this.currentStep - 1}`);
            this.showStep(this.currentStep - 1);
        } else {
            console.log(`🔍 Already at first step`);
        }
    }

    validateCurrentStep() {
        console.log(`🔍 validateCurrentStep() called for step ${this.currentStep}`);
        const currentStepElement = document.querySelector(`[data-step="${this.currentStep}"]`);
        if (!currentStepElement) {
            console.error(`❌ Could not find current step element for step ${this.currentStep}`);
            return true; // Allow progression if we can't find the element
        }

        // Get all required fields in current step
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        console.log(`🔍 Found ${requiredFields.length} required fields in step ${this.currentStep}`);
        
        let isValid = true;
        let firstInvalidField = null;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                console.log(`❌ Required field ${field.id} is empty`);
                field.style.borderColor = '#dc3545';
                if (!firstInvalidField) firstInvalidField = field;
                isValid = false;
            } else {
                console.log(`✅ Required field ${field.id} is valid: "${field.value}"`);
                field.style.borderColor = '#e1e5e9';
            }
        });

        // Special validation for venue types (step 4)
        if (this.currentStep === 4) {
            const venueTypeCheckboxes = currentStepElement.querySelectorAll('input[name="venueTypes"]:checked');
            if (venueTypeCheckboxes.length === 0) {
                console.log(`❌ No venue types selected in step 4`);
                alert('Please select at least one venue type.');
                isValid = false;
            } else {
                console.log(`✅ ${venueTypeCheckboxes.length} venue types selected`);
            }
        }

        // Special validation for group size (step 1)
        if (this.currentStep === 1) {
            const groupSizeField = document.getElementById('groupSize');
            if (groupSizeField && (parseInt(groupSizeField.value) < 1 || parseInt(groupSizeField.value) > 20)) {
                console.log(`❌ Invalid group size: ${groupSizeField.value}`);
                alert('Group size must be between 1 and 20.');
                groupSizeField.style.borderColor = '#dc3545';
                isValid = false;
            } else if (groupSizeField) {
                console.log(`✅ Group size is valid: ${groupSizeField.value}`);
            }
        }

        if (!isValid && firstInvalidField) {
            firstInvalidField.focus();
        }

        console.log(`🔍 Step ${this.currentStep} validation result: ${isValid ? 'PASSED' : 'FAILED'}`);
        return isValid;
    }

    async handleCityInput(cityName) {
        if (!cityName.trim()) return;

        try {
            // Try to get coordinates for the city
            const coordinates = await this.geocodeCity(cityName);
            if (coordinates) {
                document.getElementById('latitude').value = coordinates.lat;
                document.getElementById('longitude').value = coordinates.lng;
            }
        } catch (error) {
            console.log('Could not geocode city:', cityName);
        }
    }

    async geocodeCity(cityName) {
        // Simple geocoding for common Israeli cities
        const cityCoordinates = {
            'tel aviv': { lat: 32.0853, lng: 34.7818 },
            'jerusalem': { lat: 31.7683, lng: 35.2137 },
            'haifa': { lat: 32.7940, lng: 34.9896 },
            'beer sheva': { lat: 31.2518, lng: 34.7913 },
            'eilat': { lat: 29.5577, lng: 34.9519 },
            'netanya': { lat: 32.3328, lng: 34.8600 },
            'ashdod': { lat: 31.8044, lng: 34.6500 },
            'rishon lezion': { lat: 31.9600, lng: 34.8000 },
            'petah tikva': { lat: 32.0853, lng: 34.8860 },
            'holon': { lat: 32.0167, lng: 34.7792 }
        };

        const normalizedCity = cityName.toLowerCase().trim();
        return cityCoordinates[normalizedCity] || null;
    }

    async handlePlanningFormSubmit(event) {
        event.preventDefault();
        
        try {
            // Show loading state
            const submitBtn = event.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="icon">⏳</span> Creating Plan...';
            submitBtn.disabled = true;

            // Collect form data
            const formData = this.collectPlanningFormData();
            
            // Validate form data
            if (!this.validatePlanningFormData(formData)) {
                return;
            }

            // Create plan via Planning Service
            const planResponse = await this.createPlan(formData);
            
            // Show success message
            alert(`Plan created successfully! Plan ID: ${planResponse.plan_id}`);
            
            // Close modal and refresh dashboard
            this.closePlanningForm();
            this.refreshDashboard();
            
        } catch (error) {
            console.error('Error creating plan:', error);
            alert('Failed to create plan. Please try again.');
        } finally {
            // Reset button state
            const submitBtn = event.target.querySelector('button[type="submit"]');
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    collectPlanningFormData() {
        // Get selected venue types
        const venueTypeCheckboxes = document.querySelectorAll('input[name="venueTypes"]:checked');
        const venueTypes = Array.from(venueTypeCheckboxes).map(cb => cb.value);

        // Get form values
        const formData = {
            planName: document.getElementById('planName').value,
            groupSize: parseInt(document.getElementById('groupSize').value),
            city: document.getElementById('city').value,
            address: document.getElementById('address').value,
            latitude: parseFloat(document.getElementById('latitude').value) || null,
            longitude: parseFloat(document.getElementById('longitude').value) || null,
            planDate: document.getElementById('planDate').value,
            planTime: document.getElementById('planTime').value,
            durationHours: parseFloat(document.getElementById('durationHours').value) || null,
            venueTypes: venueTypes,
            budgetRange: document.getElementById('budgetRange').value || null,
            minRating: parseFloat(document.getElementById('minRating').value) || null,
            radiusKm: parseFloat(document.getElementById('radiusKm').value),
            maxVenues: parseInt(document.getElementById('maxVenues').value),
            dietaryRestrictions: document.getElementById('dietaryRestrictions').value || null,
            accessibilityNeeds: document.getElementById('accessibilityNeeds').value || null,
            amenities: document.getElementById('amenities').value || null
        };

        return formData;
    }

    validatePlanningFormData(formData) {
        // Check required fields
        if (!formData.planName.trim()) {
            alert('Please enter a plan name.');
            return false;
        }

        if (!formData.city.trim()) {
            alert('Please enter a city.');
            return false;
        }

        if (formData.venueTypes.length === 0) {
            alert('Please select at least one venue type.');
            return false;
        }

        if (formData.groupSize < 1) {
            alert('Group size must be at least 1.');
            return false;
        }

        return true;
    }

    async createPlan(formData) {
        // Prepare the plan request for the Planning Service
        const planRequest = {
            user_id: this.currentUser.id || 'default_user',
            plan_id: `plan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            venue_types: formData.venueTypes,
            location: {
                latitude: formData.latitude || 32.0853, // Default to Tel Aviv if no coordinates
                longitude: formData.longitude || 34.7818,
                address: formData.address,
                city: formData.city,
                country: 'Israel'
            },
            radius_km: formData.radiusKm,
            max_venues: formData.maxVenues,
            use_personalization: true,
            include_links: true,
            date: new Date(`${formData.planDate}T${formData.planTime}`).toISOString(),
            duration_hours: formData.durationHours,
            group_size: formData.groupSize,
            budget_range: formData.budgetRange,
            min_rating: formData.minRating,
            amenities: formData.amenities ? formData.amenities.split(',').map(a => a.trim()) : null,
            dietary_restrictions: formData.dietaryRestrictions ? formData.dietaryRestrictions.split(',').map(d => d.trim()) : null,
            accessibility_needs: formData.accessibilityNeeds ? formData.accessibilityNeeds.split(',').map(a => a.trim()) : null
        };

        // Make API call to Planning Service
        const response = await fetch('http://localhost:8001/v1/plans/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(planRequest)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    refreshDashboard() {
        // Refresh dashboard data after plan creation
        // This could include updating recent plans, statistics, etc.
        console.log('Dashboard refreshed');
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

function closePlanningForm() {
    window.dashboardApp.closePlanningForm();
}

function logout() {
    window.dashboardApp.logout();
}

function nextStep() {
    window.dashboardApp.nextStep();
}

function prevStep() {
    window.dashboardApp.prevStep();
}

// Test functions for debugging
function nextStepNoValidation() {
    window.dashboardApp.nextStepNoValidation();
}

function showStepTest(stepNumber) {
    window.dashboardApp.showStepTest(stepNumber);
}

function debugCurrentStep() {
    console.log(`🔍 Current step: ${window.dashboardApp.currentStep}`);
    console.log(`🔍 Total steps: ${window.dashboardApp.totalSteps}`);
    
    const allSteps = document.querySelectorAll('.form-step');
    console.log(`🔍 Found ${allSteps.length} form steps:`);
    allSteps.forEach((step, index) => {
        const isActive = step.classList.contains('active');
        console.log(`   Step ${index + 1}: data-step="${step.dataset.step}", active: ${isActive}`);
    });
}

// Test function to debug modal issues
function testModal() {
    console.log('🧪 Test Modal function called');
    console.log('🧪 Checking if planningModal element exists...');
    
    const modal = document.getElementById('planningModal');
    console.log('🧪 Modal element:', modal);
    
    if (modal) {
        console.log('🧪 Modal found! Adding active class...');
        modal.classList.add('active');
        console.log('🧪 Modal classes after adding active:', modal.className);
        console.log('🧪 Modal computed styles:');
        console.log('   - display:', window.getComputedStyle(modal).display);
        console.log('   - opacity:', window.getComputedStyle(modal).opacity);
        console.log('   - visibility:', window.getComputedStyle(modal).visibility);
        console.log('   - z-index:', window.getComputedStyle(modal).zIndex);
    } else {
        console.error('🧪 Modal NOT found!');
        console.log('🧪 All elements with "planning" in ID:');
        const allElements = document.querySelectorAll('[id*="planning"]');
        allElements.forEach(el => console.log('   -', el.id, el.tagName));
        
        console.log('🧪 All elements with "modal" in ID:');
        const modalElements = document.querySelectorAll('[id*="modal"]');
        modalElements.forEach(el => console.log('   -', el.id, el.tagName));
    }
} 