import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import PlanningModal from '../components/PlanningModal';

const HomePage = () => {
  const { currentUser } = useUser();
  const navigate = useNavigate();
  const [isPlanningModalOpen, setIsPlanningModalOpen] = useState(false);

  const handleStartPlanning = () => {
    if (!currentUser) {
      // For now, just open the modal. In a real app, you'd redirect to login
      alert('Please log in to start planning');
      return;
    }
    setIsPlanningModalOpen(true);
  };

  const handlePlanningSubmit = (formData) => {
    console.log('Planning form submitted:', formData);
    // Here you would typically send the data to your backend
    // For now, just log it and redirect to dashboard
    navigate('/dashboard');
  };

  return (
    <>
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-eyebrow">Plan together, fast</div>
          <h1>Create Amazing Outings Together</h1>
          <p>Discover the best venues, plan with friends, and make memories that last. Our smart planning system helps you find the perfect spots for any occasion.</p>
          <button className="btn btn-primary" onClick={handleStartPlanning}>
            <span className="icon">🚀</span> Start Planning
          </button>
        </div>
      </section>

      {/* Wave Separator */}
      <svg className="wave-sep" viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true">
        <path d="M0,64 C240,144 480,-16 720,64 C960,144 1200,16 1440,64 L1440,120 L0,120 Z" fill="var(--accent-5)"/>
      </svg>

      {/* Feature Cards */}
      <section className="container">
        <div className="feature-grid">
          <article className="feature-card fc-1">
            <div className="fc-icon">💬</div>
            <h3>Decide together</h3>
            <p>Share options and vote in seconds. No more endless group chats about where to go.</p>
          </article>
          <article className="feature-card fc-2">
            <div className="fc-icon">📍</div>
            <h3>Live venues</h3>
            <p>Real-time availability and open status. Know before you go with up-to-date information.</p>
          </article>
          <article className="feature-card fc-3">
            <div className="fc-icon">🎯</div>
            <h3>Smart matching</h3>
            <p>AI-powered recommendations based on your preferences and group size.</p>
          </article>
          <article className="feature-card fc-4">
            <div className="fc-icon">❤️</div>
            <h3>Save favorites</h3>
            <p>Build your personal collection of go-to spots and share them with friends.</p>
          </article>
        </div>
      </section>

      {/* Highlights Band */}
      <section className="highlights">
        <div className="container">
          <div className="highlights-content">
            <div className="stat-chips">
              <div className="stat-chip">500+ venues</div>
              <div className="stat-chip">Real-time status</div>
              <div className="stat-chip">Smart AI</div>
            </div>
            <div>
              <h2>Why choose Planeet?</h2>
              <p>We've built the most comprehensive venue discovery platform in Israel. From trendy cafes to hidden gems, we help you find exactly what you're looking for.</p>
              <button className="btn btn-secondary">How it works</button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="container">
        <div className="footer-cta">
          <h2>Ready to plan your next adventure?</h2>
          <p>Join thousands of users who are already planning amazing outings with Planeet.</p>
          <button className="btn btn-primary" onClick={handleStartPlanning}>
            <span className="icon">🎉</span> Book your night out
          </button>
        </div>
      </section>

      {/* Planning Modal */}
      <PlanningModal
        isOpen={isPlanningModalOpen}
        onClose={() => setIsPlanningModalOpen(false)}
        onSubmit={handlePlanningSubmit}
      />
    </>
  );
};

export default HomePage;
