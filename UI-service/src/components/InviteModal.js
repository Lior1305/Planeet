import React, { useState } from 'react';
import planningService from '../services/planningService.js';

const InviteModal = ({ isOpen, onClose, plan, onInviteSubmitted }) => {
  const [emails, setEmails] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen || !plan) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!emails.trim()) {
      setError('Please enter at least one email address');
      return;
    }

    // Parse emails (split by comma, semicolon, or newline)
    const emailList = emails
      .split(/[,;\n]/)
      .map(email => email.trim())
      .filter(email => email.length > 0);

    if (emailList.length === 0) {
      setError('Please enter at least one valid email address');
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const invalidEmails = emailList.filter(email => !emailRegex.test(email));
    if (invalidEmails.length > 0) {
      setError(`Invalid email format: ${invalidEmails.join(', ')}`);
      return;
    }

    // Check participant limit
    const currentParticipants = plan.participants?.length || 0;
    const maxParticipants = plan.group_size || 2;
    const availableSlots = maxParticipants - currentParticipants;
    
    if (emailList.length > availableSlots) {
      setError(`You can only invite ${availableSlots} more participant(s). Plan is limited to ${maxParticipants} people.`);
      return;
    }

    try {
      setIsLoading(true);
      setError('');

      // Call the planning service to invite participants
      await planningService.inviteParticipants(plan.plan_id, emailList);
      
      // Reset form and close modal
      setEmails('');
      onInviteSubmitted();
    } catch (error) {
      console.error('Error inviting participants:', error);
      setError(error.message || 'Failed to send invitations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setEmails('');
    setError('');
    onClose();
  };

  const currentParticipants = plan.participants?.length || 0;
  const maxParticipants = plan.group_size || 2;
  const availableSlots = maxParticipants - currentParticipants;

  return (
    <div className="modal-overlay">
      <div className="modal-content invite-modal">
        <div className="modal-header">
          <h2>Invite Participants</h2>
          <button className="modal-close" onClick={handleClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="plan-info">
            <h3>{plan.plan_name}</h3>
            <p>📅 {new Date(plan.outing_date).toLocaleDateString()} at {plan.outing_time}</p>
            <p>📍 {plan.city}</p>
            <p>👥 {currentParticipants}/{maxParticipants} participants</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="emails">
                Email Addresses
                <span className="help-text">
                  (Separate multiple emails with commas, semicolons, or new lines)
                </span>
              </label>
              <textarea
                id="emails"
                value={emails}
                onChange={(e) => setEmails(e.target.value)}
                placeholder="friend1@example.com, friend2@example.com"
                rows={4}
                disabled={isLoading}
                required
              />
            </div>

            {availableSlots > 0 && (
              <div className="slots-info">
                <p>📝 You can invite up to {availableSlots} more participant(s)</p>
              </div>
            )}

            {error && (
              <div className="error-message">
                <p>{error}</p>
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
                disabled={isLoading || availableSlots <= 0}
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
