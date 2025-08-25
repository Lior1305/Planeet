import configService from './config.js';

class PlanningService {
  constructor() {
    this.cityCoordinates = {
      'tel aviv': { lat: 32.0853, lng: 34.7818 },
      'jerusalem': { lat: 31.7683, lng: 35.2137 },
      'haifa': { lat: 32.7940, lng: 34.9896 },
      'beer sheva': { lat: 31.2518, lng: 34.7913 },
      'eilat': { lat: 29.5577, lng: 34.9519 },
      'netanya': { lat: 32.3328, lng: 34.8600 },
      'ashdod': { lat: 31.8044, lng: 34.6500 },
      'rishon lezion': { lat: 31.9600, lng: 34.8000 },
      'petah tikva': { lat: 32.0853, lng: 34.8860 },
      'holon': { lat: 32.0167, lng: 34.7792 },
      'ramat gan': { lat: 32.0689, lng: 34.8248 },
      'bat yam': { lat: 32.0233, lng: 34.7503 },
      'kfar saba': { lat: 32.1750, lng: 34.9070 },
      'raanana': { lat: 32.1833, lng: 34.8667 },
      'herzliya': { lat: 32.1667, lng: 34.8333 },
      'modiin': { lat: 31.8928, lng: 35.0153 },
      'yavne': { lat: 31.8781, lng: 34.7397 },
      'rosh haayin': { lat: 32.0950, lng: 34.9567 },
      'kfar yona': { lat: 32.3167, lng: 34.9333 },
      'tiberias': { lat: 32.7947, lng: 35.5327 }
    };
  }

  async geocodeCity(cityName) {
    if (!cityName.trim()) return null;
    
    const normalizedCity = cityName.toLowerCase().trim();
    return this.cityCoordinates[normalizedCity] || null;
  }

  // Get all available cities
  getAllCities() {
    return Object.entries(this.cityCoordinates).map(([name, coords]) => ({
      name: name,
      value: name,
      displayName: name.charAt(0).toUpperCase() + name.slice(1),
      lat: coords.lat,
      lng: coords.lng
    }));
  }

  validatePlanningFormData(formData) {
    // Check required fields
    if (!formData.planName.trim()) {
      return { isValid: false, error: 'Please enter a plan name.' };
    }

    if (!formData.city.trim()) {
      return { isValid: false, error: 'Please enter a city.' };
    }

    if (formData.venueTypes.length === 0) {
      return { isValid: false, error: 'Please select at least one venue type.' };
    }

    if (formData.groupSize < 1) {
      return { isValid: false, error: 'Group size must be at least 1.' };
    }

    if (formData.groupSize > 20) {
      return { isValid: false, error: 'Group size must be between 1 and 20.' };
    }

    return { isValid: true };
  }

  async createPlan(formData, userId) {
    try {
      // Prepare the plan request for the Planning Service
      const planRequest = {
        user_id: userId || 'default_user',
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

      console.log('Creating plan with request:', planRequest);

      // Make API call to Planning Service
      const response = await fetch(`${configService.getPlanningServiceUrl()}/v1/plans/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(planRequest)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Planning service error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Plan created successfully:', result);
      return result;
    } catch (error) {
      console.error('Error creating plan:', error);
      throw error;
    }
  }

  getDefaultFormData() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const now = new Date();
    now.setHours(now.getHours() + 1);
    
    return {
      planName: '',
      groupSize: 2,
      city: '',
      address: '',
      latitude: null,
      longitude: null,
      planDate: tomorrow.toISOString().split('T')[0],
      planTime: now.toTimeString().slice(0, 5),
      durationHours: 3,
      venueTypes: [],
      budgetRange: 'medium',
      minRating: 4.0,
      radiusKm: 5,
      maxVenues: 10,
      dietaryRestrictions: '',
      accessibilityNeeds: '',
      amenities: ''
    };
  }

  getVenueTypeOptions() {
    return [
      { value: 'restaurant', label: 'Restaurant' },
      { value: 'cafe', label: 'Café' },
      { value: 'bar', label: 'Bar' },
      { value: 'museum', label: 'Museum' },
      { value: 'theater', label: 'Theater' },
      { value: 'park', label: 'Park' },
      { value: 'shopping_center', label: 'Shopping Center' },
      { value: 'sports_facility', label: 'Sports Facility' },
      { value: 'hotel', label: 'Hotel' },
      { value: 'other', label: 'Other' }
    ];
  }

  getBudgetOptions() {
    return [
      { value: 'low', label: 'Budget-friendly' },
      { value: 'medium', label: 'Mid-range' },
      { value: 'high', label: 'Premium' }
    ];
  }
}

// Create and export planning service instance
const planningService = new PlanningService();

export default planningService;
