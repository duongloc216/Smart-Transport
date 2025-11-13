/**
 * Main App Component
 * Smart Traffic System Dashboard
 */

import React, { useState } from 'react';
import TrafficMap from './components/Map/TrafficMap';
import TrafficStats from './components/Dashboard/TrafficStats';
import RoutePlanner from './components/RoutePlanning/RoutePlanner';
import './App.css';

function App() {
  const [showRoutePlanner, setShowRoutePlanner] = useState(false);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🚦 Smart Traffic System</h1>
          <p className="header-subtitle">AI-Powered Traffic Prediction & Routing</p>
        </div>
        <div className="header-actions">
          <button 
            className="btn-primary"
            onClick={() => setShowRoutePlanner(true)}
          >
            📍 Tìm đường
          </button>
          <button className="btn-secondary">
            📊 Analytics
          </button>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {/* Traffic Statistics */}
          <section className="section">
            <TrafficStats />
          </section>

          {/* Traffic Map */}
          <section className="section">
            <TrafficMap />
          </section>

          {/* Footer Info */}
          <section className="section info-section">
            <div className="info-cards">
              <div className="info-card">
                <div className="info-icon">🤖</div>
                <h3>AI Prediction</h3>
                <p>Dự đoán traffic bằng LSTM, XGBoost, Prophet</p>
                <div className="info-stats">
                  <span className="badge">MAPE {"<"} 15%</span>
                </div>
              </div>

              <div className="info-card">
                <div className="info-icon">🗺️</div>
                <h3>Smart Routing</h3>
                <p>Thuật toán A* kết hợp ML predictions</p>
                <div className="info-stats">
                  <span className="badge">Tránh kẹt xe</span>
                  <span className="badge">Tối ưu thời gian</span>
                </div>
              </div>

              <div className="info-card">
                <div className="info-icon">⚡</div>
                <h3>Real-time Updates</h3>
                <p>Cập nhật traffic mỗi 30 giây</p>
                <div className="info-stats">
                  <span className="badge">10 segments</span>
                  <span className="badge">8,650+ records</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="app-footer">
        <p>© 2025 Smart Traffic System | Powered by FastAPI + React + ML</p>
      </footer>

      {/* Route Planner Modal */}
      <RoutePlanner 
        isOpen={showRoutePlanner}
        onClose={() => setShowRoutePlanner(false)}
      />
    </div>
  );
}

export default App;
