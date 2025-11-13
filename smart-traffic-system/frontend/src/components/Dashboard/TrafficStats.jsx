/**
 * TrafficStats Component
 * Displays traffic statistics cards
 */

import React, { useState, useEffect } from 'react';
import { trafficAPI } from '../../services/api';
import './TrafficStats.css';

const TrafficStats = () => {
  const [stats, setStats] = useState({
    totalSegments: 0,
    congested: 0,
    moderate: 0,
    freeFlow: 0,
    avgSpeed: 0,
    totalIntensity: 0,
  });
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const data = await trafficAPI.getAllTraffic();
      if (data.success) {
        const segments = data.data;

        const congested = segments.filter(s => 
          s.congestion_status === 'HEAVY_CONGESTION' || s.congestion_status === 'CONGESTED'
        ).length;
        
        const moderate = segments.filter(s => 
          s.congestion_status === 'MODERATE'
        ).length;
        
        const freeFlow = segments.filter(s => 
          s.congestion_status === 'FREE_FLOW' || s.congestion_status === 'FLOWING'
        ).length;

        const avgSpeed = segments.reduce((sum, s) => sum + s.speed, 0) / segments.length;
        const totalIntensity = segments.reduce((sum, s) => sum + s.intensity, 0);

        setStats({
          totalSegments: segments.length,
          congested,
          moderate,
          freeFlow,
          avgSpeed: avgSpeed.toFixed(1),
          totalIntensity: Math.round(totalIntensity),
        });
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="stats-loading">Đang tải thống kê...</div>;
  }

  return (
    <div className="traffic-stats">
      <h2 className="stats-title">📊 Thống kê Traffic</h2>
      
      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-icon">🛣️</div>
          <div className="stat-content">
            <div className="stat-label">Tổng số đoạn đường</div>
            <div className="stat-value">{stats.totalSegments}</div>
          </div>
        </div>

        <div className="stat-card congested">
          <div className="stat-icon">🔴</div>
          <div className="stat-content">
            <div className="stat-label">Kẹt xe</div>
            <div className="stat-value">{stats.congested}</div>
            <div className="stat-subtitle">
              {stats.totalSegments > 0 
                ? `${((stats.congested / stats.totalSegments) * 100).toFixed(0)}%`
                : '0%'
              }
            </div>
          </div>
        </div>

        <div className="stat-card moderate">
          <div className="stat-icon">🟡</div>
          <div className="stat-content">
            <div className="stat-label">Trung bình</div>
            <div className="stat-value">{stats.moderate}</div>
            <div className="stat-subtitle">
              {stats.totalSegments > 0 
                ? `${((stats.moderate / stats.totalSegments) * 100).toFixed(0)}%`
                : '0%'
              }
            </div>
          </div>
        </div>

        <div className="stat-card free-flow">
          <div className="stat-icon">🟢</div>
          <div className="stat-content">
            <div className="stat-label">Thông thoáng</div>
            <div className="stat-value">{stats.freeFlow}</div>
            <div className="stat-subtitle">
              {stats.totalSegments > 0 
                ? `${((stats.freeFlow / stats.totalSegments) * 100).toFixed(0)}%`
                : '0%'
              }
            </div>
          </div>
        </div>

        <div className="stat-card speed">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <div className="stat-label">Tốc độ trung bình</div>
            <div className="stat-value">{stats.avgSpeed}</div>
            <div className="stat-subtitle">km/h</div>
          </div>
        </div>

        <div className="stat-card intensity">
          <div className="stat-icon">🚗</div>
          <div className="stat-content">
            <div className="stat-label">Tổng lưu lượng</div>
            <div className="stat-value">{stats.totalIntensity.toLocaleString()}</div>
            <div className="stat-subtitle">xe/giờ</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrafficStats;
