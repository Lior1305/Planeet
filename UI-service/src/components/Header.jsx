import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import SettingsModal from './SettingsModal';
import LoginModal from './LoginModal';

const Header = () => {
  const { currentUser, logout } = useUser();
  const location = useLocation();
  const [isSettingsOpen, setIsSettingsOpen] = React.useState(false);
  const [isLoginOpen, setIsLoginOpen] = React.useState(false);
  const [loginMode, setLoginMode] = React.useState('login');

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    logout();
    setIsSettingsOpen(false);
  };

  const handleLoginClick = (mode) => {
    setLoginMode(mode);
    setIsLoginOpen(true);
  };

  return (
    <>
      <header className="header">
        <div className="container">
          <div className="header-content">
            {/* Left: Logo */}
            <Link to="/" className="logo">
              <img src="/images/planeet-small.png" alt="Planeet" />
            </Link>

            {/* Center: Nav */}
            <nav className="nav">
              <Link 
                to="/plan" 
                className={`nav-link ${isActive('/plan') ? 'active' : ''}`}
              >
                Plan
              </Link>
              <Link 
                to="/profile" 
                className={`nav-link ${isActive('/profile') ? 'active' : ''}`}
              >
                Profile
              </Link>
              <Link 
                to="/history" 
                className={`nav-link ${isActive('/history') ? 'active' : ''}`}
              >
                Previous Outings
              </Link>
            </nav>

            {/* Right: Actions */}
            <div className="header-actions">
              {currentUser ? (
                                 <div className="user-menu">
                   <span className="user-name">Hi, {currentUser.username || 'User'}!</span>
                  <button 
                    className="btn btn-secondary"
                    onClick={() => setIsSettingsOpen(true)}
                  >
                    Settings
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={handleLogout}
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <div className="auth-actions">
                  <button 
                    className="btn btn-secondary"
                    onClick={() => handleLoginClick('login')}
                  >
                    Login
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={() => handleLoginClick('signup')}
                  >
                    Sign Up
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {isSettingsOpen && (
        <SettingsModal 
          isOpen={isSettingsOpen} 
          onClose={() => setIsSettingsOpen(false)} 
        />
      )}

      {isLoginOpen && (
        <LoginModal 
          isOpen={isLoginOpen} 
          onClose={() => setIsLoginOpen(false)}
          mode={loginMode}
        />
      )}
    </>
  );
};

export default Header;
