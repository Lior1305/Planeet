import configService from './config.js';

class NotificationService {
  constructor() {
    this.baseUrl = configService.getOutingProfileServiceUrl();
  }

  /**
   * Get pending invitations for a user
   * @param {string} userId - ID of the user
   * @returns {Promise<Array>} Array of pending invitations
   */
  async getPendingInvitations(userId) {
    try {
      const response = await fetch(`${this.baseUrl}/invitations/pending?user_id=${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch invitations: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching pending invitations:', error);
      return [];
    }
  }

  /**
   * Mark an invitation as read
   * @param {string} invitationId - ID of the invitation
   * @returns {Promise<boolean>} Success status
   */
  async markInvitationAsRead(invitationId) {
    try {
      const response = await fetch(`${this.baseUrl}/invitations/${invitationId}/read`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      return response.ok;
    } catch (error) {
      console.error('Error marking invitation as read:', error);
      return false;
    }
  }

  /**
   * Accept an invitation
   * @param {string} invitationId - ID of the invitation
   * @returns {Promise<boolean>} Success status
   */
  async acceptInvitation(invitationId) {
    try {
      const response = await fetch(`${this.baseUrl}/invitations/${invitationId}/accept`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      return response.ok;
    } catch (error) {
      console.error('Error accepting invitation:', error);
      return false;
    }
  }

  /**
   * Decline an invitation
   * @param {string} invitationId - ID of the invitation
   * @returns {Promise<boolean>} Success status
   */
  async declineInvitation(invitationId) {
    try {
      const response = await fetch(`${this.baseUrl}/invitations/${invitationId}/decline`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      return response.ok;
    } catch (error) {
      console.error('Error declining invitation:', error);
      return false;
    }
  }
}

export default new NotificationService();
