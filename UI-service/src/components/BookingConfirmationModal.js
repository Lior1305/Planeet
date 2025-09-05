import React, { useState, useEffect } from 'react';
import bookingService from '../services/bookingService.js';

const BookingConfirmationModal = ({ 
  selectedPlan, 
  formData, 
  currentUser, 
  onBookingComplete, 
  onClose 
}) => {
  const [bookingStatus, setBookingStatus] = useState({});
  const [isBooking, setIsBooking] = useState(false);
  const [bookingResults, setBookingResults] = useState({});
  const [error, setError] = useState('');

  useEffect(() => {
    // Initialize booking status for each venue
    const initialStatus = {};
    selectedPlan.suggested_venues.forEach(venue => {
      initialStatus[venue.venue_id] = 'pending';
    });
    setBookingStatus(initialStatus);
  }, [selectedPlan]);

  const formatTime = (timeString) => {
    if (!timeString) return '';
    try {
      const [hours, minutes] = timeString.split(':');
      const hour = parseInt(hours);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const displayHour = hour % 12 || 12;
      return `${displayHour}:${minutes} ${ampm}`;
    } catch {
      return timeString;
    }
  };

  const formatTimeSlot = (startTime, endTime) => {
    if (!startTime || !endTime) return '';
    return `${formatTime(startTime)} - ${formatTime(endTime)}`;
  };

  const handleBookPlan = async () => {
    setIsBooking(true);
    setError('');
    
    try {
      // Set all venues to booking status
      const newStatus = {};
      selectedPlan.suggested_venues.forEach(venue => {
        newStatus[venue.venue_id] = 'booking';
      });
      setBookingStatus(newStatus);
      
      // Book all venues in parallel
      const bookingPromises = selectedPlan.suggested_venues.map(async (venue) => {
        const timeSlot = `${venue.start_time}-${venue.end_time}`;
        const bookingRequest = {
          google_place_id: venue.venue_id,
          time_slot: timeSlot,
          user_id: currentUser.id,
          group_size: selectedPlan.group_size || formData.groupSize || 1
        };

        try {
          const result = await bookingService.makeBooking(bookingRequest);
          
          // Check if booking was successful (booking_id exists means success)
          if (result.booking_id && result.status === 'confirmed') {
            setBookingStatus(prev => ({ ...prev, [venue.venue_id]: 'confirmed' }));
            setBookingResults(prev => ({ ...prev, [venue.venue_id]: result }));
            return { success: true, venue: venue.name };
          } else {
            setBookingStatus(prev => ({ ...prev, [venue.venue_id]: 'failed' }));
            return { success: false, venue: venue.name, error: result.error || 'Booking failed' };
          }
        } catch (error) {
          console.error(`Error booking ${venue.name}:`, error);
          setBookingStatus(prev => ({ ...prev, [venue.venue_id]: 'failed' }));
          return { success: false, venue: venue.name, error: error.message };
        }
      });

      // Wait for all bookings to complete
      const results = await Promise.all(bookingPromises);
      
      // Check if all bookings were successful
      const failedBookings = results.filter(r => !r.success);
      if (failedBookings.length > 0) {
        const failedNames = failedBookings.map(r => r.venue).join(', ');
        setError(`Failed to book: ${failedNames}. Please try again.`);
      }
      
    } catch (error) {
      console.error('Error booking plan:', error);
      setError('Failed to book the plan. Please try again.');
    } finally {
      setIsBooking(false);
    }
  };

  const handleConfirmBooking = () => {
    // All venues are booked, proceed to save the plan
    onBookingComplete(selectedPlan, bookingResults);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return '⏳';
      case 'booking': return '🔄';
      case 'confirmed': return '✅';
      case 'failed': return '❌';
      default: return '⏳';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending': return 'Pending';
      case 'booking': return 'Booking...';
      case 'confirmed': return 'Confirmed';
      case 'failed': return 'Failed';
      default: return 'Pending';
    }
  };

  const allBooked = Object.values(bookingStatus).every(status => status === 'confirmed');
  const anyFailed = Object.values(bookingStatus).some(status => status === 'failed');
  const anyBooking = Object.values(bookingStatus).some(status => status === 'booking');

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal booking-confirmation-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Book Your Plan</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        
        <div className="modal-body">
          <div className="booking-summary">
            <p className="booking-intro">
              Ready to book your selected plan? We'll reserve time slots at all venues in your plan.
              Click "Book This Plan" to confirm all bookings at once.
            </p>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          <div className="venues-booking-list">
            {selectedPlan.suggested_venues.map((venue, index) => (
              <div key={venue.venue_id} className="venue-booking-item">
                <div className="venue-booking-header">
                  <div className="venue-info">
                    <h4 className="venue-name">{venue.name}</h4>
                    <p className="venue-type">{venue.venue_type}</p>
                    <p className="venue-address">{venue.address}</p>
                  </div>
                  <div className="venue-timing">
                    <span className="time-slot">
                      {formatTimeSlot(venue.start_time, venue.end_time)}
                    </span>
                    <span className="duration">
                      {venue.duration_minutes ? `${Math.floor(venue.duration_minutes / 60)}h ${venue.duration_minutes % 60}m` : ''}
                    </span>
                  </div>
                </div>
                
                <div className="venue-booking-actions">
                  <div className="booking-status">
                    <span className="status-icon">{getStatusIcon(bookingStatus[venue.venue_id])}</span>
                    <span className="status-text">{getStatusText(bookingStatus[venue.venue_id])}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="booking-actions">
            <button 
              className="btn btn-primary btn-lg"
              onClick={handleBookPlan}
              disabled={isBooking || allBooked}
            >
              {isBooking ? 'Booking Plan...' : 'Book This Plan'}
            </button>
          </div>
        </div>

        <div className="modal-actions">
          {allBooked && (
            <button 
              className="btn btn-success"
              onClick={handleConfirmBooking}
            >
              ✅ Confirm & Save Plan
            </button>
          )}
          <button className="btn btn-outline" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default BookingConfirmationModal;
