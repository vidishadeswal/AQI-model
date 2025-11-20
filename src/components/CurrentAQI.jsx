import React from 'react';
import { Thermometer, Droplets, Wind } from 'lucide-react';
import './CurrentAQI.css';

const CurrentAQI = ({ data }) => {
  if (!data) return null;

  return (
    <div className="current-aqi-card glass-card" style={{ '--card-glow': data.color }}>
      <div className="card-header">
        <h3>Air Quality Index</h3>
        <span className="live-badge">
          {data.time === "Now" ? "LIVE" : data.time}
        </span>
      </div>

      <div className="hero-content">
        <div className="aqi-circle" style={{ borderColor: data.color, boxShadow: `0 0 20px ${data.color}40` }}>
          <div className="aqi-value" style={{ color: data.color }}>
            {data.val || data.pm25}
          </div>
          <div className="aqi-label">AQI</div>
        </div>

        <div className="status-container">
          <div className="aqi-status-chip" style={{ backgroundColor: data.color }}>
            {data.status}
          </div>
          <p className="aqi-recommendation">
            {data.recommendation || "Check detailed metrics for more info."}
          </p>
        </div>
      </div>

      <div className="weather-row">
        <div className="weather-item">
          <Thermometer size={20} className="weather-icon" />
          <div className="weather-info">
            <span className="w-label">Temp</span>
            <span className="w-value">{data.temp}</span>
          </div>
        </div>
        <div className="weather-item">
          <Droplets size={20} className="weather-icon" />
          <div className="weather-info">
            <span className="w-label">Humidity</span>
            <span className="w-value">{data.humidity}</span>
          </div>
        </div>
        <div className="weather-item">
          <Wind size={20} className="weather-icon" />
          <div className="weather-info">
            <span className="w-label">Wind</span>
            <span className="w-value">{data.wind}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurrentAQI;
