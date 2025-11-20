import React from 'react';
import { Loader2 } from 'lucide-react';
import './LoadingState.css';

const LoadingState = () => {
    return (
        <div className="loading-container flex-center">
            <div className="loading-content text-center">
                <Loader2 className="spinner" size={48} color="var(--color-teal)" />
                <h3 className="loading-text">Generating predictions...</h3>
                <p className="loading-subtext text-secondary">Analyzing weather patterns & sensor data</p>
            </div>
        </div>
    );
};

export default LoadingState;
