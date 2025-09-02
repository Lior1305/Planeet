import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import userService from '../services/userService.js';
import EditUserModal from './EditUserModal.js';

const Header = () => {
  const navigate = useNavigate();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [hasNotifications, setHasNotifications] = useState(false); // For future use
  
  // Example of how to use notifications in the future:
  // useEffect(() => {
  //   // Check for notifications from backend
  //   const checkNotifications = async () => {
  //     try {
  //       const response = await fetch('/api/notifications');
  //       const notifications = await response.json();
  //       setHasNotifications(notifications.length > 0);
  //     } catch (error) {
  //       console.error('Error checking notifications:', error);
  //     }
  //   };
  //   
  //   checkNotifications();
  //   // Set up interval to check for new notifications
  //   const interval = setInterval(checkNotifications, 30000); // Check every 30 seconds
  //   
  //   return () => clearInterval(interval);
  // }, []);
  const currentUser = userService.getCurrentUser();

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
            <Link to="/history" className="nav-link">History</Link>
          </nav>

          <div className="user-menu">
            {currentUser ? (
              <>
                <div className="notification-bell">
                  <button className="bell-button" onClick={() => console.log('Notifications clicked')}>
                    <span className="bell-icon">🔔</span>
                    {/* Notification indicator - will show when there are notifications */}
                    {hasNotifications && <span className="notification-indicator"></span>}
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
    </header>
  );
};

export default Header;
