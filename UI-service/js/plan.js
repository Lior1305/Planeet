// Plan Page Controller
class PlanPageController {
    constructor() {
        this.currentUser = null;
        this.currentStep = 1;
        this.totalSteps = 6;
        this.init();
    }

    async init() {
        // Load user and redirect if not authenticated
        this.currentUser = commonUtils.getCurrentUserOrRedirect();
        if (!this.currentUser) return;

        // Load components
        await commonUtils.loadHeader();
        await commonUtils.loadSettingsModal();
        
        // Load planning modal
        await this.loadPlanningModal();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('Plan Page Controller initialized');
    }

    async loadPlanningModal() {
        try {
            const modalResponse = await fetch('components/planning-modal.html');
            const modalHtml = await modalResponse.text();
            
            const modalMount = document.getElementById('planningModalMount');
            if (modalMount) {
                modalMount.innerHTML = modalHtml;
                this.setupPlanningForm();
            }
        } catch (error) {
            console.error('Failed to load planning modal:', error);
        }
    }

    setupEventListeners() {
        // Add any page-specific event listeners here
        console.log('Plan page event listeners setup');
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

    openPlanningForm() {
        console.log('🔍 openPlanningForm() called');
        const modal = document.getElementById('planningModal');
        console.log('🔍 Modal element found:', modal);
        
        if (modal) {
            console.log('🔍 Adding active class to modal');
            modal.classList.add('active');
            console.log('🔍 Modal classes after adding active:', modal.className);
            
            // Reset to step 1 and setup form
            this.currentStep = 1;
            this.showStep(1);
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
            // Reset to step 1 when closing
            this.currentStep = 1;
            this.showStep(1);
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
        
        // Hide all steps first
        const formSteps = document.querySelectorAll('.form-step');
        console.log(`🔍 Found ${formSteps.length} form steps`);
        formSteps.forEach(step => {
            step.classList.remove('active');
            console.log(`🔍 Step ${step.dataset.step}: removed active class`);
        });
        
        // Force a small delay to ensure DOM updates
        setTimeout(() => {
            // Show current step - specifically look for form-step elements
            const currentStepElement = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
            console.log(`🔍 Looking for form step ${stepNumber}, found:`, currentStepElement);
            
            if (currentStepElement) {
                currentStepElement.classList.add('active');
                console.log(`🔍 Form step ${stepNumber} now has active class`);
                
                // Scroll to top of the step content
                currentStepElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                console.error(`❌ Could not find form step element with data-step="${stepNumber}"`);
                // Debug: show all available form steps
                const allSteps = document.querySelectorAll('.form-step');
                allSteps.forEach((step, index) => {
                    console.log(`   Form Step ${index + 1}: data-step="${step.dataset.step}"`);
                });
            }
            
            // Update progress indicator
            this.currentStep = stepNumber;
            this.updateProgressIndicator();
            console.log(`🔍 Current step updated to: ${this.currentStep}`);
        }, 50);
    }

    nextStep() {
        console.log(`🔍 nextStep() called from step ${this.currentStep}`);
        console.log(`🔍 Total steps: ${this.totalSteps}`);
        
        if (this.currentStep < this.totalSteps) {
            console.log(`🔍 Validating step ${this.currentStep} before proceeding...`);
            // Validate current step before proceeding
            if (this.validateCurrentStep()) {
                const nextStepNumber = this.currentStep + 1;
                console.log(`🔍 Validation passed, moving to step ${nextStepNumber}`);
                this.showStep(nextStepNumber);
            } else {
                console.log(`❌ Validation failed for step ${this.currentStep}`);
            }
        } else {
            console.log(`🔍 Already at last step (${this.currentStep}/${this.totalSteps})`);
        }
    }

    prevStep() {
        console.log(`🔍 prevStep() called from step ${this.currentStep}`);
        if (this.currentStep > 1) {
            this.showStep(this.currentStep - 1);
        }
    }

    validateCurrentStep() {
        console.log(`🔍 validateCurrentStep() called for step ${this.currentStep}`);
        const currentStepElement = document.querySelector(`.form-step[data-step="${this.currentStep}"]`);
        if (!currentStepElement) {
            console.error(`❌ Could not find current form step element for step ${this.currentStep}`);
            return true;
        }

        // Get all required fields in current step
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        let isValid = true;
        let firstInvalidField = null;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = '#dc3545';
                if (!firstInvalidField) firstInvalidField = field;
                isValid = false;
            } else {
                field.style.borderColor = '#e1e5e9';
            }
        });

        // Special validation for venue types (step 4)
        if (this.currentStep === 4) {
            const venueTypeCheckboxes = currentStepElement.querySelectorAll('input[name="venueTypes"]:checked');
            if (venueTypeCheckboxes.length === 0) {
                alert('Please select at least one venue type.');
                isValid = false;
            }
        }

        // Special validation for group size (step 1)
        if (this.currentStep === 1) {
            const groupSizeField = document.getElementById('groupSize');
            if (groupSizeField && (parseInt(groupSizeField.value) < 1 || parseInt(groupSizeField.value) > 20)) {
                alert('Group size must be between 1 and 20.');
                groupSizeField.style.borderColor = '#dc3545';
                isValid = false;
            }
        }

        if (!isValid && firstInvalidField) {
            firstInvalidField.focus();
        }

        return isValid;
    }

    async handleCityInput(cityName) {
        if (!cityName.trim()) return;

        try {
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
            
            // Close modal and refresh page
            this.closePlanningForm();
            window.location.reload();
            
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
}

// Initialize the plan page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.planPageController = new PlanPageController();
});

// Global functions for HTML onclick handlers
function openPlanningForm() {
    window.planPageController.openPlanningForm();
}

function closePlanningForm() {
    window.planPageController.closePlanningForm();
}

function nextStep() {
    window.planPageController.nextStep();
}

function prevStep() {
    window.planPageController.prevStep();
}

// Debug functions for testing
function testStep(stepNumber) {
    console.log(`🧪 Testing step ${stepNumber}`);
    if (window.planPageController) {
        window.planPageController.showStep(stepNumber);
    } else {
        console.error('❌ planPageController not found');
    }
}

function debugCurrentStep() {
    if (window.planPageController) {
        console.log(`🔍 Current step: ${window.planPageController.currentStep}`);
        console.log(`🔍 Total steps: ${window.planPageController.totalSteps}`);
        
        const activeStep = document.querySelector('.form-step.active');
        console.log(`🔍 Active step element:`, activeStep);
        
        const allSteps = document.querySelectorAll('.form-step');
        console.log(`🔍 All steps found:`, allSteps.length);
        allSteps.forEach((step, index) => {
            console.log(`   Step ${index + 1}: data-step="${step.dataset.step}", active: ${step.classList.contains('active')}`);
        });
    } else {
        console.error('❌ planPageController not found');
    }
}
