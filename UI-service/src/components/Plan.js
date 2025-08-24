import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import userService from '../services/userService.js';
import PlanningModal from './PlanningModal.js';

const Plan = () => {
  const navigate = useNavigate();
  const [isPlanningModalOpen, setIsPlanningModalOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const user = userService.getCurrentUser();
    if (!user) {
      // Redirect to login if not authenticated
      navigate('/login');
      return;
    }
    setCurrentUser(user);
  }, [navigate]);

  const handleOpenPlanningForm = () => {
    setIsPlanningModalOpen(true);
  };

  const handlePlanCreated = (plan) => {
    console.log('Plan created:', plan);
    // You can add additional logic here, like showing a success message
    // or redirecting to a plan view page
  };

  if (!currentUser) {
    return null; // Will redirect to login
  }

  return (
    <div className="container" style={{ marginTop: '40px' }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <h1 style={{ fontSize: '36px', marginBottom: '16px' }}>Plan Your Outing</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '18px' }}>
          Welcome back, {currentUser.username}! Let's create an amazing plan together.
        </p>
      </div>

      <div style={{ 
        background: 'var(--background)', 
        padding: '48px', 
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow)',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '64px', marginBottom: '24px' }}>🎯</div>
        <h2 style={{ fontSize: '24px', marginBottom: '16px' }}>Ready to start planning?</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', maxWidth: '500px', margin: '0 auto 32px' }}>
          Our intelligent planning system will help you find the perfect venues based on your preferences, 
          group size, and location. Let's create something amazing!
        </p>
        
        <button 
          className="btn btn-primary" 
          onClick={handleOpenPlanningForm}
          style={{ fontSize: '18px', padding: '16px 32px' }}
        >
          <span className="icon">🚀</span> Start Planning Now
        </button>
      </div>

      <div style={{ 
        marginTop: '48px',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px'
      }}>
        <div style={{ 
          background: 'var(--background)', 
          padding: '24px', 
          borderRadius: 'var(--radius)',
          border: '1px solid var(--border)'
        }}>
          <div style={{ fontSize: '32px', marginBottom: '16px' }}>📍</div>
          <h3 style={{ marginBottom: '12px' }}>Smart Location</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            We'll find the best venues near your chosen location with real-time availability.
          </p>
        </div>

        <div style={{ 
          background: 'var(--background)', 
          padding: '24px', 
          borderRadius: 'var(--radius)',
          border: '1px solid var(--border)'
        }}>
          <div style={{ fontSize: '32px', marginBottom: '16px' }}>👥</div>
          <h3 style={{ marginBottom: '12px' }}>Group Optimization</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Venues are selected based on your group size and preferences for the best experience.
          </p>
        </div>

        <div style={{ 
          background: 'var(--background)', 
          padding: '24px', 
          borderRadius: 'var(--radius)',
          border: '1px solid var(--border)'
        }}>
          <div style={{ fontSize: '32px', marginBottom: '16px' }}>⚡</div>
          <h3 style={{ marginBottom: '12px' }}>Quick Results</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Get your personalized plan in seconds with detailed venue information and ratings.
          </p>
        </div>
      </div>

      {/* Planning Modal */}
      <PlanningModal
        isOpen={isPlanningModalOpen}
        onClose={() => setIsPlanningModalOpen(false)}
        onPlanCreated={handlePlanCreated}
      />
    </div>
  );
};

export default Plan;
