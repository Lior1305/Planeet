import React, { useState } from 'react';
import { useUser } from '../contexts/UserContext';

const LoginModal = ({ isOpen, onClose, mode = 'login' }) => {
  const { login, signup } = useUser();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
    // Clear submit error when user starts typing
    if (submitError) {
      setSubmitError('');
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (mode === 'signup') {
      if (!formData.username.trim()) {
        newErrors.username = 'Username is required';
      }
      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = 'Email is invalid';
      }
      if (!formData.password) {
        newErrors.password = 'Password is required';
      } else if (formData.password.length < 6) {
        newErrors.password = 'Password must be at least 6 characters';
      }
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    } else {
      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      }
      if (!formData.password) {
        newErrors.password = 'Password is required';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError('');

    try {
      let result;
      
      if (mode === 'signup') {
        // Prepare user data for signup
        const userData = {
          username: formData.username,
          email: formData.email,
          password: formData.password,
          cellphoneNumber: '' // Optional field
        };
        
        result = await signup(userData);
      } else {
        // Prepare credentials for login
        const credentials = {
          email: formData.email,
          password: formData.password
        };
        
        result = await login(credentials);
      }

      if (result.success) {
        onClose();
        // Reset form
        setFormData({
          username: '',
          email: '',
          password: '',
          confirmPassword: ''
        });
      } else {
        setSubmitError(result.error || 'Authentication failed');
      }
    } catch (error) {
      console.error('Authentication error:', error);
      setSubmitError('An unexpected error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="settings-modal active">
      <div className="settings-content">
        <div className="settings-header">
          <h2 className="settings-title">
            {mode === 'login' ? 'Login' : 'Sign Up'}
          </h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        {submitError && (
          <div className="error-message" style={{ 
            backgroundColor: '#fee', 
            color: '#c33', 
            padding: '12px', 
            borderRadius: '4px', 
            marginBottom: '16px',
            border: '1px solid #fcc'
          }}>
            {submitError}
          </div>
        )}
        
        <form className="form-container" onSubmit={handleSubmit}>
          {mode === 'signup' && (
            <div className="form-group">
              <label>Username</label>
              <input
                className={`input-field ${errors.username ? 'error' : ''}`}
                type="text"
                placeholder="Username"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                disabled={isSubmitting}
              />
              {errors.username && <span className="error-text">{errors.username}</span>}
            </div>
          )}
          
          <div className="form-group">
            <label>Email</label>
            <input
              className={`input-field ${errors.email ? 'error' : ''}`}
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              disabled={isSubmitting}
            />
            {errors.email && <span className="error-text">{errors.email}</span>}
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              className={`input-field ${errors.password ? 'error' : ''}`}
              type="password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              disabled={isSubmitting}
            />
            {errors.password && <span className="error-text">{errors.password}</span>}
          </div>

          {mode === 'signup' && (
            <div className="form-group">
              <label>Confirm Password</label>
              <input
                className={`input-field ${errors.confirmPassword ? 'error' : ''}`}
                type="password"
                placeholder="Confirm Password"
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                disabled={isSubmitting}
              />
              {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
            </div>
          )}
          
          <div className="btn-row">
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Processing...' : (mode === 'login' ? 'Login' : 'Sign Up')}
            </button>
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
          </div>

          <div style={{ textAlign: 'center', marginTop: '1rem' }}>
            {mode === 'login' ? (
              <p>
                Don't have an account?{' '}
                <button
                  type="button"
                  className="link-btn"
                  onClick={() => window.location.reload()}
                >
                  Sign up here
                </button>
              </p>
            ) : (
              <p>
                Already have an account?{' '}
                <button
                  type="button"
                  className="link-btn"
                  onClick={() => window.location.reload()}
                >
                  Login here
                </button>
              </p>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginModal;
