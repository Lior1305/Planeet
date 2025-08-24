import React from 'react';
import { Link } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';

const DashboardHub = () => {
  const { currentUser } = useUser();

  // Redirect if not authenticated (you could add this logic)
  if (!currentUser) {
    return (
      <div className="container">
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <h2>Please log in to access your dashboard</h2>
          <p>You need to be authenticated to view this page.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-eyebrow">Welcome to Planeet</div>
          <h1>Your Adventure Hub</h1>
          <p>Choose what you'd like to do today and start planning amazing experiences with friends.</p>
        </div>
      </section>

      {/* Hub Cards */}
      <section className="container" style={{ padding: '60px 0' }}>
        <div className="feature-grid">
          <article className="feature-card fc-1">
            <div className="fc-icon">📅</div>
            <h3>Plan New Outing</h3>
            <p>Create a new adventure plan with our multi-step wizard</p>
            <Link to="/plan" className="btn btn-primary">Start Planning</Link>
          </article>
          
          <article className="feature-card fc-2">
            <div className="fc-icon">👤</div>
            <h3>My Profile</h3>
            <p>View and edit your profile information and settings</p>
            <Link to="/profile" className="btn btn-secondary">View Profile</Link>
          </article>
          
          <article className="feature-card fc-3">
            <div className="fc-icon">📋</div>
            <h3>Previous Outings</h3>
            <p>Browse your past adventures and plans</p>
            <Link to="/history" className="btn btn-secondary">View History</Link>
          </article>
        </div>
      </section>
    </>
  );
};

export default DashboardHub;
