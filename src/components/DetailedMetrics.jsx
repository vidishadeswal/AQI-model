import React from 'react';
import { Activity, CloudRain, Layers } from 'lucide-react';
import './DetailedMetrics.css';

const MetricCard = ({ title, icon: Icon, children }) => {
    return (
        <div className="metric-card">
            <div className="metric-header flex-center gap-2">
                <div className="icon-box">
                    <Icon size={18} color="var(--color-blue)" />
                </div>
                <span className="metric-title">{title}</span>
            </div>
            <div className="metric-content">
                {children}
            </div>
        </div>
    );
};

const DetailedMetrics = ({ data }) => {
    if (!data) return null;

    return (
        <section className="detailed-metrics-section h-full">
            <div className="card h-full flex-col">
                <h3 className="section-title">Analysis & Breakdown</h3>

                <div className="metrics-grid">
                    <MetricCard title="Past Hour Trend" icon={Activity}>
                        <div className="trend-content">
                            <p className="text-sm text-secondary mb-2">Rising steadily over last 6h.</p>
                            <div className="simple-bar-chart">
                                {data.trend.map((val, i) => (
                                    <div key={i} className="bar-col">
                                        <div className="bar" style={{ height: `${(val / 200) * 100}%` }}></div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </MetricCard>

                    <MetricCard title="Weather Impact" icon={CloudRain}>
                        <div className="weather-impact-grid">
                            <div className="impact-item">
                                <span className="impact-label">Humidity</span>
                                <span className="impact-val">High</span>
                                <span className="impact-desc">Traps pollutants.</span>
                            </div>
                            <div className="impact-item">
                                <span className="impact-label">Wind</span>
                                <span className="impact-val">Mod</span>
                                <span className="impact-desc">Helps dispersion.</span>
                            </div>
                        </div>
                    </MetricCard>

                    <MetricCard title="Pollutant Breakdown" icon={Layers}>
                        <div className="pollutant-list">
                            {data.pollutants.map((p, i) => (
                                <div key={i} className="pollutant-row flex-between">
                                    <span className="p-name">{p.name}</span>
                                    <div className="flex-center gap-2">
                                        <span className="p-val">{p.val} <small>{p.unit}</small></span>
                                        <span className="p-dot" style={{ backgroundColor: p.color }}></span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </MetricCard>
                </div>
            </div>
        </section>
    );
};

export default DetailedMetrics;
