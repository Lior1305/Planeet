import React, { useState, useEffect } from 'react';
import outingProfileService from '../services/outingProfileService.js';
import userService from '../services/userService.js';
import planningService from '../services/planningService.js';
import RatingModal from './RatingModal.js';
import InviteModal from './InviteModal.js';

const OutingHistory = () => {
  const [outingHistory, setOutingHistory] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('future'); // 'future' or 'past'
  const [ratingModalOpen, setRatingModalOpen] = useState(false);
  const [selectedOuting, setSelectedOuting] = useState(null);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [selectedPlanForInvite, setSelectedPlanForInvite] = useState(null);
  
  const currentUser = userService.getCurrentUser();

  useEffect(() => {
    if (currentUser?.id) {
      loadOutingHistory();
    }
  }, [currentUser?.id]);

  const loadOutingHistory = async () => {
    try {
      setIsLoading(true);
      setError('');
      const history = await outingProfileService.getUserOutingHistory(currentUser.id);
      setOutingHistory(history);
    } catch (error) {
      console.error('Error loading outing history:', error);
      setError('Failed to load outing history. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const updateOutingStatus = async (planId, newStatus, userId) => {
    try {
      await outingProfileService.updateOutingStatus(planId, newStatus, userId);
      // Reload the history to reflect the change
      await loadOutingHistory();
    } catch (error) {
      console.error('Error updating outing status:', error);
      setError('Failed to update outing status. Please try again.');
    }
  };

  const deleteOuting = async (planId, userId) => {
    try {
      await outingProfileService.deleteOuting(planId, userId);
      // Reload the history to reflect the change
      await loadOutingHistory();
    } catch (error) {
      console.error('Error deleting outing:', error);
      setError('Failed to delete outing. Please try again.');
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const formatTime = (timeString) => {
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

  const formatDurationMinutes = (minutes) => {
    if (!minutes) return '';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    }
    return `${mins}m`;
  };

  const getVenueTypeIcon = (venueType) => {
    const icons = {
      restaurant: '🍽️',
      cafe: '☕',
      bar: '🍺',
      museum: '🏛️',
      theater: '🎭',
      park: '🌳',
      spa: '💆‍♀️',
      shopping_center: '🛍️',
      sports_facility: '⚽',
      other: '📍'
    };
    return icons[venueType] || '📍';
  };

  const renderVenueDetails = (outing) => {
    // Check if we have selected plan data with venues
    if (outing.selected_plan && outing.selected_plan.suggested_venues) {
      return (
        <div className="venue-details">
          <h4 className="venue-details-title">Selected Venues:</h4>
                         <div className="venue-list">
                 {outing.selected_plan.suggested_venues.map((venue, index) => (
                   <div key={venue.venue_id || index} className="venue-item">
                     <span className="venue-icon">{getVenueTypeIcon(venue.venue_type)}</span>
                     <div className="venue-info">
                       <span className="venue-name">{venue.name}</span>
                       <span className="venue-type">{venue.venue_type}</span>
                       
                       {/* Timing Information */}
                       {(venue.start_time || venue.end_time) && (
                         <div className="venue-timing-compact">
                           {venue.start_time && venue.end_time && (
                             <span className="timing-info-compact">
                               🕒 {formatTime(venue.start_time)} - {formatTime(venue.end_time)}
                             </span>
                           )}
                           {venue.duration_minutes && (
                             <span className="duration-info-compact">
                               ⏱️ {formatDurationMinutes(venue.duration_minutes)}
                             </span>
                           )}
                         </div>
                       )}
                       
                                               {/* Travel Information */}
                        <div className="venue-travel-compact">
                          {venue.travel_distance_km && venue.travel_distance_km > 0 && venue.travel_time_from_previous && venue.travel_time_from_previous > 0 ? (
                            <>
                              <span className="distance-info-compact">
                                {venue.travel_distance_km < 2 ? '🚶‍♂️' : '🚗'} {venue.travel_distance_km}km
                              </span>
                              <span className="travel-time-info-compact">
                                {venue.travel_distance_km < 2 ? '🚶‍♂️' : '🚗'} {venue.travel_time_from_previous}min
                              </span>
                            </>
                          ) : (
                            <span className="travel-time-info-compact">
                              🏁 Start
                            </span>
                          )}
                        </div>
                     </div>
                   </div>
                 ))}
               </div>
        </div>
      );
    }
    
    // Fallback: just show venue types if no detailed venue data
    return (
      <div className="venue-details">
        <h4 className="venue-details-title">Venue Types:</h4>
        <div className="venue-types">
          {outing.venue_types.map((type, index) => (
            <span key={index} className="venue-type-badge">
              {getVenueTypeIcon(type)} {type}
            </span>
          ))}
        </div>
      </div>
    );
  };

  const handleRateOuting = (outing) => {
    setSelectedOuting(outing);
    setRatingModalOpen(true);
  };

  const handleRatingSubmitted = () => {
    // Reload the outing history to show updated ratings
    loadOutingHistory();
  };

  const handleInviteParticipants = (outing) => {
    setSelectedPlanForInvite(outing);
    setInviteModalOpen(true);
  };

  const handleInviteSubmitted = () => {
    // Reload the outing history to show updated participants
    loadOutingHistory();
    setInviteModalOpen(false);
    setSelectedPlanForInvite(null);
  };

  const handleConfirmInvitation = async (planId) => {
    try {
      await planningService.respondToPlanInvitation(planId, currentUser.id, 'confirmed');
      await loadOutingHistory();
    } catch (error) {
      console.error('Error confirming invitation:', error);
      setError('Failed to confirm invitation. Please try again.');
    }
  };

  const handleDeclineInvitation = async (planId) => {
    try {
      await planningService.respondToPlanInvitation(planId, currentUser.id, 'declined');
      await loadOutingHistory();
    } catch (error) {
      console.error('Error declining invitation:', error);
      setError('Failed to decline invitation. Please try again.');
    }
  };

  // Helper function to determine if user is the creator
  const isCreator = (outing) => {
    return outing.creator_user_id === currentUser.id;
  };

  // Helper function to determine if user is invited (not creator)
  const isInvited = (outing) => {
    return !isCreator(outing);
  };

  // Helper function to get creator name for invited plans
  const getCreatorName = (outing) => {
    if (isCreator(outing)) return null;
    
    // Try to find creator in participants array
    const creator = outing.participants?.find(p => p.user_id === outing.creator_user_id);
    return creator?.name || 'Unknown';
  };

  // Helper function to get participant status icon
  const getParticipantStatusIcon = (participant) => {
    switch (participant.status) {
      case 'confirmed':
        return '✅';
      case 'declined':
        return '❌';
      case 'pending':
      default:
        return '⏳';
    }
  };

  // Helper function to render participants list
  const renderParticipantsList = (outing) => {
    if (!outing.participants || outing.participants.length === 0) {
      return null;
    }

    return (
      <div className="participants-list">
        <h4 className="participants-title">Participants ({outing.participants.length}/{outing.group_size})</h4>
        <div className="participants-grid">
          {outing.participants.map((participant, index) => (
            <div key={participant.user_id || index} className="participant-item">
              <span className="participant-status-icon">
                {getParticipantStatusIcon(participant)}
              </span>
              <span className="participant-name">{participant.name}</span>
              {participant.user_id === currentUser.id && (
                <span className="participant-you">(You)</span>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (!currentUser) {
    return (
      <div className="outing-history-container">
        <div className="no-user-message">
          <p>Please log in to view your outing history.</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="outing-history-container">
        <div className="loading-message">
          <p>Loading your outing history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="outing-history-container">
        <div className="error-message">
          <p>{error}</p>
          <button onClick={loadOutingHistory} className="btn btn-primary">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const futureOutings = outingHistory?.future_outings || [];
  const pastOutings = outingHistory?.past_outings || [];

  return (
    <div className="outing-history-container">
      <div className="outing-history-header">
        <h2>My Outing History</h2>
        <div className="tab-navigation">
          <button
            className={`tab-button ${activeTab === 'future' ? 'active' : ''}`}
            onClick={() => setActiveTab('future')}
          >
            Future Outings ({futureOutings.length})
          </button>
          <button
            className={`tab-button ${activeTab === 'past' ? 'active' : ''}`}
            onClick={() => setActiveTab('past')}
          >
            Past Outings ({pastOutings.length})
          </button>
        </div>
      </div>

      {activeTab === 'future' && (
        <div className="outings-section">
          {futureOutings.length === 0 ? (
            <div className="no-outings-message">
              <p>No future outings planned yet.</p>
              <p>Create a new plan to get started!</p>
            </div>
          ) : (
            <div className="outings-grid">
              {futureOutings.map((outing) => (
                <div key={outing.plan_id} className="outing-card future">
                  <div className="outing-header">
                    <div className="outing-title-section">
                      <h3 className="outing-title">{outing.plan_name}</h3>
                      <div className="outing-tags">
                        {isCreator(outing) && (
                          <span className="tag tag-creator">Created by me</span>
                        )}
                        {isInvited(outing) && (
                          <span className="tag tag-invited">Invited by {getCreatorName(outing)}</span>
                        )}
                      </div>
                    </div>
                    <span className={`outing-status ${outing.status}`}>
                      {outing.status}
                    </span>
                  </div>
                  
                  <div className="outing-details">
                    <div className="outing-info">
                      <span className="outing-date">📅 {formatDate(outing.outing_date)}</span>
                      <span className="outing-time">🕒 {formatTime(outing.outing_time)}</span>
                      <span className="outing-location">📍 {outing.city}</span>
                      <span className="outing-group">👥 {outing.group_size} people</span>
                    </div>
                    
                    {renderVenueDetails(outing)}
                    {renderParticipantsList(outing)}
                  </div>

                  <div className="outing-actions">
                    {isCreator(outing) && outing.is_group_outing && (
                      <>
                        {outing.participants && outing.participants.length < outing.group_size ? (
                          <button
                            onClick={() => handleInviteParticipants(outing)}
                            className="btn btn-primary btn-sm"
                            title="Invite more participants"
                          >
                            📧 Invite
                          </button>
                        ) : (
                          <button
                            className="btn btn-primary btn-sm disabled"
                            title="Maximum participants reached"
                            disabled
                          >
                            📧 Invite (Full)
                          </button>
                        )}
                      </>
                    )}
                    
                    {isInvited(outing) && (
                      <>
                        <button
                          onClick={() => handleConfirmInvitation(outing.plan_id)}
                          className="btn btn-success btn-sm"
                        >
                          ✅ Confirm
                        </button>
                        <button
                          onClick={() => handleDeclineInvitation(outing.plan_id)}
                          className="btn btn-danger btn-sm"
                        >
                          ❌ Decline
                        </button>
                      </>
                    )}
                    
                    {isCreator(outing) && (
                      <button
                        onClick={() => updateOutingStatus(outing.plan_id, 'cancelled', currentUser.id)}
                        className={`btn btn-danger btn-sm ${outing.status === 'cancelled' ? 'disabled' : ''}`}
                        disabled={outing.status === 'cancelled'}
                      >
                        {outing.status === 'cancelled' ? 'Cancelled' : 'Cancel'}
                      </button>
                    )}
                    
                    {outing.status === 'cancelled' && (
                      <button
                        onClick={() => deleteOuting(outing.plan_id, currentUser.id)}
                        className="btn btn-outline btn-sm"
                        title="Delete this cancelled outing"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'past' && (
        <div className="outings-section">
          {pastOutings.length === 0 ? (
            <div className="no-outings-message">
              <p>No past outings yet.</p>
            </div>
          ) : (
            <div className="outings-grid">
              {pastOutings.map((outing) => (
                <div key={outing.plan_id} className="outing-card past">
                  <div className="outing-header">
                    <h3 className="outing-title">{outing.plan_name}</h3>
                    <span className={`outing-status ${outing.status}`}>
                      {outing.status}
                    </span>
                  </div>
                  
                  <div className="outing-details">
                    <div className="outing-info">
                      <span className="outing-date">📅 {formatDate(outing.outing_date)}</span>
                      <span className="outing-time">🕒 {formatTime(outing.outing_time)}</span>
                      <span className="outing-location">📍 {outing.city}</span>
                      <span className="outing-group">👥 {outing.group_size} people</span>
                    </div>
                    
                    {renderVenueDetails(outing)}
                  </div>

                  <div className="outing-actions">
                    {!outing.venue_ratings && outing.selected_plan && outing.selected_plan.suggested_venues && (
                      <button
                        onClick={() => handleRateOuting(outing)}
                        className="btn btn-primary btn-sm"
                        title="Rate this outing"
                      >
                        ⭐ Rate
                      </button>
                    )}
                    <button
                      onClick={() => deleteOuting(outing.plan_id, currentUser.id)}
                      className="btn btn-outline btn-sm"
                      title="Delete this past outing"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Rating Modal */}
      <RatingModal
        isOpen={ratingModalOpen}
        onClose={() => setRatingModalOpen(false)}
        outing={selectedOuting}
        onRatingSubmitted={handleRatingSubmitted}
      />

      {/* Invite Modal */}
      <InviteModal
        isOpen={inviteModalOpen}
        onClose={() => setInviteModalOpen(false)}
        plan={selectedPlanForInvite}
        onInviteSubmitted={handleInviteSubmitted}
      />
    </div>
  );
};

export default OutingHistory;
