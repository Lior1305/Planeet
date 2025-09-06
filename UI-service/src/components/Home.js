import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import userService from '../services/userService.js';
import PlanningModal from './PlanningModal.js';
import HowItWorksModal from './HowItWorksModal.js';

const Home = () => {
  const navigate = useNavigate();
  const [isPlanningModalOpen, setIsPlanningModalOpen] = useState(false);
  const [isHowItWorksModalOpen, setIsHowItWorksModalOpen] = useState(false);
  const currentUser = userService.getCurrentUser();

  const handleStartPlanning = () => {
    if (!currentUser) {
      alert('Please log in to plan an outing.');
      return;
    }
    setIsPlanningModalOpen(true);
  };

  const handlePlanCreated = (plan) => {
    console.log('Plan created:', plan);
    // You can add additional logic here, like redirecting to a plan view page
  };

  return (
    <>
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-eyebrow">Plan together, fast</div>
          <h1>Create Amazing Outings Together</h1>
          <p>Discover the best venues, plan with friends, and make memories that last. Our comprehensive venue database helps you find the perfect spots for any occasion.</p>
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
            <h3>Personalized matching</h3>
            <p>Curated venue suggestions based on your preferences, budget, and group size.</p>
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
              <div className="stat-chip">Invite friends</div>
            </div>
            <div>
              <h2>Why choose Planeet?</h2>
              <p>We've built the most comprehensive venue discovery platform in Israel. From trendy cafes to hidden gems, we help you find exactly what you're looking for.</p>
              <button className="btn btn-secondary" onClick={() => setIsHowItWorksModalOpen(true)}>How it works</button>
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
        onPlanCreated={handlePlanCreated}
      />

      {/* How It Works Modal */}
      <HowItWorksModal
        isOpen={isHowItWorksModalOpen}
        onClose={() => setIsHowItWorksModalOpen(false)}
      />
    </>
  );
};

export default Home;
