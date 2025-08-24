import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import userService from '../services/userService.js';

const Header = () => {
  const navigate = useNavigate();
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
                <div className="user-info">
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
    </header>
  );
};

export default Header;
