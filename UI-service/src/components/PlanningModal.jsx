import React, { useState, useEffect } from 'react';

const PlanningModal = ({ isOpen, onClose, onSubmit }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    planName: '',
    groupSize: 2,
    city: '',
    address: '',
    latitude: null,
    longitude: null,
    planDate: '',
    planTime: '',
    durationHours: 3,
    venueTypes: [],
    budgetRange: '',
    minRating: '',
    radiusKm: 5,
    maxVenues: 5,
    dietaryRestrictions: '',
    accessibilityNeeds: '',
    amenities: ''
  });

  const totalSteps = 6;

  // Set default date and time when component mounts
  useEffect(() => {
    if (isOpen) {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      const now = new Date();
      now.setHours(now.getHours() + 1);
      
      setFormData(prev => ({
        ...prev,
        planDate: tomorrow.toISOString().split('T')[0],
        planTime: now.toTimeString().slice(0, 5)
      }));
    }
  }, [isOpen]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleVenueTypeChange = (venueType, checked) => {
    setFormData(prev => ({
      ...prev,
      venueTypes: checked 
        ? [...prev.venueTypes, venueType]
        : prev.venueTypes.filter(type => type !== venueType)
    }));
  };

  const validateCurrentStep = () => {
    switch (currentStep) {
      case 1:
        if (!formData.planName.trim()) {
          alert('Please enter a plan name.');
          return false;
        }
        if (formData.groupSize < 1 || formData.groupSize > 20) {
          alert('Group size must be between 1 and 20.');
          return false;
        }
        break;
      case 2:
        if (!formData.city.trim()) {
          alert('Please enter a city.');
          return false;
        }
        break;
      case 3:
        if (!formData.planDate || !formData.planTime) {
          alert('Please select both date and time.');
          return false;
        }
        break;
      case 4:
        if (formData.venueTypes.length === 0) {
          alert('Please select at least one venue type.');
          return false;
        }
        break;
      default:
        break;
    }
    return true;
  };

  const nextStep = () => {
    if (validateCurrentStep() && currentStep < totalSteps) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateCurrentStep()) {
      console.log('Form data submitted:', formData);
      onSubmit?.(formData);
      onClose();
    }
  };

  const handleCityInput = async (cityName) => {
    if (!cityName.trim()) return;

    try {
      const coordinates = await geocodeCity(cityName);
      if (coordinates) {
        setFormData(prev => ({
          ...prev,
          latitude: coordinates.lat,
          longitude: coordinates.lng
        }));
      }
    } catch (error) {
      console.log('Could not geocode city:', cityName);
    }
  };

  const geocodeCity = async (cityName) => {
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
  };

  if (!isOpen) return null;

  return (
    <div className="planning-modal active">
      <div className="planning-content">
        <div className="planning-header">
          <h2 className="planning-title">Create New Outing Plan</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        {/* Progress Indicator */}
        <div className="progress-indicator">
          {Array.from({ length: totalSteps }, (_, index) => {
            const stepNumber = index + 1;
            let className = 'progress-step';
            if (stepNumber === currentStep) {
              className += ' active';
            } else if (stepNumber < currentStep) {
              className += ' completed';
            }
            return (
              <div key={stepNumber} className={className}>
                {stepNumber}
              </div>
            );
          })}
        </div>
        
        <form className="planning-form" onSubmit={handleSubmit}>
          {/* Step 1: Basic Information */}
          {currentStep === 1 && (
            <div className="form-step active">
              <div className="form-section">
                <h3>Basic Information</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="planName">Plan Name *</label>
                    <input
                      className="input-field"
                      id="planName"
                      type="text"
                      placeholder="e.g., Weekend in Tel Aviv"
                      value={formData.planName}
                      onChange={(e) => handleInputChange('planName', e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="groupSize">Group Size *</label>
                    <input
                      className="input-field"
                      id="groupSize"
                      type="number"
                      min="1"
                      max="20"
                      placeholder="2"
                      value={formData.groupSize}
                      onChange={(e) => handleInputChange('groupSize', parseInt(e.target.value))}
                      required
                    />
                  </div>
                </div>
              </div>
              <div className="step-actions">
                <button type="button" className="btn btn-primary" onClick={nextStep}>
                  Next
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Location */}
          {currentStep === 2 && (
            <div className="form-step active">
              <div className="form-section">
                <h3>Location</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="city">City *</label>
                    <input
                      className="input-field"
                      id="city"
                      type="text"
                      placeholder="e.g., Tel Aviv"
                      value={formData.city}
                      onChange={(e) => handleInputChange('city', e.target.value)}
                      onBlur={(e) => handleCityInput(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="address">Address (Optional)</label>
                    <input
                      className="input-field"
                      id="address"
                      type="text"
                      placeholder="e.g., Rothschild Blvd"
                      value={formData.address}
                      onChange={(e) => handleInputChange('address', e.target.value)}
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="latitude">Latitude</label>
                    <input
                      className="input-field"
                      id="latitude"
                      type="number"
                      step="0.000001"
                      placeholder="32.0853"
                      value={formData.latitude || ''}
                      onChange={(e) => handleInputChange('latitude', parseFloat(e.target.value) || null)}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="longitude">Longitude</label>
                    <input
                      className="input-field"
                      id="longitude"
                      type="number"
                      step="0.000001"
                      placeholder="34.7818"
                      value={formData.latitude || ''}
                      onChange={(e) => handleInputChange('longitude', parseFloat(e.target.value) || null)}
                    />
                  </div>
                </div>
              </div>
              <div className="step-actions">
                <button type="button" className="btn btn-secondary" onClick={prevStep}>
                  Previous
                </button>
                <button type="button" className="btn btn-primary" onClick={nextStep}>
                  Next
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Date & Time */}
          {currentStep === 3 && (
            <div className="form-step active">
              <div className="form-section">
                <h3>Date & Time</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="planDate">Date *</label>
                    <input
                      className="input-field"
                      id="planDate"
                      type="date"
                      value={formData.planDate}
                      onChange={(e) => handleInputChange('planDate', e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="planTime">Time *</label>
                    <input
                      className="input-field"
                      id="planTime"
                      type="time"
                      value={formData.planTime}
                      onChange={(e) => handleInputChange('planTime', e.target.value)}
                      required
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="durationHours">Duration (Hours)</label>
                    <input
                      className="input-field"
                      id="durationHours"
                      type="number"
                      min="0.5"
                      max="24"
                      step="0.5"
                      placeholder="3"
                      value={formData.durationHours}
                      onChange={(e) => handleInputChange('durationHours', parseFloat(e.target.value))}
                    />
                  </div>
                </div>
              </div>
              <div className="step-actions">
                <button type="button" className="btn btn-secondary" onClick={prevStep}>
                  Previous
                </button>
                <button type="button" className="btn btn-primary" onClick={nextStep}>
                  Next
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Venue Types */}
          {currentStep === 4 && (
            <div className="form-step active">
              <div className="form-section">
                <h3>Venue Types *</h3>
                <div className="venue-types-grid">
                  {[
                    { value: 'restaurant', label: '🍽️ Restaurant' },
                    { value: 'cafe', label: '☕ Cafe' },
                    { value: 'bar', label: '🍺 Bar' },
                    { value: 'museum', label: '🏛️ Museum' },
                    { value: 'theater', label: '🎭 Theater' },
                    { value: 'park', label: '🌳 Park' },
                    { value: 'shopping_center', label: '🛍️ Shopping Center' },
                    { value: 'sports_facility', label: '🏃 Sports Facility' }
                  ].map(venueType => (
                    <label key={venueType.value} className="checkbox-label">
                      <input
                        type="checkbox"
                        name="venueTypes"
                        value={venueType.value}
                        checked={formData.venueTypes.includes(venueType.value)}
                        onChange={(e) => handleVenueTypeChange(venueType.value, e.target.checked)}
                      />
                      <span className="checkmark">{venueType.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="step-actions">
                <button type="button" className="btn btn-secondary" onClick={prevStep}>
                  Previous
                </button>
                <button type="button" className="btn btn-primary" onClick={nextStep}>
                  Next
                </button>
              </div>
            </div>
          )}

          {/* Step 5: Preferences */}
          {currentStep === 5 && (
            <div className="form-step active">
              <div className="form-section">
                <h3>Preferences</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="budgetRange">Budget Range</label>
                    <select
                      className="input-field"
                      id="budgetRange"
                      value={formData.budgetRange}
                      onChange={(e) => handleInputChange('budgetRange', e.target.value)}
                    >
                      <option value="">Any Budget</option>
                      <option value="$">$ - Inexpensive</option>
                      <option value="$$">$$ - Moderate</option>
                      <option value="$$$">$$$ - Expensive</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="minRating">Minimum Rating</label>
                    <select
                      className="input-field"
                      id="minRating"
                      value={formData.minRating}
                      onChange={(e) => handleInputChange('minRating', e.target.value)}
                    >
                      <option value="">Any Rating</option>
                      <option value="3.0">3.0+ Stars</option>
                      <option value="3.5">3.5+ Stars</option>
                      <option value="4.0">4.0+ Stars</option>
                      <option value="4.5">4.5+ Stars</option>
                    </select>
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="radiusKm">Search Radius (km)</label>
                    <input
                      className="input-field"
                      id="radiusKm"
                      type="number"
                      min="0.5"
                      max="50"
                      step="0.5"
                      value={formData.radiusKm}
                      onChange={(e) => handleInputChange('radiusKm', parseFloat(e.target.value))}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="maxVenues">Max Venues</label>
                    <input
                      className="input-field"
                      id="maxVenues"
                      type="number"
                      min="1"
                      max="20"
                      value={formData.maxVenues}
                      onChange={(e) => handleInputChange('maxVenues', parseInt(e.target.value))}
                    />
                  </div>
                </div>
              </div>
              <div className="step-actions">
                <button type="button" className="btn btn-secondary" onClick={prevStep}>
                  Previous
                </button>
                <button type="button" className="btn btn-primary" onClick={nextStep}>
                  Next
                </button>
              </div>
            </div>
          )}

          {/* Step 6: Special Requirements */}
          {currentStep === 6 && (
            <div className="form-step active">
              <div className="form-section">
                <h3>Special Requirements</h3>
                <div className="form-group">
                  <label htmlFor="dietaryRestrictions">Dietary Restrictions</label>
                  <input
                    className="input-field"
                    id="dietaryRestrictions"
                    type="text"
                    placeholder="e.g., vegetarian, gluten-free"
                    value={formData.dietaryRestrictions}
                    onChange={(e) => handleInputChange('dietaryRestrictions', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="accessibilityNeeds">Accessibility Needs</label>
                  <input
                    className="input-field"
                    id="accessibilityNeeds"
                    type="text"
                    placeholder="e.g., wheelchair accessible"
                    value={formData.accessibilityNeeds}
                    onChange={(e) => handleInputChange('accessibilityNeeds', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="amenities">Required Amenities</label>
                  <input
                    className="input-field"
                    id="amenities"
                    type="text"
                    placeholder="e.g., wifi, parking, outdoor seating"
                    value={formData.amenities}
                    onChange={(e) => handleInputChange('amenities', e.target.value)}
                  />
                </div>
              </div>
              <div className="step-actions">
                <button type="button" className="btn btn-secondary" onClick={prevStep}>
                  Previous
                </button>
                <button type="submit" className="btn btn-primary">
                  <span className="icon">🚀</span> Create Plan
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default PlanningModal;
