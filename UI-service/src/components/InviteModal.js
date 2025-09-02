import React, { useState } from 'react';
import planningService from '../services/planningService.js';

const InviteModal = ({ isOpen, onClose, planId, groupSize, currentParticipants = [] }) => {
  const [emails, setEmails] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const maxInvites = groupSize - currentParticipants.length;

  const handleClose = () => {
    setEmails('');
    setError('');
    setSuccess('');
    onClose();
  };

  const validateEmails = (emailString) => {
    const emailList = emailString.split(',').map(email => email.trim()).filter(email => email);
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    for (const email of emailList) {
      if (!emailRegex.test(email)) {
        return `Invalid email format: ${email}`;
      }
    }
    
    if (emailList.length > maxInvites) {
      return `You can only invite ${maxInvites} more people (group size: ${groupSize})`;
    }
    
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const emailList = emails.split(',').map(email => email.trim()).filter(email => email);
    
    if (emailList.length === 0) {
      setError('Please enter at least one email address');
      return;
    }

    const validationError = validateEmails(emails);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    
    try {
      console.log('Attempting to invite participants:', { planId, emailList });
      const result = await planningService.inviteParticipants(planId, emailList);
      console.log('Invite result:', result);
      setSuccess(`Successfully invited ${emailList.length} people!`);
      
      // Clear form after successful invite
      setTimeout(() => {
        handleClose();
      }, 2000);
      
    } catch (error) {
      console.error('Error sending invitations:', error);
      if (error.message.includes('Plan not confirmed yet')) {
        setError('This plan needs to be confirmed first. Please select a plan from the generated options before inviting friends.');
      } else {
        setError(error.message || 'Failed to send invitations. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Invite Friends</h2>
          <button className="modal-close" onClick={handleClose}>×</button>
        </div>
        
        <div className="modal-body">
          <p className="invite-info">
            Invite friends to join your outing! You can invite up to <strong>{maxInvites}</strong> more people.
          </p>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="emails">Email Addresses</label>
              <textarea
                id="emails"
                value={emails}
                onChange={(e) => setEmails(e.target.value)}
                placeholder="Enter email addresses separated by commas (e.g., friend1@example.com, friend2@example.com)"
                rows="4"
                className="form-control"
                disabled={isLoading}
              />
              <small className="form-help">
                Separate multiple email addresses with commas
              </small>
            </div>

            {error && (
              <div className="alert alert-error">
                {error}
              </div>
            )}

            {success && (
              <div className="alert alert-success">
                {success}
              </div>
            )}

            <div className="modal-actions">
              <button
                type="button"
                onClick={handleClose}
                className="btn btn-outline"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isLoading || !emails.trim()}
              >
                {isLoading ? 'Sending...' : 'Send Invitations'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default InviteModal;
