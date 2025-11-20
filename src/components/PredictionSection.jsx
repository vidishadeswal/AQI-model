import React from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Filler,
    Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import './PredictionSection.css';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Filler,
    Legend
);

const PredictionSection = ({ data }) => {
    if (!data) return null;

    const labels = ['Now', ...data.map(d => d.time)];
    // Prepend current value (mocked as 168 for continuity or take from props if available)
    const dataPoints = [168, ...data.map(d => d.val)];

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                titleColor: '#1a202c',
                bodyColor: '#4a5568',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                padding: 10,
                displayColors: false,
            },
        },
        scales: {
            x: {
                grid: {
                    display: false,
                },
                ticks: {
                    color: '#718096',
                    font: {
                        size: 11
                    }
                }
            },
            y: {
                grid: {
                    color: 'rgba(0,0,0,0.05)',
                },
                ticks: {
                    color: '#718096',
                    font: {
                        size: 11
                    }
                },
                suggestedMin: 100,
                suggestedMax: 200,
            },
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }
    };

    const chartData = {
        labels,
        datasets: [
            {
                fill: true,
                label: 'PM2.5',
                data: dataPoints,
                borderColor: '#3a7bd5',
                backgroundColor: (context) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
                    gradient.addColorStop(0, 'rgba(58, 123, 213, 0.4)');
                    gradient.addColorStop(1, 'rgba(58, 123, 213, 0.0)');
                    return gradient;
                },
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: '#3a7bd5',
                pointBorderWidth: 2,
            },
        ],
    };

    return (
        <section className="prediction-section h-full">
            <div className="card graph-card h-full flex-col">
                <div className="flex-between mb-4">
                    <h2 className="section-title mb-0">Next 6-Hour Forecast</h2>
                    <div className="legend flex-center gap-2">
                        <span className="dot-legend"></span>
                        <span className="text-sm text-secondary">Predicted Trend</span>
                    </div>
                </div>

                <div className="chart-container flex-1">
                    <Line options={options} data={chartData} />
                </div>

                <div className="prediction-cards mt-4">
                    {data.map((pred, idx) => (
                        <div key={idx} className="mini-card">
                            <div className="time-label">{pred.time}</div>
                            <div className="pred-value">{pred.val}</div>
                            <div className="indicator-row">
                                <span className="dot" style={{ backgroundColor: pred.color }}></span>
                                <span className="mini-label">{pred.label}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default PredictionSection;
