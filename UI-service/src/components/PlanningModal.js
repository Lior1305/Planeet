import React, { useState, useEffect } from 'react';
import planningService from '../services/planningService.js';
import userService from '../services/userService.js';
import outingProfileService from '../services/outingProfileService.js';
import GeneratedPlansModal from './GeneratedPlansModal.js';
import CustomTimePicker from './CustomTimePicker.js';

const PlanningModal = ({ isOpen, onClose, onPlanCreated }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState(planningService.getDefaultFormData());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [cities, setCities] = useState([]);
  const [generatedPlans, setGeneratedPlans] = useState(null);
  const [showPlans, setShowPlans] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);

  const totalSteps = 6;
  const currentUser = userService.getCurrentUser();

  useEffect(() => {
    if (isOpen) {
      setFormData(planningService.getDefaultFormData());
      setCurrentStep(1);
      setError('');
      setGeneratedPlans(null);
      setShowPlans(false);
      // Load cities immediately (no async needed)
      setCities(planningService.getAllCities());
    }
  }, [isOpen]);

  // Function to validate and adjust time to 15-minute increments
  const validateAndAdjustTime = (timeString) => {
    if (!timeString) return timeString;
    
    try {
      const [hours, minutes] = timeString.split(':').map(Number);
      if (isNaN(hours) || isNaN(minutes)) return timeString;
      
      // Round minutes to nearest 15-minute increment
      const adjustedMinutes = Math.round(minutes / 15) * 15;
      
      // Handle overflow (e.g., 45 -> 60 should become next hour)
      let adjustedHours = hours;
      if (adjustedMinutes === 60) {
        adjustedHours = (hours + 1) % 24;
        adjustedMinutes = 0;
      }
      
      // Format back to HH:MM
      return `${adjustedHours.toString().padStart(2, '0')}:${adjustedMinutes.toString().padStart(2, '0')}`;
    } catch {
      return timeString;
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      if (name === 'venueTypes') {
        const updatedVenueTypes = checked
          ? [...formData.venueTypes, value]
          : formData.venueTypes.filter(type => type !== value);
        
        setFormData(prev => {
          const newVenueTypes = updatedVenueTypes;
          let newMaxVenues = prev.maxVenues;
          
          // Adjust maxVenues if it exceeds the new venue types count
          if (newMaxVenues > newVenueTypes.length) {
            newMaxVenues = Math.max(1, newVenueTypes.length);
          }
          
          return { 
            ...prev, 
            venueTypes: newVenueTypes,
            maxVenues: newMaxVenues
          };
        });
      }
    } else {
      // Special handling for time input to enforce 15-minute increments
      if (name === 'planTime') {
        const adjustedTime = validateAndAdjustTime(value);
        setFormData(prev => ({ ...prev, [name]: adjustedTime }));
      } else {
        setFormData(prev => ({ ...prev, [name]: value }));
      }
    }
    
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleCityFocus = () => {
    // Clear any previous city selection when focusing on the input
    if (formData.city && !cities.find(city => 
      city.value === formData.city || city.displayName === formData.city
    )) {
      // If current city is not in predefined list, keep it as custom city
      // but ensure coordinates are set
      if (!formData.latitude || !formData.longitude) {
        setFormData(prev => ({
          ...prev,
          latitude: 32.0853,
          longitude: 34.7818
        }));
      }
    }
  };

  const handleCityChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Auto-set coordinates when city is selected
    if (name === 'city' && value) {
      // First try to find exact match in predefined cities
      const selectedCity = cities.find(city => 
        city.value === value || city.displayName === value
      );
      
      if (selectedCity && selectedCity.lat && selectedCity.lng) {
        // Use predefined city coordinates
        setFormData(prev => ({
          ...prev,
          latitude: selectedCity.lat,
          longitude: selectedCity.lng
        }));
      } else {
        // For custom cities, we'll set default coordinates (can be updated later)
        // Default to Tel Aviv area as fallback
        setFormData(prev => ({
          ...prev,
          latitude: 32.0853,
          longitude: 34.7818
        }));
      }
    }
    
    // Clear error when user makes a selection
    if (error) setError('');
  };

  const validateCurrentStep = () => {
    switch (currentStep) {
      case 1:
        if (!formData.planName.trim()) {
          setError('Please enter a plan name.');
          return false;
        }
        if (formData.groupSize < 1 || formData.groupSize > 20) {
          setError('Group size must be between 1 and 20.');
          return false;
        }
        break;
      case 2:
        if (!formData.city.trim()) {
          setError('Please enter a city.');
          return false;
        }
        break;
      case 3:
        if (!formData.planDate) {
          setError('Please select a date.');
          return false;
        }
        if (!formData.planTime) {
          setError('Please select a time.');
          return false;
        }
        break;
      case 4:
        if (formData.venueTypes.length === 0) {
          setError('Please select at least one venue type.');
          return false;
        }
        break;
             case 5:
         if (formData.radiusKm < 1) {
           setError('Radius must be at least 1 km.');
           return false;
         }
         if (formData.maxVenues < 1) {
           setError('Maximum venues must be at least 1.');
           return false;
         }
         if (formData.maxVenues > formData.venueTypes.length) {
           setError(`Maximum venues cannot exceed the number of selected venue types (${formData.venueTypes.length}).`);
           return false;
         }
         break;
      default:
        break;
    }
    return true;
  };

  const nextStep = () => {
    if (validateCurrentStep()) {
      setError('');
      if (currentStep < totalSteps) {
        setCurrentStep(currentStep + 1);
      }
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    setLoadingStep(0);

    try {
      // Final validation
      const validation = planningService.validatePlanningFormData(formData);
      if (!validation.isValid) {
        setError(validation.error);
        return;
      }

      // Show progress steps with minimal delays for better UX
      setLoadingStep(1); // Analyzing preferences
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setLoadingStep(2); // Discovering venues
      await new Promise(resolve => setTimeout(resolve, 400));
      
      setLoadingStep(3); // Generating plans
      await new Promise(resolve => setTimeout(resolve, 300));

      // Create plan
      const result = await planningService.createPlan(formData, currentUser?.id);
      
      setLoadingStep(4); // Finalizing
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // Store the generated plans and show them
      setGeneratedPlans(result);
      setShowPlans(true);
      
    } catch (error) {
      console.error('Error creating plan:', error);
      setError('Failed to create plan. Please try again.');
    } finally {
      setIsLoading(false);
      setLoadingStep(0);
    }
  };

  const handlePlanSelection = async (selectedPlan) => {
    try {
      // Save the chosen plan to the outing profile service
      const outingData = outingProfileService.formatOutingData(selectedPlan, formData, currentUser?.id);
      await outingProfileService.addOutingToHistory(outingData);
      
      // Show success message (you can add a toast notification here later)
      console.log('Plan saved to outing history successfully!');
      
      // Close modal and notify parent with the selected plan
      onClose();
      if (onPlanCreated) {
        onPlanCreated(selectedPlan);
      }
    } catch (error) {
      console.error('Error saving plan to outing history:', error);
      // You can add error handling here (show error message to user)
      setError('Failed to save plan to history. Please try again.');
    }
  };

  const handleRegenerate = () => {
    setShowPlans(false);
    setGeneratedPlans(null);
    setError('');
    // Trigger the loading process again
    handleSubmit({ preventDefault: () => {} });
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal" onClick={e => e.stopPropagation()}>
          <div className="modal-header">
            <h2 className="modal-title">Plan Your Outing</h2>
            <button className="modal-close" onClick={onClose}>&times;</button>
          </div>

          <div className="modal-body">
            {/* Progress Bar */}
            <div className="progress-bar">
              {[1, 2, 3, 4, 5, 6].map(step => (
                <div
                  key={step}
                  className={`progress-step ${step === currentStep ? 'active' : step < currentStep ? 'completed' : ''}`}
                >
                  <div className="progress-label">
                    {step === 1 && 'Basic Info'}
                    {step === 2 && 'Location'}
                    {step === 3 && 'Date & Time'}
                    {step === 4 && 'Venue Types'}
                    {step === 5 && 'Preferences'}
                    {step === 6 && 'Review'}
                  </div>
                </div>
              ))}
            </div>

            {error && (
              <div className="form-error" style={{ marginBottom: '16px' }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              {/* Step 1: Basic Info */}
              <div className={`form-step ${currentStep === 1 ? 'active' : ''}`}>
                <div className="form-group">
                  <label htmlFor="planName" className="form-label">Plan Name *</label>
                  <input
                    type="text"
                    id="planName"
                    name="planName"
                    className="form-input"
                    value={formData.planName}
                    onChange={handleInputChange}
                    placeholder="e.g., Friday Night Out, Birthday Celebration"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="groupSize" className="form-label">Group Size *</label>
                  <input
                    type="number"
                    id="groupSize"
                    name="groupSize"
                    className="form-input"
                    value={formData.groupSize}
                    onChange={handleInputChange}
                    min="1"
                    max="20"
                    required
                  />
                </div>
              </div>

              {/* Step 2: Location */}
              <div className={`form-step ${currentStep === 2 ? 'active' : ''}`}>
                               <div className="form-group">
                   <label htmlFor="city" className="form-label">City *</label>
                   <div className="city-input-container">
                     <input
                       type="text"
                       id="city"
                       name="city"
                       className="form-input"
                       value={formData.city}
                       onChange={handleCityChange}
                       onFocus={handleCityFocus}
                       placeholder="Type or select a city"
                       required
                       list="cities-list"
                     />
                     <datalist id="cities-list">
                       {cities.map(city => (
                         <option key={city.value} value={city.displayName} />
                       ))}
                     </datalist>
                   </div>
                   <div className="form-help">
                     {formData.city && !cities.find(city => 
                       city.value === formData.city || city.displayName === formData.city
                     ) ? (
                       <span style={{ color: 'var(--accent-1)' }}>
                         🆕 Custom city - using default coordinates
                       </span>
                     ) : (
                       <span>
                         💡 Type any city name or select from suggestions
                       </span>
                     )}
                   </div>
                 </div>

                <div className="form-group">
                  <label htmlFor="address" className="form-label">Address (Optional)</label>
                  <input
                    type="text"
                    id="address"
                    name="address"
                    className="form-input"
                    value={formData.address}
                    onChange={handleInputChange}
                    placeholder="Specific address or neighborhood"
                  />
                </div>
              </div>

              {/* Step 3: Date & Time */}
              <div className={`form-step ${currentStep === 3 ? 'active' : ''}`}>
                <div className="form-group">
                  <label htmlFor="planDate" className="form-label">Date *</label>
                  <input
                    type="date"
                    id="planDate"
                    name="planDate"
                    className="form-input"
                    value={formData.planDate}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="planTime" className="form-label">Time *</label>
                  <CustomTimePicker
                    value={formData.planTime}
                    onChange={handleInputChange}
                    required
                  />
                  <div className="form-help">
                    <span>⏰ Time selection in 15-minute increments (00, 15, 30, 45)</span>
                  </div>
                </div>


              </div>

              {/* Step 4: Venue Types */}
              <div className={`form-step ${currentStep === 4 ? 'active' : ''}`}>
                <div className="form-group">
                  <label className="form-label">Venue Types *</label>
                  <div className="form-help" style={{ marginBottom: 
                    '16px' }}>
                    <span>🎯 Select the types of venues you'd like to include in your plan. The venues in your generated plan will be chosen from these selected categories.</span>
                  </div>
                  <div className="checkbox-group">
                    {planningService.getVenueTypeOptions().map(option => (
                      <div key={option.value} className="checkbox-item">
                        <input
                          type="checkbox"
                          id={option.value}
                          name="venueTypes"
                          value={option.value}
                          checked={formData.venueTypes.includes(option.value)}
                          onChange={handleInputChange}
                        />
                        <label htmlFor={option.value}>{option.label}</label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Step 5: Preferences */}
              <div className={`form-step ${currentStep === 5 ? 'active' : ''}`}>
                <div className="form-group">
                  <label htmlFor="budgetRange" className="form-label">Budget Range</label>
                  <select
                    id="budgetRange"
                    name="budgetRange"
                    className="form-select"
                    value={formData.budgetRange}
                    onChange={handleInputChange}
                  >
                    {planningService.getBudgetOptions().map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="minRating" className="form-label">Minimum Rating</label>
                  <input
                    type="number"
                    id="minRating"
                    name="minRating"
                    className="form-input"
                    value={formData.minRating}
                    onChange={handleInputChange}
                    min="1"
                    max="5"
                    step="0.1"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="radiusKm" className="form-label">Search Radius (km)</label>
                  <input
                    type="number"
                    id="radiusKm"
                    name="radiusKm"
                    className="form-input"
                    value={formData.radiusKm}
                    onChange={handleInputChange}
                    min="1"
                    max="50"
                    required
                  />
                </div>

                               <div className="form-group">
                   <label htmlFor="maxVenues" className="form-label">
                     Maximum Venues
                                         <span 
                        className="info-icon" 
                        title="Maximum venues / activities per generated plan"
                        data-tooltip="Maximum venues / activities per generated plan"
                      >
                        <img src="/images/info.png" alt="Info" />
                      </span>
                   </label>
                   <input
                     type="number"
                     id="maxVenues"
                     name="maxVenues"
                     className="form-input"
                     value={formData.maxVenues}
                     onChange={handleInputChange}
                     min="1"
                     max={formData.venueTypes.length || 1}
                     required
                   />
                   <div className="form-help">
                     Range: 1 - {formData.venueTypes.length || 1} (based on selected venue types)
                   </div>
                 </div>
              </div>

              {/* Step 6: Review */}
              <div className={`form-step ${currentStep === 6 ? 'active' : ''}`}>
                <div className="form-group">
                  <label htmlFor="dietaryRestrictions" className="form-label">Dietary Restrictions</label>
                  <input
                    type="text"
                    id="dietaryRestrictions"
                    name="dietaryRestrictions"
                    className="form-input"
                    value={formData.dietaryRestrictions}
                    onChange={handleInputChange}
                    placeholder="e.g., vegetarian, gluten-free, kosher"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="accessibilityNeeds" className="form-label">Accessibility Needs</label>
                  <input
                    type="text"
                    id="accessibilityNeeds"
                    name="accessibilityNeeds"
                    className="form-input"
                    value={formData.accessibilityNeeds}
                    onChange={handleInputChange}
                    placeholder="e.g., wheelchair accessible, elevator"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="amenities" className="form-label">Preferred Amenities</label>
                  <input
                    type="text"
                    id="amenities"
                    name="amenities"
                    className="form-input"
                    value={formData.amenities}
                    onChange={handleInputChange}
                    placeholder="e.g., parking, wifi, outdoor seating"
                  />
                </div>

                <div style={{ 
                  background: 'var(--background-alt)', 
                  padding: '16px', 
                  borderRadius: 'var(--radius)',
                  marginTop: '16px'
                }}>
                  <h4 style={{ marginBottom: '12px' }}>Plan Summary</h4>
                  <p><strong>Name:</strong> {formData.planName}</p>
                  <p><strong>Location:</strong> {formData.city}</p>
                  <p><strong>Date:</strong> {formData.planDate} at {formData.planTime}</p>
                  <p><strong>Group Size:</strong> {formData.groupSize} people</p>
                  <p><strong>Venue Types:</strong> {formData.venueTypes.join(', ')}</p>
                </div>
              </div>
            </form>
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </button>

            <div style={{ display: 'flex', gap: '12px' }}>
              {currentStep > 1 && (
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={prevStep}
                  disabled={isLoading}
                >
                  Previous
                </button>
              )}

              {currentStep < totalSteps ? (
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={nextStep}
                  disabled={isLoading}
                >
                  Next
                </button>
              ) : (
                <button
                  type="submit"
                  className="btn btn-primary"
                  onClick={handleSubmit}
                  disabled={isLoading}
                >
                  {isLoading ? 'Generating Plans...' : 'Generate Plans'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <div className="loading-title">Creating Your Perfect Plan</div>
            <div className="loading-subtitle">This usually takes 10-15 seconds</div>
            
            <div className="loading-steps">
              <div className={`loading-step ${loadingStep >= 1 ? 'completed' : loadingStep === 1 ? 'active' : ''}`}>
                <div className={`loading-step-icon ${loadingStep > 1 ? 'completed' : loadingStep === 1 ? 'active' : 'pending'}`}>
                  {loadingStep > 1 ? '✓' : loadingStep === 1 ? '⟳' : '1'}
                </div>
                Analyzing your preferences
              </div>
              
              <div className={`loading-step ${loadingStep >= 2 ? 'completed' : loadingStep === 2 ? 'active' : ''}`}>
                <div className={`loading-step-icon ${loadingStep > 2 ? 'completed' : loadingStep === 2 ? 'active' : 'pending'}`}>
                  {loadingStep > 2 ? '✓' : loadingStep === 2 ? '⟳' : '2'}
                </div>
                Discovering venues in your area
              </div>
              
              <div className={`loading-step ${loadingStep >= 3 ? 'completed' : loadingStep === 3 ? 'active' : ''}`}>
                <div className={`loading-step-icon ${loadingStep > 3 ? 'completed' : loadingStep === 3 ? 'active' : 'pending'}`}>
                  {loadingStep > 3 ? '✓' : loadingStep === 3 ? '⟳' : '3'}
                </div>
                Generating multiple plan options
              </div>
              
              <div className={`loading-step ${loadingStep >= 4 ? 'completed' : loadingStep === 4 ? 'active' : ''}`}>
                <div className={`loading-step-icon ${loadingStep > 4 ? 'completed' : loadingStep === 4 ? 'active' : 'pending'}`}>
                  {loadingStep > 4 ? '✓' : loadingStep === 4 ? '⟳' : '4'}
                </div>
                Finalizing your plans
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Generated Plans Modal */}
      {showPlans && generatedPlans && (
        <GeneratedPlansModal
          plans={generatedPlans}
          onPlanSelection={handlePlanSelection}
          onRegenerate={handleRegenerate}
          onClose={() => {
            setShowPlans(false);
            setGeneratedPlans(null);
          }}
        />
      )}
    </>
  );
};

export default PlanningModal;
