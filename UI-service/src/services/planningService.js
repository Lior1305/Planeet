import configService from './config.js';
import { getAllCountries, getCitiesByCountry, getAllCities, findCityCoordinates } from '../data/countries.js';

class PlanningService {
  constructor() {
    // Countries data is now imported from separate file
  }

  async geocodeCity(cityName) {
    return findCityCoordinates(cityName);
  }

  // Get all available countries
  getAllCountries() {
    return getAllCountries();
  }

  // Get cities for a specific country
  getCitiesByCountry(countryKey) {
    return getCitiesByCountry(countryKey);
  }

  // Get all available cities (for backward compatibility)
  getAllCities() {
    return getAllCities();
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

    if (formData.maxVenues < 1) {
      return { isValid: false, error: 'Maximum venues must be at least 1.' };
    }

    if (formData.maxVenues > formData.venueTypes.length) {
      return { isValid: false, error: `Maximum venues cannot exceed the number of selected venue types (${formData.venueTypes.length}).` };
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
          address: formData.address || '',
          city: formData.city,
          country: (formData.country && formData.country.toLowerCase()) || 'israel'
        },
        radius_km: formData.radiusKm || 5, // Default radius
        max_venues: formData.maxVenues || formData.venueTypes.length || 1,
        use_personalization: true,
        include_links: true,
        date: `${formData.planDate}T${formData.planTime}:00`,
        group_size: formData.groupSize,
        budget_range: formData.budgetRange || '$$',
        min_rating: formData.minRating || 4.0, // Default minimum rating
        amenities: formData.amenities && formData.amenities.length > 0 ? formData.amenities : null,
        dietary_restrictions: formData.dietaryRestrictions && formData.dietaryRestrictions.length > 0 ? formData.dietaryRestrictions : null,
        accessibility_needs: formData.accessibilityNeeds && formData.accessibilityNeeds.length > 0 ? formData.accessibilityNeeds : null
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
    const now = new Date();
    const planTime = this.roundToNearest15Minutes(now);
    
    return {
      planName: '',
      country: 'israel', // Default to Israel
      city: 'tel aviv', // Default to Tel Aviv
      address: '',
      latitude: 32.0853,
      longitude: 34.7818,
      planDate: now.toISOString().split('T')[0],
      planTime: planTime,
      groupSize: 2,
      budgetRange: '$$',
      venueTypes: ['restaurant'],
      radiusKm: 5, // Default search radius
      maxVenues: 1, // Default max venues
      minRating: 4.0, // Default minimum rating
      amenities: [], // Now an array for tag selection
      dietaryRestrictions: [], // Now an array for tag selection
      accessibilityNeeds: [] // Now an array for tag selection
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
      { value: 'spa', label: 'Spa' },
      { value: 'other', label: 'Other' }
    ];
  }

  getBudgetOptions() {
    return [
      { value: 'low', label: '$ Budget-friendly' },
      { value: 'medium', label: '$$ Mid-range' },
      { value: 'high', label: '$$$ Premium' }
    ];
  }

  roundToNearest15Minutes(date) {
    const minutes = date.getMinutes();
    const roundedMinutes = Math.round(minutes / 15) * 15;
    date.setMinutes(roundedMinutes);
    date.setSeconds(0);
    date.setMilliseconds(0);
    return date.toTimeString().slice(0, 5);
  }

  async inviteParticipants(planId, participantEmails) {
    try {
      const response = await fetch(`${configService.getPlanningServiceUrl()}/v1/plans/${planId}/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          participant_emails: participantEmails
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Planning service error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Participants invited successfully:', result);
      return result;
    } catch (error) {
      console.error('Error inviting participants:', error);
      throw error;
    }
  }

  async respondToPlanInvitation(planId, userId, status) {
    try {
      const response = await fetch(`${configService.getPlanningServiceUrl()}/v1/plans/${planId}/respond`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          status: status
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Planning service error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Plan invitation response sent successfully:', result);
      return result;
    } catch (error) {
      console.error('Error responding to plan invitation:', error);
      throw error;
    }
  }
}

// Create and export planning service instance
const planningService = new PlanningService();

export default planningService;
