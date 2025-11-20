import React from 'react';
import './PollutantBreakdown.css';

const PollutantBreakdown = ({ data }) => {
    if (!data || !data.metrics || !data.metrics.pollutants) return null;

    return (
        <div className="pollutant-breakdown-card glass-card">
            <div className="card-header">
                <h3>Pollutant Breakdown</h3>
                <span className="info-icon" title="Concentration of various pollutants">i</span>
            </div>
            <div className="pollutant-grid">
                {data.metrics.pollutants.map((item, index) => (
                    <div key={index} className="pollutant-item">
                        <div className="pollutant-header">
                            <span className="pollutant-name">{item.name}</span>
                            <span className="pollutant-unit">{item.unit}</span>
                        </div>
                        <div className="pollutant-value" style={{ color: item.color }}>
                            {item.val}
                        </div>
                        <div className="pollutant-bar-bg">
                            <div
                                className="pollutant-bar-fill"
                                style={{
                                    width: `${Math.min((item.val / (item.name === 'CO' ? 10 : 100)) * 100, 100)}%`,
                                    backgroundColor: item.color
                                }}
                            ></div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PollutantBreakdown;
