import React from 'react';

const HowItWorksModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const steps = [
    {
      icon: '🔐',
      title: 'Create Your Account',
      description: 'Sign up or log in to your Planeet account and start planning your perfect outing.'
    },
    {
      icon: '🎯',
      title: 'Set Your Preferences',
      description: 'Tell us what you like—cuisine, budget, group size, and any special requests.'
    },
    {
      icon: '📋',
      title: 'Pick a Plan',
      description: 'Browse the 3 personalized plans we create for you, or regenerate until you find the perfect match.'
    },
    {
      icon: '🎉',
      title: 'Book & Enjoy',
      description: 'Reserve your spots and get ready for a fun, stress-free night out with friends or family.'
    },
    {
      icon: '⭐',
      title: 'Share Feedback',
      description: 'Rate your experience and leave feedback so we can make your next outing even better.'
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
