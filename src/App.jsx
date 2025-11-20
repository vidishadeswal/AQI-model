import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import CurrentAQI from './components/CurrentAQI';
import PredictionSection from './components/PredictionSection';
import DetailedMetrics from './components/DetailedMetrics';
import ConfidenceSection from './components/ConfidenceSection';
import PollutantBreakdown from './components/PollutantBreakdown';
import WeatherCard from './components/WeatherCard';
import ActivityAdvice from './components/ActivityAdvice';
import PredictionControl from './components/PredictionControl';
import LoadingState from './components/LoadingState';
import ErrorState from './components/ErrorState';
import Footer from './components/Footer';
import { useAirQuality } from './hooks/useAirQuality';

function App() {
  const { data, loading, error, calculatePrediction } = useAirQuality();
  const [selectedTimeIndex, setSelectedTimeIndex] = useState(-1); // Pending selection
  const [displayedTimeIndex, setDisplayedTimeIndex] = useState(-1); // Actual displayed data

  // Handle "Update Prediction" click
  const handleUpdatePrediction = () => {
    setDisplayedTimeIndex(selectedTimeIndex);
    // No need to re-fetch data, just update the view with existing forecast
  };

  // Helper to get data for the displayed time
  const getDisplayData = () => {
    if (!data) return null;
    if (displayedTimeIndex === -1) return data; // Return full data object for "Now"

    // For forecast hours, construct a view similar to the main data object
    const forecastItem = data.forecast[displayedTimeIndex];
    return {
      ...data,
      current: {
        ...data.current,
        ...forecastItem.current, // Override weather
        val: forecastItem.val,
        status: forecastItem.label,
        color: forecastItem.color,
        recommendation: `Forecast for ${forecastItem.time}`,
        time: forecastItem.time
      },
      metrics: {
        ...forecastItem.metrics, // Override pollutants
        trend: data.metrics.trend // Preserve historical trend
      },
      advice: forecastItem.advice // Override advice
    };
  };

  const displayData = getDisplayData();

  return (
    <div className="app-container">
      <Sidebar />

      <main className="main-content">
        <Header />

        {error && <ErrorState onRetry={() => window.location.reload()} />}

        {!data && loading && <LoadingState />}

        {displayData && (
          <div className="content-scrollable">
            <div className="dashboard-grid">
              {/* Row 1: Current Status, Controls, Weather */}
              <div className="grid-item item-current">
                <CurrentAQI data={displayData.current} />
              </div>

              <div className="grid-item item-controls">
                <PredictionControl
                  forecast={data.forecast}
                  onTimeSelect={setSelectedTimeIndex}
                  selectedTimeIndex={selectedTimeIndex}
                  onCalculate={handleUpdatePrediction}
                  isCalculating={loading}
                />
              </div>

              <div className="grid-item item-weather">
                <WeatherCard data={displayData.current} />
              </div>

              {/* Row 2: Prediction Graph */}
              <div className="grid-item item-prediction">
                <PredictionSection data={data.forecast} />
              </div>

              {/* Row 3: Pollutants & Advice */}
              <div className="grid-item item-pollutants">
                <PollutantBreakdown data={displayData} />
              </div>

              <div className="grid-item item-advice">
                <ActivityAdvice advice={displayData.advice} />
              </div>

              {/* Row 4: Confidence & Details */}
              <div className="grid-item item-confidence">
                <ConfidenceSection confidence={data.confidence} />
              </div>

              <div className="grid-item item-details">
                <DetailedMetrics data={displayData.metrics} />
              </div>
            </div>
            <Footer />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
