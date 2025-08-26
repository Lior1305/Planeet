import configService from './config.js';

class OutingProfileService {
  constructor() {
    this.baseUrl = configService.getOutingProfileServiceUrl();
  }

  async addOutingToHistory(outingData) {
    try {
      const response = await fetch(`${this.baseUrl}/outing-history`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(outingData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Outing profile service error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Outing added to history successfully:', result);
      return result;
    } catch (error) {
      console.error('Error adding outing to history:', error);
      throw error;
    }
  }

  async getUserOutingHistory(userId) {
    try {
      const response = await fetch(`${this.baseUrl}/outing-history?user_id=${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Outing profile service error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('User outing history retrieved:', result);
      return result;
    } catch (error) {
      console.error('Error retrieving outing history:', error);
      throw error;
    }
  }

  async updateOutingStatus(planId, newStatus, userId) {
    try {
      const response = await fetch(`${this.baseUrl}/outing-history/${planId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus, user_id: userId })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Outing profile service error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Outing status updated successfully:', result);
      return result;
    } catch (error) {
      console.error('Error updating outing status:', error);
      throw error;
    }
  }

  async deleteOuting(planId, userId) {
    try {
      const response = await fetch(`${this.baseUrl}/outing-history/${planId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Outing profile service error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Outing deleted successfully:', result);
      return result;
    } catch (error) {
      console.error('Error deleting outing:', error);
      throw error;
    }
  }

  // Helper method to format outing data for the outing profile service
  formatOutingData(selectedPlan, formData, userId) {
    return {
      user_id: userId,
      plan_id: selectedPlan.plan_id,
      plan_name: formData.planName,
      outing_date: formData.planDate,
      outing_time: formData.planTime,
      group_size: formData.groupSize,
      city: formData.city,
      venue_types: formData.venueTypes,
      selected_plan: selectedPlan
    };
  }

  // Admin/maintenance method to update all expired outings
  async updateExpiredOutings() {
    try {
      const response = await fetch(`${this.baseUrl}/outing-history/update-expired`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Outing profile service error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Expired outings updated:', result);
      return result;
    } catch (error) {
      console.error('Error updating expired outings:', error);
      throw error;
    }
  }
}

// Create and export outing profile service instance
const outingProfileService = new OutingProfileService();

export default outingProfileService;
