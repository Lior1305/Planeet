import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import userService from '../services/userService.js';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    phone: ''
  });
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const validateField = (name, value) => {
    const errors = { ...fieldErrors };
    
    switch (name) {
      case 'username':
        if (value && value.length < 3) {
          errors.username = 'Username must be at least 3 characters long.';
        } else if (value && !/^[a-zA-Z0-9_]+$/.test(value)) {
          errors.username = 'Username can only contain letters, numbers, and underscores.';
        } else {
          delete errors.username;
        }
        break;
      case 'email':
        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          errors.email = 'Please enter a valid email address.';
        } else {
          delete errors.email;
        }
        break;
      case 'password':
        if (value && value.length < 6) {
          errors.password = 'Password must be at least 6 characters long.';
        } else if (value && value.length > 50) {
          errors.password = 'Password must be less than 50 characters.';
        } else {
          delete errors.password;
        }
        break;
      case 'phone':
        if (value && !/^05\d{8}$/.test(value)) {
          errors.phone = 'Please enter a valid Israeli phone number (e.g., 05XXXXXXXX) or leave it empty.';
        } else {
          delete errors.phone;
        }
        break;
      default:
        break;
    }
    
    setFieldErrors(errors);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear general error when user starts typing
    if (error) setError('');
    
    // Validate the specific field
    validateField(name, value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Validate form data
      const validation = userService.validateRegistrationData(formData);
      if (!validation.isValid) {
        setError(validation.error);
        return;
      }

      // Attempt registration
      const result = await userService.register(formData);
      
      if (result.success) {
        console.log('Registration successful, redirecting to plan page...');
        navigate('/plan');
      } else {
        setError(result.error);
      }
    } catch (error) {
      console.error('Registration error:', error);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '400px', marginTop: '60px' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Create Account</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Join Planeet and start planning amazing outings</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username" className="form-label">Username</label>
          <input
            type="text"
            id="username"
            name="username"
            className={`form-input ${fieldErrors.username ? 'error' : ''}`}
            value={formData.username}
            onChange={handleInputChange}
            required
            disabled={isLoading}
          />
          {fieldErrors.username && (
            <div className="field-error">
              {fieldErrors.username}
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="email" className="form-label">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            className={`form-input ${fieldErrors.email ? 'error' : ''}`}
            value={formData.email}
            onChange={handleInputChange}
            required
            disabled={isLoading}
          />
          {fieldErrors.email && (
            <div className="field-error">
              {fieldErrors.email}
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="password" className="form-label">Password</label>
          <div className="password-input-container">
            <input
              type={showPassword ? "text" : "password"}
              id="password"
              name="password"
              className={`form-input ${fieldErrors.password ? 'error' : ''}`}
              value={formData.password}
              onChange={handleInputChange}
              required
              disabled={isLoading}
            />
            <button
              type="button"
              className="password-toggle-btn"
              onClick={() => setShowPassword(!showPassword)}
              disabled={isLoading}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              <img 
                src={showPassword ? "/images/hidden.png" : "/images/eye.png"} 
                alt={showPassword ? "Hide password" : "Show password"}
                width="20" 
                height="20"
              />
            </button>
          </div>
          {fieldErrors.password && (
            <div className="field-error">
              {fieldErrors.password}
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="phone" className="form-label">Phone (Optional)</label>
          <input
            type="tel"
            id="phone"
            name="phone"
            className={`form-input ${fieldErrors.phone ? 'error' : ''}`}
            value={formData.phone}
            onChange={handleInputChange}
            placeholder="05XXXXXXXX"
            disabled={isLoading}
          />
          <small style={{ color: 'var(--text-light)', fontSize: '14px' }}>
            Israeli format: 05XXXXXXXX
          </small>
          {fieldErrors.phone && (
            <div className="field-error">
              {fieldErrors.phone}
            </div>
          )}
        </div>

        {error && (
          <div className="form-error">
            {error}
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', marginBottom: '24px' }}
          disabled={isLoading}
        >
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </button>

        <div style={{ textAlign: 'center' }}>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--primary)', textDecoration: 'none' }}>
              Sign in here
            </Link>
          </p>
          
          <Link to="/" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
            ← Back to Home
          </Link>
        </div>
      </form>
    </div>
  );
};

export default Register;
