import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import './ErrorState.css';

const ErrorState = ({ onRetry }) => {
    return (
        <div className="error-container flex-center">
            <div className="error-card card text-center">
                <div className="error-icon-bg flex-center">
                    <AlertTriangle size={32} color="#e53e3e" />
                </div>
                <h3 className="error-title">Unable to generate predictions</h3>
                <p className="error-msg text-secondary">
                    We couldn't connect to the AI model. Please check your internet connection and try again.
                </p>
                <button className="retry-btn flex-center" onClick={onRetry}>
                    <RefreshCw size={18} />
                    <span>Retry Analysis</span>
                </button>
            </div>
        </div>
    );
};

export default ErrorState;
