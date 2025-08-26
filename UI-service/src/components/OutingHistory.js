import React, { useState, useEffect } from 'react';
import outingProfileService from '../services/outingProfileService.js';
import userService from '../services/userService.js';

const OutingHistory = () => {
  const [outingHistory, setOutingHistory] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('future'); // 'future' or 'past'
  
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

  const updateOutingStatus = async (planId, newStatus) => {
    try {
      await outingProfileService.updateOutingStatus(planId, newStatus);
      // Reload the history to reflect the change
      await loadOutingHistory();
    } catch (error) {
      console.error('Error updating outing status:', error);
      setError('Failed to update outing status. Please try again.');
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
                    
                    <div className="venue-types">
                      {outing.venue_types.map((type, index) => (
                        <span key={index} className="venue-type-badge">
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="outing-actions">
                    <button
                      onClick={() => updateOutingStatus(outing.plan_id, 'completed', currentUser.id)}
                      className="btn btn-success btn-sm"
                    >
                      Mark as Completed
                    </button>
                    <button
                      onClick={() => updateOutingStatus(outing.plan_id, 'cancelled', currentUser.id)}
                      className="btn btn-danger btn-sm"
                    >
                      Cancel
                    </button>
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
                    
                    <div className="venue-types">
                      {outing.venue_types.map((type, index) => (
                        <span key={index} className="venue-type-badge">
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default OutingHistory;
