import React, { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext';

const SettingsModal = ({ isOpen, onClose }) => {
  const { currentUser, updateUser } = useUser();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone: '',
    password: ''
  });

  useEffect(() => {
    if (currentUser && isOpen) {
      setFormData({
        username: currentUser.username || '',
        email: currentUser.email || '',
        phone: currentUser.phone || '',
        password: ''
      });
    }
  }, [currentUser, isOpen]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const updatedUser = {
      ...currentUser,
      username: formData.username,
      email: formData.email,
      phone: formData.phone
    };

    if (formData.password) {
      updatedUser.password = formData.password;
    }

    updateUser(updatedUser);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="settings-modal active">
      <div className="settings-content">
        <div className="settings-header">
          <h2 className="settings-title">Account Settings</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form className="form-container" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              className="input-field"
              type="text"
              placeholder="Username"
              value={formData.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              className="input-field"
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Phone Number</label>
            <input
              className="input-field"
              type="tel"
              placeholder="Phone Number"
              value={formData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>New Password (leave blank to keep current)</label>
            <input
              className="input-field"
              type="password"
              placeholder="New Password"
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
            />
          </div>
          <div className="btn-row">
            <button type="submit" className="btn">Save Changes</button>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SettingsModal;
