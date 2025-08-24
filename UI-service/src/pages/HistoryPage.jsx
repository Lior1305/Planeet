import React from 'react';
import { useUser } from '../contexts/UserContext';

const HistoryPage = () => {
  const { currentUser } = useUser();

  // Mock data - in a real app, this would come from your backend
  const mockOutings = [
    {
      id: 1,
      name: 'Weekend in Tel Aviv',
      date: '2024-01-15',
      venueTypes: ['restaurant', 'cafe'],
      status: 'completed'
    },
    {
      id: 2,
      name: 'Jerusalem Day Trip',
      date: '2024-01-10',
      venueTypes: ['museum', 'restaurant'],
      status: 'completed'
    },
    {
      id: 3,
      name: 'Haifa Beach Day',
      date: '2024-01-05',
      venueTypes: ['restaurant', 'park'],
      status: 'cancelled'
    }
  ];

  if (!currentUser) {
    return (
      <div className="container">
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <h2>Please log in to view your history</h2>
          <p>You need to be authenticated to view this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <section className="hero">
        <div className="container">
          <h1>Previous Outings</h1>
          <p>Review your past adventures and plans</p>
        </div>
      </section>

      <section style={{ padding: '60px 0' }}>
        {mockOutings.length > 0 ? (
          <div>
            {mockOutings.map(outing => (
              <div key={outing.id} className="outing-item">
                <div className="outing-header">
                  <h3>{outing.name}</h3>
                  <span className={`outing-status ${outing.status}`}>
                    {outing.status}
                  </span>
                </div>
                <div className="outing-details">
                  <p><strong>Date:</strong> {new Date(outing.date).toLocaleDateString()}</p>
                  <p><strong>Venue Types:</strong> {outing.venueTypes.join(', ')}</p>
                </div>
                <div className="outing-actions">
                  <button className="btn btn-secondary">View Details</button>
                  <button className="btn btn-primary">Plan Similar</button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-outings">
            <span className="icon">📋</span>
            <h3>No outings yet</h3>
            <p>Start planning your first adventure to see it here!</p>
            <button className="btn btn-primary">Start Planning</button>
          </div>
        )}
      </section>
    </div>
  );
};

export default HistoryPage;
