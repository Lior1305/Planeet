import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import userService from '../services/userService.js';
import notificationService from '../services/notificationService.js';
import EditUserModal from './EditUserModal.js';
import NotificationDropdown from './NotificationDropdown.js';

const Header = () => {
  const navigate = useNavigate();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  const [notificationCount, setNotificationCount] = useState(0);
  const currentUser = userService.getCurrentUser();

  // Load notification count when user changes
  useEffect(() => {
    if (currentUser) {
      loadNotificationCount();
      // Start polling for notifications every 30 seconds
      const interval = setInterval(loadNotificationCount, 30000);
      return () => clearInterval(interval);
    } else {
      setNotificationCount(0);
    }
  }, [currentUser]);

  const loadNotificationCount = async () => {
    try {
      const invitations = await notificationService.getPendingInvitations(currentUser.id);
      setNotificationCount(invitations.length);
    } catch (error) {
      console.error('Error loading notification count:', error);
    }
  };

  // Expose refresh function globally so other components can call it
  useEffect(() => {
    window.refreshNotificationCount = loadNotificationCount;
    return () => {
      delete window.refreshNotificationCount;
    };
  }, [currentUser]);

  const handleNotificationClick = () => {
    setIsNotificationOpen(!isNotificationOpen);
  };

  const handleLogout = () => {
    userService.logout();
    navigate('/');
  };

  const handlePlanningClick = () => {
    if (!currentUser) {
      alert('Please log in to plan an outing.');
      return;
    }
    navigate('/plan');
  };

  const handleUserUpdated = (updatedUser) => {
    // The userService already updates the storage, so we just need to force a re-render
    // by updating the component state or triggering a refresh
    window.location.reload();
  };

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo">
            <img src="/images/planeet-small.png" alt="Planeet" />
            <span className="logo-text">Planeet</span>
          </Link>

          <nav className="nav-menu">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/plan" className="nav-link">Plan Outing</Link>
            <Link to="/history" className="nav-link">My Outings</Link>
          </nav>

          <div className="user-menu">
            {currentUser ? (
              <>
                {/* Notification Bell */}
                <div className="notification-container">
                  <button 
                    className="notification-bell"
                    onClick={handleNotificationClick}
                    title="Notifications"
                  >
                    <img src="/images/bell.png" alt="Notifications" />
                    {notificationCount > 0 && (
                      <span className="notification-badge">{notificationCount}</span>
                    )}
                  </button>
                </div>
                
                <div className="user-info" onClick={() => setIsEditModalOpen(true)} style={{ cursor: 'pointer' }}>
                  <div className="user-avatar">
                    {currentUser.username.charAt(0).toUpperCase()}
                  </div>
                  <span>{currentUser.username}</span>
                </div>
                <button onClick={handleLogout} className="btn btn-outline">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-outline">Login</Link>
                <Link to="/register" className="btn btn-primary">Sign Up</Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Edit User Modal */}
      <EditUserModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onUserUpdated={handleUserUpdated}
      />

      {/* Notification Dropdown */}
      <NotificationDropdown
        isOpen={isNotificationOpen}
        onClose={() => setIsNotificationOpen(false)}
      />
    </header>
  );
};

export default Header;
