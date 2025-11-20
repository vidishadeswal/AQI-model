import React from 'react';
import './WeatherCard.css';
import { Cloud, Droplets, Wind, Compass } from 'lucide-react';

const WeatherCard = ({ data }) => {
    if (!data) return null;

    return (
        <div className="weather-card glass-card">
            <div className="card-header">
                <h3>Weather Details</h3>
            </div>
            <div className="weather-grid">
                <div className="weather-item">
                    <div className="weather-icon-wrapper temp-icon">
                        <Cloud size={24} />
                    </div>
                    <div className="weather-info">
                        <span className="weather-label">Temperature</span>
                        <span className="weather-value">{data.temp}</span>
                    </div>
                </div>

                <div className="weather-item">
                    <div className="weather-icon-wrapper humidity-icon">
                        <Droplets size={24} />
                    </div>
                    <div className="weather-info">
                        <span className="weather-label">Humidity</span>
                        <span className="weather-value">{data.humidity}</span>
                    </div>
                </div>

                <div className="weather-item">
                    <div className="weather-icon-wrapper wind-icon">
                        <Wind size={24} />
                    </div>
                    <div className="weather-info">
                        <span className="weather-label">Wind Speed</span>
                        <span className="weather-value">{data.wind}</span>
                    </div>
                </div>

                <div className="weather-item">
                    <div className="weather-icon-wrapper dir-icon">
                        <Compass size={24} style={{ transform: `rotate(${data.wind_dir}deg)` }} />
                    </div>
                    <div className="weather-info">
                        <span className="weather-label">Wind Direction</span>
                        <span className="weather-value">{data.wind_dir}°</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WeatherCard;
