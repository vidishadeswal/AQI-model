import React from 'react';
import './PredictionControl.css';
import { Clock, Zap } from 'lucide-react';

const PredictionControl = ({ forecast, onTimeSelect, selectedTimeIndex, onCalculate, isCalculating }) => {
    return (
        <div className="prediction-control-card glass-card">
            <div className="control-header">
                <h3>Prediction Controls</h3>
                <Clock size={20} className="header-icon" />
            </div>

            <div className="control-body">
                <div className="time-select-group">
                    <label className="control-label">Select Time</label>
                    <div className="select-wrapper">
                        <select
                            value={selectedTimeIndex}
                            onChange={(e) => onTimeSelect(Number(e.target.value))}
                            className="time-dropdown"
                        >
                            <option value={-1}>Now (Live)</option>
                            {forecast && forecast.map((item, index) => (
                                <option key={index} value={index}>
                                    +{index + 1}h ({item.time})
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <button
                    className="calculate-btn"
                    onClick={onCalculate}
                    disabled={isCalculating}
                >
                    {isCalculating ? (
                        <>
                            <span className="spinner-small"></span>
                            Processing...
                        </>
                    ) : (
                        <>
                            <Zap size={18} />
                            Update Prediction
                        </>
                    )}
                </button>
            </div>
        </div>
    );
};

export default PredictionControl;
