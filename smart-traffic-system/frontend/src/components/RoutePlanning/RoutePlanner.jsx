/**
 * Route Planning Component
 * Demo Predictive Time-Aware Routing
 */

import React, { useState } from 'react';
import { routingAPI } from '../../services/api';
import RouteMap from '../Map/RouteMap';
import './RoutePlanner.css';

const RoutePlanner = ({ isOpen, onClose }) => {
  const [origin, setOrigin] = useState('segment_001');
  const [destination, setDestination] = useState('segment_010');
  const [departureTime, setDepartureTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const segments = [
    'segment_001', 'segment_002', 'segment_003', 'segment_004', 'segment_005',
    'segment_006', 'segment_007', 'segment_008', 'segment_009', 'segment_010'
  ];

  const handleFindRoute = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Convert datetime-local format to ISO format if provided
      let formattedDepartureTime = null;
      if (departureTime) {
        // datetime-local gives "2025-11-13T11:24" format
        // Backend expects ISO format with seconds: "2025-11-13T11:24:00"
        formattedDepartureTime = departureTime + ':00';
      }

      const response = await routingAPI.findRoute(
        origin,
        destination,
        formattedDepartureTime
      );

      console.log('Route response:', response); // Debug log

      // Transform backend response structure to frontend expected structure
      if (response.success && response.route) {
        const transformedResult = {
          success: true,
          segments: response.route.segments || [],
          total_distance_km: response.route.total_distance || 0,
          estimated_time_min: response.route.total_duration || 0,
          path: response.route.segments?.map(s => s.segment_id) || [],
          departure_time: response.departure_time || response.generated_at,
          estimated_arrival_time: response.estimated_arrival_time || response.generated_at,
          prediction_based: response.prediction_based || response.route.traffic_conditions === 'ML-predicted',
          explanation: response.explanation || 'Route calculated using AI-predicted traffic at arrival times for each segment',
          incidents_avoided: response.incidents_avoided || 0
        };
        setResult(transformedResult);
      } else {
        setResult(response);
      }
    } catch (err) {
      console.error('Route error:', err); // Debug log
      setError(err.response?.data?.detail || err.message || 'Failed to find route');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="route-planner-overlay">
      <div className="route-planner-modal">
        <div className="modal-header">
          <h2>🗺️ AI-Powered Route Planning</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Input Form */}
          <div className="route-form">
            <div className="form-group">
              <label>📍 Điểm xuất phát (Origin)</label>
              <select value={origin} onChange={(e) => setOrigin(e.target.value)}>
                {segments.map(seg => (
                  <option key={seg} value={seg}>{seg}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>🎯 Điểm đến (Destination)</label>
              <select value={destination} onChange={(e) => setDestination(e.target.value)}>
                {segments.map(seg => (
                  <option key={seg} value={seg}>{seg}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>🕐 Thời gian xuất phát (Optional)</label>
              <input
                type="datetime-local"
                value={departureTime}
                onChange={(e) => setDepartureTime(e.target.value)}
                placeholder="Leave empty for now"
              />
              <small>Để trống = xuất phát ngay bây giờ</small>
            </div>

            <button
              className="btn-find-route"
              onClick={handleFindRoute}
              disabled={loading || origin === destination}
            >
              {loading ? '🔄 Đang tính toán...' : '🚀 Tìm tuyến đường tối ưu'}
            </button>

            {origin === destination && (
              <p className="error-msg">⚠️ Điểm xuất phát và đích phải khác nhau</p>
            )}
          </div>

          {/* Loading */}
          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Đang sử dụng AI để tính toán route tối ưu...</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="error-box">
              <h3>❌ Lỗi</h3>
              <p>{error}</p>
            </div>
          )}

          {/* Result */}
          {result && result.success && (
            <div className="route-result">
              <div className="result-header">
                <h3>✅ Tìm thấy tuyến đường tối ưu!</h3>
                {result.prediction_based && (
                  <span className="badge-ai">🤖 AI-Predicted</span>
                )}
              </div>

              <div className="route-summary">
                <div className="summary-card">
                  <div className="summary-icon">📏</div>
                  <div className="summary-info">
                    <span className="label">Tổng quãng đường</span>
                    <span className="value">{result.total_distance_km || 0} km</span>
                  </div>
                </div>

                <div className="summary-card">
                  <div className="summary-icon">⏱️</div>
                  <div className="summary-info">
                    <span className="label">Thời gian dự kiến</span>
                    <span className="value">{result.estimated_time_min || 0} phút</span>
                  </div>
                </div>

                <div className="summary-card">
                  <div className="summary-icon">🚦</div>
                  <div className="summary-info">
                    <span className="label">Số đoạn đường</span>
                    <span className="value">{result.segments?.length || 0}</span>
                  </div>
                </div>
              </div>

              {/* Time Info */}
              {result.departure_time && result.estimated_arrival_time && (
                <div className="time-info">
                  <div className="time-item">
                    <span>🕐 Xuất phát:</span>
                    <strong>{new Date(result.departure_time).toLocaleString('vi-VN')}</strong>
                  </div>
                  <div className="time-item">
                    <span>🏁 Dự kiến tới nơi:</span>
                    <strong>{new Date(result.estimated_arrival_time).toLocaleString('vi-VN')}</strong>
                  </div>
                </div>
              )}

              {/* AI Explanation */}
              {result.explanation && (
                <div className="ai-explanation">
                  <h4>💡 Cách tính toán:</h4>
                  <p>{result.explanation}</p>
                </div>
              )}

              {/* Route Map Visualization */}
              <RouteMap routeData={result} />

              {/* Route Segments */}
              {result.segments && result.segments.length > 0 && (
                <div className="segments-list">
                  <h4>📍 Chi tiết tuyến đường ({result.path?.length || result.segments.length} điểm):</h4>
                  <div className="segments-timeline">
                    {result.segments.map((segment, index) => (
                      <div key={index} className="segment-item">
                        <div className="segment-number">{index + 1}</div>
                        <div className="segment-details">
                          <div className="segment-header">
                            <strong>{segment.segment_id}</strong>
                            {segment.arrival_time && (
                              <span className="arrival-time">
                                🕐 {new Date(segment.arrival_time).toLocaleTimeString('vi-VN')}
                              </span>
                            )}
                          </div>
                          <div className="segment-info">
                            <span>📏 {segment.distance_km || 0} km</span>
                            <span>⚡ Max: {segment.max_speed || 0} km/h</span>
                            {segment.has_incident && (
                              <span className="incident-badge">⚠️ Có sự cố</span>
                            )}
                          </div>
                          {segment.name && <p className="segment-name">{segment.name}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Show result even if success is missing */}
          {result && !result.success && !error && (
            <div className="error-box">
              <h3>❌ Không tìm thấy tuyến đường</h3>
              <p>{result.error || 'Unknown error'}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RoutePlanner;
