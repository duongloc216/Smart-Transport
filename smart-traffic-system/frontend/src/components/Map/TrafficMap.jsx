/**
 * TrafficMap Component
 * Displays real-time traffic on a Leaflet map
 */

import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, Popup, CircleMarker } from 'react-leaflet';
import { trafficAPI } from '../../services/api';
import { getColorBySpeed } from '../../utils/helpers';
import './TrafficMap.css';

const TrafficMap = () => {
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // HCM City center
  const center = [10.8231, 106.6297];
  const zoom = 13;

  // Fetch traffic data
  const fetchTrafficData = async () => {
    try {
      const data = await trafficAPI.getAllTraffic();
      if (data.success) {
        setSegments(data.data);
        setLastUpdate(new Date());
        setError(null);
      }
      setLoading(false);
    } catch (err) {
      console.error('Error fetching traffic:', err);
      setError('Không thể tải dữ liệu traffic');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrafficData();
    // Update every 30 seconds
    const interval = setInterval(fetchTrafficData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Segment coordinates (hardcoded for now - will be from database)
  const getSegmentCoordinates = (segmentId) => {
    const coords = {
      'segment_001': [[10.850758, 106.771806], [10.848920, 106.775353]],
      'segment_002': [[10.848920, 106.775353], [10.847082, 106.778900]],
      'segment_003': [[10.847082, 106.778900], [10.845244, 106.782447]],
      'segment_004': [[10.845244, 106.782447], [10.843406, 106.785994]],
      'segment_005': [[10.843406, 106.785994], [10.841568, 106.789541]],
      'segment_006': [[10.841568, 106.789541], [10.839730, 106.793088]],
      'segment_007': [[10.839730, 106.793088], [10.837892, 106.796635]],
      'segment_008': [[10.837892, 106.796635], [10.836054, 106.800182]],
      'segment_009': [[10.836054, 106.800182], [10.834216, 106.803729]],
      'segment_010': [[10.834216, 106.803729], [10.832378, 106.807276]],
    };
    return coords[segmentId] || null;
  };

  if (loading) {
    return (
      <div className="map-loading">
        <div className="spinner"></div>
        <p>Đang tải dữ liệu giao thông...</p>
      </div>
    );
  }

  return (
    <div className="traffic-map-container">
      {error && (
        <div className="map-error">
          {error}
          <button onClick={fetchTrafficData}>Thử lại</button>
        </div>
      )}

      <div className="map-header">
        <h2>🗺️ Bản đồ Traffic Real-time</h2>
        {lastUpdate && (
          <span className="last-update">
            Cập nhật: {lastUpdate.toLocaleTimeString('vi-VN')}
          </span>
        )}
      </div>

      <div className="map-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ background: '#00ff00' }}></span>
          <span>Thông thoáng ({">"} 30 km/h)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ background: '#ffff00' }}></span>
          <span>Trung bình (15-30 km/h)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ background: '#ff0000' }}></span>
          <span>Kẹt xe ({"<"} 15 km/h)</span>
        </div>
      </div>

      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '600px', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {segments.map((segment) => {
          const coords = getSegmentCoordinates(segment.road_segment_id);
          if (!coords) return null;

          const color = getColorBySpeed(segment.speed, 40);
          const midPoint = [
            (coords[0][0] + coords[1][0]) / 2,
            (coords[0][1] + coords[1][1]) / 2
          ];

          return (
            <React.Fragment key={segment.road_segment_id}>
              {/* Road segment line */}
              <Polyline
                positions={coords}
                color={color}
                weight={8}
                opacity={0.7}
              />

              {/* Midpoint marker with popup */}
              <CircleMarker
                center={midPoint}
                radius={6}
                fillColor={color}
                fillOpacity={0.8}
                color="#fff"
                weight={2}
              >
                <Popup>
                  <div className="traffic-popup">
                    <h3>{segment.road_name}</h3>
                    <div className="popup-stats">
                      <div className="stat-row">
                        <span className="stat-label">🚗 Tốc độ:</span>
                        <span className="stat-value">{segment.speed.toFixed(1)} km/h</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">🚦 Mật độ:</span>
                        <span className="stat-value">{segment.intensity.toFixed(0)} xe/h</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">📊 Trạng thái:</span>
                        <span className={`stat-badge ${segment.congestion_status.toLowerCase()}`}>
                          {segment.congestion_status}
                        </span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">⚠️ Kẹt xe:</span>
                        <span className="stat-value">
                          {(segment.congestion_probability * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default TrafficMap;
