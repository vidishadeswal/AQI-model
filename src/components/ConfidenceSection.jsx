import React from 'react';
import './ConfidenceSection.css';

const ConfidenceSection = ({ confidence }) => {
    if (!confidence) return null;

    return (
        <section className="confidence-section h-full">
            <div className="card confidence-card h-full flex-col justify-center">
                <h3 className="section-subtitle mb-4">Model Confidence</h3>

                <div className="flex-between mb-2">
                    <span className="confidence-label">Prediction Reliability</span>
                    <span className="confidence-value">{confidence}%</span>
                </div>

                <div className="progress-bar-bg">
                    <div
                        className="progress-bar-fill"
                        style={{ width: `${confidence}%` }}
                    ></div>
                </div>

                <p className="confidence-msg mt-4">
                    {confidence > 80 ? 'High confidence — weather patterns are stable.' : 'Moderate confidence — variable winds detected.'}
                </p>
            </div>
        </section>
    );
};

export default ConfidenceSection;
