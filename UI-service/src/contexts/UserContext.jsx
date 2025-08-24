import React, { createContext, useContext, useState, useEffect } from 'react';

// Configuration for API endpoints using Kubernetes environment variables
const API_CONFIG = {
  USERS_SERVICE_URL: process.env.REACT_APP_USERS_SERVICE_URL || 'http://localhost:30080',
  OUTING_PROFILE_SERVICE_URL: process.env.REACT_APP_OUTING_PROFILE_SERVICE_URL || 'http://localhost:30050',
  PLANNING_SERVICE_URL: process.env.REACT_APP_PLANNING_SERVICE_URL || 'http://localhost:8001',
  VENUES_SERVICE_URL: process.env.REACT_APP_VENUES_SERVICE_URL || 'http://localhost:8000'
};

// Log the configuration for debugging
console.log('⚙️ API Configuration:', API_CONFIG);
console.log('🌍 Environment variables:', {
  REACT_APP_USERS_SERVICE_URL: process.env.REACT_APP_USERS_SERVICE_URL,
  REACT_APP_OUTING_PROFILE_SERVICE_URL: process.env.REACT_APP_OUTING_PROFILE_SERVICE_URL,
  REACT_APP_PLANNING_SERVICE_URL: process.env.REACT_APP_PLANNING_SERVICE_URL,
  REACT_APP_VENUES_SERVICE_URL: process.env.REACT_APP_VENUES_SERVICE_URL
});

const UserContext = createContext();

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export const UserProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from localStorage on app start
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user:', error);
        localStorage.removeItem('user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (credentials) => {
    console.log('🔐 Attempting login with:', credentials);
    try {
      console.log('📡 Sending request to:', `${API_CONFIG.USERS_SERVICE_URL}/users/auth/login`);
      const response = await fetch(`${API_CONFIG.USERS_SERVICE_URL}/users/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      console.log('📥 Response received:', response.status, response.statusText);
      console.log('📋 Response headers:', Object.fromEntries(response.headers.entries()));

      if (response.ok) {
        const userData = await response.json();
        console.log('✅ Login successful:', userData);
        setCurrentUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        return { success: true, user: userData };
      } else {
        const errorData = await response.text();
        console.log('❌ Login failed:', errorData);
        return { success: false, error: errorData || 'Login failed' };
      }
    } catch (error) {
      console.error('💥 Login error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const signup = async (userData) => {
    console.log('📝 Attempting signup with:', userData);
    try {
      console.log('📡 Sending request to:', `${API_CONFIG.USERS_SERVICE_URL}/users/auth/signup`);
      const response = await fetch(`${API_CONFIG.USERS_SERVICE_URL}/users/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      console.log('📥 Response received:', response.status, response.statusText);
      console.log('📋 Response headers:', Object.fromEntries(response.headers.entries()));

      if (response.ok) {
        const newUser = await response.json();
        console.log('✅ Signup successful:', newUser);
        setCurrentUser(newUser);
        localStorage.setItem('user', JSON.stringify(newUser));
        return { success: true, user: newUser };
      } else {
        const errorData = await response.text();
        console.log('❌ Signup failed:', errorData);
        return { success: false, error: errorData || 'Signup failed' };
      }
    } catch (error) {
      console.error('💥 Signup error:', error);
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('user');
  };

  const updateUser = (updatedData) => {
    if (currentUser) {
      const updatedUser = { ...currentUser, ...updatedData };
      setCurrentUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  const value = {
    currentUser,
    isLoading,
    login,
    signup,
    logout,
    updateUser,
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};
