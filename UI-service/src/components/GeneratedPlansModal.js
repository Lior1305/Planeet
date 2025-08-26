import React from 'react';

const GeneratedPlansModal = ({ plans, onPlanSelection, onRegenerate, onClose }) => {
  if (!plans || !plans.plans) return null;

  const formatPriceRange = (priceRange) => {
    if (!priceRange) return 'N/A';
    return priceRange === '$' ? 'Budget-friendly' : 
           priceRange === '$$' ? 'Mid-range' : 
           priceRange === '$$$' ? 'Premium' : priceRange;
  };

  const formatDuration = (duration) => {
    return `${duration} hour${duration !== 1 ? 's' : ''}`;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal generated-plans-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Choose Your Perfect Plan</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        
        <div className="modal-body">
          <div className="plans-summary">
            <p className="plans-intro">
              We've generated <strong>{plans.total_plans_generated} personalized plans</strong> for you! 
              Each plan includes {plans.plans[0]?.suggested_venues?.length || 0} venues carefully selected 
              based on your preferences.
            </p>
          </div>

          <div className="plans-container">
            {plans.plans.map((plan, index) => (
              <div key={plan.plan_id} className="plan-card">
                <div className="plan-header">
                  <h3 className="plan-title">Plan {index + 1}</h3>
                  <div className="plan-meta">
                    <span className="plan-duration">
                      ⏱️ {formatDuration(plan.estimated_total_duration)}
                    </span>
                    <span className="plan-venues">
                      📍 {plan.venue_types_included.length} venue types
                    </span>
                  </div>
                </div>

                <div className="venues-list">
                  {plan.suggested_venues.map((venue) => (
                    <div key={venue.venue_id} className="venue-item">
                      <div className="venue-header">
                        <h4 className="venue-name">{venue.name}</h4>
                        <div className="venue-badges">
                          <span className="venue-type-badge">{venue.venue_type}</span>
                          <span className="venue-rating">⭐ {venue.rating}</span>
                          <span className="venue-price">{formatPriceRange(venue.price_range)}</span>
                        </div>
                      </div>
                      <p className="venue-address">{venue.address}</p>
                      {venue.url_link && (
                        <a 
                          href={venue.url_link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="venue-link"
                        >
                          Visit Website →
                        </a>
                      )}
                    </div>
                  ))}
                </div>

                <div className="plan-actions">
                  <button 
                    className="btn btn-primary"
                    onClick={() => onPlanSelection(plan)}
                  >
                    Choose This Plan
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="modal-actions">
          <button className="btn btn-outline" onClick={onRegenerate}>
            🔄 Regenerate Plans
          </button>
          <button className="btn btn-outline" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default GeneratedPlansModal;
