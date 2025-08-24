import React, { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext';

const ProfilePage = () => {
  const { currentUser, updateUser } = useUser();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    bio: ''
  });

  useEffect(() => {
    if (currentUser) {
      setFormData({
        name: currentUser.name || '',
        email: currentUser.email || '',
        phone: currentUser.phone || '',
        bio: currentUser.bio || ''
      });
    }
  }, [currentUser]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = () => {
    updateUser({
      ...currentUser,
      ...formData
    });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setFormData({
      name: currentUser?.name || '',
      email: currentUser?.email || '',
      phone: currentUser?.phone || '',
      bio: currentUser?.bio || ''
    });
    setIsEditing(false);
  };

  if (!currentUser) {
    return (
      <div className="container">
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <h2>Please log in to view your profile</h2>
          <p>You need to be authenticated to view this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <section className="hero">
        <div className="container">
          <h1>My Profile</h1>
          <p>Manage your account settings and preferences</p>
        </div>
      </section>

      <section style={{ padding: '60px 0' }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <div className="card">
            <div style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2>Profile Information</h2>
                {!isEditing && (
                  <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
                    Edit Profile
                  </button>
                )}
              </div>

              {isEditing ? (
                <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
                  <div className="form-group">
                    <label>Name</label>
                    <input
                      className="input-field"
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input
                      className="input-field"
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Phone</label>
                    <input
                      className="input-field"
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Bio</label>
                    <textarea
                      className="input-field"
                      rows="4"
                      value={formData.bio}
                      onChange={(e) => handleInputChange('bio', e.target.value)}
                    />
                  </div>
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                    <button type="submit" className="btn btn-primary">
                      Save Changes
                    </button>
                    <button type="button" className="btn btn-secondary" onClick={handleCancel}>
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <div>
                  <div style={{ marginBottom: '1rem' }}>
                    <strong>Name:</strong> {currentUser.name || 'Not set'}
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <strong>Email:</strong> {currentUser.email || 'Not set'}
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <strong>Phone:</strong> {currentUser.phone || 'Not set'}
                  </div>
                  <div style={{ marginBottom: '1rem' }}>
                    <strong>Bio:</strong> {currentUser.bio || 'No bio added yet'}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ProfilePage;
