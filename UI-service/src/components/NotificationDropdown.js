import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import notificationService from '../services/notificationService.js';
import userService from '../services/userService.js';

const NotificationDropdown = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [invitations, setInvitations] = useState([]);
  const [loading, setLoading] = useState(false);
  const currentUser = userService.getCurrentUser();

  useEffect(() => {
    if (isOpen && currentUser) {
      loadInvitations();
      // Poll for updates every 10 seconds when dropdown is open
      const interval = setInterval(loadInvitations, 10000);
      return () => clearInterval(interval);
    }
  }, [isOpen, currentUser]);

  const loadInvitations = async () => {
    if (!currentUser) return;
    
    setLoading(true);
    try {
      const pendingInvitations = await notificationService.getPendingInvitations(currentUser.id);
      setInvitations(pendingInvitations);
    } catch (error) {
      console.error('Error loading invitations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptInvitation = async (invitationId) => {
    try {
      const success = await notificationService.acceptInvitation(invitationId);
      if (success) {
        // Remove the invitation from the list
        setInvitations(prev => prev.filter(inv => inv.id !== invitationId));
        // Refresh notification count in header
        if (window.refreshNotificationCount) {
          window.refreshNotificationCount();
        }
        // Navigate to future outings
        navigate('/history?tab=future');
        onClose();
      }
    } catch (error) {
      console.error('Error accepting invitation:', error);
    }
  };

  const handleDeclineInvitation = async (invitationId) => {
    try {
      const success = await notificationService.declineInvitation(invitationId);
      if (success) {
        // Remove the invitation from the list
        setInvitations(prev => prev.filter(inv => inv.id !== invitationId));
        // Refresh notification count in header
        if (window.refreshNotificationCount) {
          window.refreshNotificationCount();
        }
      }
    } catch (error) {
      console.error('Error declining invitation:', error);
    }
  };

  const handleViewOutings = () => {
    navigate('/history?tab=future');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="notification-dropdown">
      <div className="notification-header">
        <h3>Invitations</h3>
        <div className="header-actions">
          <button 
            className="refresh-btn" 
            onClick={loadInvitations}
            title="Refresh"
            disabled={loading}
          >
            {loading ? '⟳' : '↻'}
          </button>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
      </div>
      
      <div className="notification-content">
        {loading ? (
          <div className="loading">Loading invitations...</div>
        ) : invitations.length === 0 ? (
          <div className="no-invitations">
            <p>No pending invitations</p>
          </div>
        ) : (
          <div className="invitations-list">
            {invitations.map((invitation) => (
              <div key={invitation.id} className="invitation-item">
                <div className="invitation-content">
                  <p className="invitation-text">
                    <strong>{invitation.inviter_name}</strong> invited you to join 
                    <strong> "{invitation.plan_name}"</strong>
                  </p>
                  <p className="invitation-date">
                    {new Date(invitation.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="invitation-actions">
                  <button 
                    className="btn btn-sm btn-primary"
                    onClick={() => handleAcceptInvitation(invitation.id)}
                  >
                    Accept
                  </button>
                  <button 
                    className="btn btn-sm btn-outline"
                    onClick={() => handleDeclineInvitation(invitation.id)}
                  >
                    Decline
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {invitations.length > 0 && (
        <div className="notification-footer">
          <button 
            className="btn btn-primary"
            onClick={handleViewOutings}
          >
            View All Future Outings
          </button>
        </div>
      )}
    </div>
  );
};

export default NotificationDropdown;
