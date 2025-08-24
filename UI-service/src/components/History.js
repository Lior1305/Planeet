import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import userService from '../services/userService.js';

const History = () => {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(null);
  const [plans, setPlans] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const user = userService.getCurrentUser();
    if (!user) {
      // Redirect to login if not authenticated
      navigate('/login');
      return;
    }
    setCurrentUser(user);
    
    // TODO: Load user's planning history from the planning service
    // For now, we'll show a placeholder
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  }, [navigate]);

  if (!currentUser) {
    return null; // Will redirect to login
  }

  if (isLoading) {
    return (
      <div className="container" style={{ marginTop: '40px', textAlign: 'center' }}>
        <div style={{ fontSize: '32px', marginBottom: '16px' }}>⏳</div>
        <p>Loading your planning history...</p>
      </div>
    );
  }

  return (
    <div className="container" style={{ marginTop: '40px' }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <h1 style={{ fontSize: '36px', marginBottom: '16px' }}>Your Planning History</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '18px' }}>
          Track your past adventures and plans
        </p>
      </div>

      {plans.length === 0 ? (
        <div style={{ 
          background: 'var(--background)', 
          padding: '48px', 
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '24px' }}>📚</div>
          <h2 style={{ fontSize: '24px', marginBottom: '16px' }}>No plans yet</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', maxWidth: '500px', margin: '0 auto 32px' }}>
            You haven't created any plans yet. Start planning your first outing and it will appear here!
          </p>
          
          <button 
            className="btn btn-primary" 
            onClick={() => navigate('/plan')}
            style={{ fontSize: '18px', padding: '16px 32px' }}
          >
            <span className="icon">🚀</span> Start Planning
          </button>
        </div>
      ) : (
        <div style={{ 
          display: 'grid',
          gap: '24px'
        }}>
          {plans.map((plan, index) => (
            <div key={index} style={{ 
              background: 'var(--background)', 
              padding: '24px', 
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
              boxShadow: 'var(--shadow)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '20px', margin: 0 }}>{plan.name}</h3>
                <span style={{ 
                  background: 'var(--accent-2)', 
                  color: 'white', 
                  padding: '4px 12px', 
                  borderRadius: 'var(--radius)',
                  fontSize: '14px'
                }}>
                  {plan.status || 'Completed'}
                </span>
              </div>
              
              <div style={{ 
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '16px',
                marginBottom: '16px'
              }}>
                <div>
                  <strong>Location:</strong> {plan.location?.city || 'N/A'}
                </div>
                <div>
                  <strong>Date:</strong> {plan.date ? new Date(plan.date).toLocaleDateString() : 'N/A'}
                </div>
                <div>
                  <strong>Group Size:</strong> {plan.group_size || 'N/A'} people
                </div>
                <div>
                  <strong>Venues:</strong> {plan.venue_types?.join(', ') || 'N/A'}
                </div>
              </div>
              
              <div style={{ 
                display: 'flex',
                gap: '12px',
                justifyContent: 'flex-end'
              }}>
                <button className="btn btn-outline" style={{ fontSize: '14px', padding: '8px 16px' }}>
                  View Details
                </button>
                <button className="btn btn-primary" style={{ fontSize: '14px', padding: '8px 16px' }}>
                  Plan Again
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
