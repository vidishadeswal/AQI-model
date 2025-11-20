import React from 'react';
import './ActivityAdvice.css';
import { Activity, Shield, Wind } from 'lucide-react';

const ActivityAdvice = ({ advice }) => {
    if (!advice) return null;

    return (
        <div className="advice-card glass-card">
            <div className="card-header">
                <h3>Health & Activity</h3>
            </div>
            <div className="advice-list">
                <div className="advice-item">
                    <div className="advice-icon-wrapper activity-bg">
                        <Activity size={20} />
                    </div>
                    <div className="advice-content">
                        <span className="advice-label">Outdoor Activity</span>
                        <p className="advice-text">{advice.activity}</p>
                    </div>
                </div>

                <div className="advice-item">
                    <div className="advice-icon-wrapper mask-bg">
                        <Shield size={20} />
                    </div>
                    <div className="advice-content">
                        <span className="advice-label">Mask Recommendation</span>
                        <p className="advice-text">{advice.mask}</p>
                    </div>
                </div>

                <div className="advice-item">
                    <div className="advice-icon-wrapper ventilation-bg">
                        <Wind size={20} />
                    </div>
                    <div className="advice-content">
                        <span className="advice-label">Ventilation</span>
                        <p className="advice-text">{advice.ventilation}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ActivityAdvice;
