import configService from './config.js';

class BookingService {
  constructor() {
    this.baseUrl = configService.getBookingServiceUrl();
  }

  async makeBooking(bookingRequest) {
    try {
      const response = await fetch(`${this.baseUrl}/v1/book`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookingRequest)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Booking service error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Booking successful:', result);
      return result;
    } catch (error) {
      console.error('Error making booking:', error);
      throw error;
    }
  }

  async validateBooking(bookingRequest) {
    try {
      const response = await fetch(`${this.baseUrl}/v1/book/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookingRequest)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Booking validation error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Booking validation result:', result);
      return result;
    } catch (error) {
      console.error('Error validating booking:', error);
      throw error;
    }
  }

  async checkAvailability(venueId, timeSlot) {
    try {
      const response = await fetch(`${this.baseUrl}/v1/availability/${venueId}/${timeSlot}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Availability check error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Availability check result:', result);
      return result;
    } catch (error) {
      console.error('Error checking availability:', error);
      throw error;
    }
  }

  async checkOverlappingAvailability(googlePlaceId, timeSlot) {
    try {
      const response = await fetch(`${this.baseUrl}/v1/availability/google-place/${googlePlaceId}/overlapping/${timeSlot}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Overlapping availability check error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Overlapping availability check result:', result);
      return result;
    } catch (error) {
      console.error('Error checking overlapping availability:', error);
      throw error;
    }
  }

  async findVenueByGooglePlaceId(googlePlaceId) {
    try {
      const response = await fetch(`${this.baseUrl}/v1/venue/google-place/${googlePlaceId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Find venue error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Find venue result:', result);
      return result;
    } catch (error) {
      console.error('Error finding venue:', error);
      throw error;
    }
  }
}

// Create and export booking service instance
const bookingService = new BookingService();
export default bookingService;
