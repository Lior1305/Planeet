import React from 'react';

const HowItWorksModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const steps = [
    {
      icon: '🔐',
      title: 'Create Your Account',
      description: 'Sign up or log in to your Planeet account to get started with planning your perfect outing.'
    },
    {
      icon: '🎯',
      title: 'Set Your Preferences',
      description: 'Tell us about your preferences - cuisine type, budget, group size, and any special requirements.'
    },
    {
      icon: '📋',
      title: 'Choose Your Plan',
      description: 'Browse through our AI-generated suggestions and pick the perfect plan that matches your preferences.'
    },
    {
      icon: '🎉',
      title: 'Book & Enjoy',
      description: 'Reserve your venues and enjoy an amazing night out with friends and family!'
    },
    {
      icon: '⭐',
      title: 'Rate & Improve',
      description: 'Share your experience by rating venues and providing feedback to help us serve you better next time.'
    }
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal how-it-works-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">How Planeet Works</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        
        <div className="modal-body">
          <div className="steps-container">
            {steps.map((step, index) => (
              <div key={index} className="step-item">
                <div className="step-number">{index + 1}</div>
                <div className="step-content">
                  <div className="step-icon">{step.icon}</div>
                  <h3 className="step-title">{step.title}</h3>
                  <p className="step-description">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="modal-actions">
          <button className="btn btn-primary" onClick={onClose}>
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
};

export default HowItWorksModal;
