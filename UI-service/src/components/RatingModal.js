import React, { useState, useEffect } from 'react';
import outingProfileService from '../services/outingProfileService.js';
import userService from '../services/userService.js';

const RatingModal = ({ isOpen, onClose, outing, onRatingSubmitted }) => {
  const [ratings, setRatings] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const currentUser = userService.getCurrentUser();

  useEffect(() => {
    if (isOpen && outing && outing.selected_plan && outing.selected_plan.suggested_venues) {
      // Initialize ratings for each venue
      const initialRatings = {};
      outing.selected_plan.suggested_venues.forEach(venue => {
        initialRatings[venue.venue_id] = 0; // 0 means no rating yet
      });
      setRatings(initialRatings);
      setMessage('');
      setError('');
    }
  }, [isOpen, outing]);

  const handleRatingChange = (venueId, rating) => {
    setRatings(prev => ({
      ...prev,
      [venueId]: rating
    }));
  };

  const validateRatings = () => {
    const venues = outing.selected_plan.suggested_venues;
    for (let venue of venues) {
      if (ratings[venue.venue_id] === 0) {
        return false;
      }
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateRatings()) {
      setError('Please rate all venues before submitting');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Convert ratings to the format expected by the API
      const venueRatings = Object.entries(ratings).map(([venueId, rating]) => ({
        venue_id: venueId,
        rating: rating
      }));

      await outingProfileService.addOutingRatings(outing.plan_id, currentUser.id, venueRatings);
      
      setMessage('Ratings submitted successfully!');
      
      if (onRatingSubmitted) {
        onRatingSubmitted();
      }
      
      // Close modal after a short delay
      setTimeout(() => {
        onClose();
      }, 1500);
      
    } catch (error) {
      console.error('Error submitting ratings:', error);
      setError('Failed to submit ratings. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderStarRating = (venueId, currentRating) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <button
          key={i}
          type="button"
          className={`star-button ${i <= currentRating ? 'filled' : ''}`}
          onClick={() => handleRatingChange(venueId, i)}
          disabled={isLoading}
        >
          ★
        </button>
      );
    }
    return stars;
  };

  if (!isOpen || !outing || !outing.selected_plan) return null;

  const venues = outing.selected_plan.suggested_venues || [];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal rating-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Rate Your Experience</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        
        <div className="modal-body">
          {message && (
            <div className="message success">
              {message}
            </div>
          )}
          
          {error && (
            <div className="message error">
              {error}
            </div>
          )}
          
          <div className="rating-intro">
            <p>Please rate each venue from your outing on a scale of 1-5 stars:</p>
            <div className="rating-legend">
              <span>1 = Poor</span>
              <span>2 = Fair</span>
              <span>3 = Good</span>
              <span>4 = Very Good</span>
              <span>5 = Excellent</span>
            </div>
          </div>

          <div className="venues-rating-list">
            {venues.map((venue) => (
              <div key={venue.venue_id} className="venue-rating-item">
                <div className="venue-info">
                  <h4 className="venue-name">{venue.name}</h4>
                  <p className="venue-type">{venue.venue_type}</p>
                </div>
                <div className="rating-stars">
                  {renderStarRating(venue.venue_id, ratings[venue.venue_id] || 0)}
                  {ratings[venue.venue_id] > 0 && (
                    <span className="rating-value">({ratings[venue.venue_id]}/5)</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="modal-actions">
          <button type="button" className="btn btn-outline" onClick={onClose}>
            Cancel
          </button>
          <button 
            type="submit" 
            className="btn btn-primary" 
            onClick={handleSubmit}
            disabled={isLoading || !validateRatings()}
          >
            {isLoading ? 'Submitting...' : 'Submit Ratings'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RatingModal;
