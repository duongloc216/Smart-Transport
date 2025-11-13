/**
 * RouteMap Component
 * Displays planned route on map like Google Maps
 */

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import RoutingControl from './RoutingControl';
import './RouteMap.css';

// Fix Leaflet default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons
const startIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSI0MCI+PGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTAiIGZpbGw9IiM0Mjg1RjQiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMyIvPjxwYXRoIGQ9Ik0xNiAyNSBRIDE2IDMwIDE2IDQwIiBzdHJva2U9IiM0Mjg1RjQiIHN0cm9rZS13aWR0aD0iMyIgZmlsbD0ibm9uZSIvPjwvc3ZnPg==',
  iconSize: [32, 40],
  iconAnchor: [16, 40],
});

const endIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSI0MCI+PGNpcmNsZSBjeD0iMTYiIGN5PSIxNiIgcj0iMTAiIGZpbGw9IiNFQTQzMzUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMyIvPjxwYXRoIGQ9Ik0xNiAyNSBRIDE2IDMwIDE2IDQwIiBzdHJva2U9IiNFQTQzMzUiIHN0cm9rZS13aWR0aD0iMyIgZmlsbD0ibm9uZSIvPjwvc3ZnPg==',
  iconSize: [32, 40],
  iconAnchor: [16, 40],
});

// Detailed street coordinates for each segment (Vo Van Ngan street)
const getSegmentDetailedCoordinates = (segmentId) => {
  // These are detailed coordinates that follow actual street layout
  const detailedCoords = {
    'segment_001': [
      [10.850758, 106.771806], [10.850600, 106.772150], [10.850450, 106.772480],
      [10.850300, 106.772800], [10.850100, 106.773200], [10.849900, 106.773600],
      [10.849700, 106.774000], [10.849400, 106.774500], [10.849100, 106.774950],
      [10.848920, 106.775353]
    ],
    'segment_002': [
      [10.848920, 106.775353], [10.848750, 106.775700], [10.848580, 106.776050],
      [10.848400, 106.776400], [10.848200, 106.776800], [10.848000, 106.777200],
      [10.847800, 106.777550], [10.847600, 106.777900], [10.847400, 106.778250],
      [10.847200, 106.778600], [10.847082, 106.778900]
    ],
    'segment_003': [
      [10.847082, 106.778900], [10.846900, 106.779250], [10.846700, 106.779600],
      [10.846500, 106.779950], [10.846300, 106.780300], [10.846100, 106.780700],
      [10.845900, 106.781100], [10.845700, 106.781500], [10.845500, 106.781900],
      [10.845350, 106.782250], [10.845244, 106.782447]
    ],
    'segment_004': [
      [10.845244, 106.782447], [10.845100, 106.782750], [10.844900, 106.783150],
      [10.844700, 106.783550], [10.844500, 106.783950], [10.844300, 106.784300],
      [10.844100, 106.784650], [10.843900, 106.785000], [10.843700, 106.785400],
      [10.843500, 106.785750], [10.843406, 106.785994]
    ],
    'segment_005': [
      [10.843406, 106.785994], [10.843250, 106.786300], [10.843050, 106.786700],
      [10.842850, 106.787100], [10.842650, 106.787500], [10.842450, 106.787900],
      [10.842250, 106.788300], [10.842050, 106.788700], [10.841850, 106.789100],
      [10.841700, 106.789350], [10.841568, 106.789541]
    ],
    'segment_006': [
      [10.841568, 106.789541], [10.841400, 106.789850], [10.841200, 106.790250],
      [10.841000, 106.790650], [10.840800, 106.791050], [10.840600, 106.791450],
      [10.840400, 106.791850], [10.840200, 106.792250], [10.840000, 106.792650],
      [10.839850, 106.792900], [10.839730, 106.793088]
    ],
    'segment_007': [
      [10.839730, 106.793088], [10.839550, 106.793400], [10.839350, 106.793800],
      [10.839150, 106.794200], [10.838950, 106.794600], [10.838750, 106.795000],
      [10.838550, 106.795400], [10.838350, 106.795800], [10.838150, 106.796200],
      [10.838000, 106.796450], [10.837892, 106.796635]
    ],
    'segment_008': [
      [10.837892, 106.796635], [10.837700, 106.796950], [10.837500, 106.797350],
      [10.837300, 106.797750], [10.837100, 106.798150], [10.836900, 106.798550],
      [10.836700, 106.798950], [10.836500, 106.799350], [10.836300, 106.799750],
      [10.836150, 106.800000], [10.836054, 106.800182]
    ],
    'segment_009': [
      [10.836054, 106.800182], [10.835850, 106.800500], [10.835650, 106.800900],
      [10.835450, 106.801300], [10.835250, 106.801700], [10.835050, 106.802100],
      [10.834850, 106.802500], [10.834650, 106.802900], [10.834450, 106.803300],
      [10.834300, 106.803550], [10.834216, 106.803729]
    ],
    'segment_010': [
      [10.834216, 106.803729], [10.834050, 106.804050], [10.833850, 106.804450],
      [10.833650, 106.804850], [10.833450, 106.805250], [10.833250, 106.805650],
      [10.833050, 106.806050], [10.832850, 106.806450], [10.832650, 106.806850],
      [10.832450, 106.807100], [10.832378, 106.807276]
    ],
  };
  return detailedCoords[segmentId] || null;
};

// Component to fit map to route bounds
function FitBounds({ route }) {
  const map = useMap();

  useEffect(() => {
    if (route && route.length > 0) {
      const bounds = L.latLngBounds(route);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [route, map]);

  return null;
}

const RouteMap = ({ routeData }) => {
  const center = [10.8231, 106.6297]; // HCM City

  if (!routeData || !routeData.segments || routeData.segments.length === 0) {
    return (
      <div className="route-map-empty">
        <p>⚠️ Không có dữ liệu route để hiển thị</p>
      </div>
    );
  }

  // Helper function to interpolate points between two coordinates (creates curved path)
  const interpolatePoints = (start, end, numPoints = 8) => {
    const [startLat, startLon] = start;
    const [endLat, endLon] = end;
    const points = [];
    
    for (let i = 0; i <= numPoints; i++) {
      const t = i / numPoints;
      // Use quadratic curve for more natural road-like path
      const curve = t * (2 - t); // Easing function
      const lat = startLat + (endLat - startLat) * curve;
      const lon = startLon + (endLon - startLon) * curve;
      points.push([lat, lon]);
    }
    
    return points;
  };

  // Build route coordinates from segments using REAL coordinates from backend
  const routeCoordinates = [];
  
  routeData.segments.forEach((segment, index) => {
    // Use coordinates from backend if available
    if (segment.start_coordinates && segment.end_coordinates) {
      const [startLon, startLat] = segment.start_coordinates;
      const [endLon, endLat] = segment.end_coordinates;
      
      const startPoint = [startLat, startLon];
      const endPoint = [endLat, endLon];
      
      // Add interpolated points to create smooth curve
      if (index === 0 || routeCoordinates.length === 0) {
        // First segment: add all interpolated points
        const interpolated = interpolatePoints(startPoint, endPoint, 12);
        routeCoordinates.push(...interpolated);
      } else {
        // Subsequent segments: skip first point to avoid duplication
        const interpolated = interpolatePoints(startPoint, endPoint, 12);
        routeCoordinates.push(...interpolated.slice(1));
      }
    } else {
      // Fallback to detailed hardcoded coordinates if backend doesn't provide
      const coords = getSegmentDetailedCoordinates(segment.segment_id);
      if (coords) {
        if (index === 0) {
          routeCoordinates.push(...coords);
        } else {
          // Skip first point to avoid duplication
          routeCoordinates.push(...coords.slice(1));
        }
      }
    }
  });

  // Start and end points
  const startPoint = routeCoordinates[0];
  const endPoint = routeCoordinates[routeCoordinates.length - 1];

  return (
    <div className="route-map-container">
      <div className="route-map-header">
        <h3>🗺️ Bản đồ tuyến đường</h3>
        <div className="route-stats-mini">
          <span>📏 {routeData.total_distance_km} km</span>
          <span>⏱️ {routeData.estimated_time_min} phút</span>
          <span>🚦 {routeData.segments.length} đoạn</span>
        </div>
      </div>

      <MapContainer
        center={center}
        zoom={13}
        style={{ height: '500px', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Use OSRM routing to draw real street-following path */}
        <RoutingControl 
          waypoints={routeCoordinates.length > 0 ? [startPoint, endPoint] : []}
          color="#4285F4"
        />

        {/* Fallback: Show interpolated line if routing fails */}
        {routeCoordinates.length > 2 && (
          <Polyline
            positions={routeCoordinates}
            color="#4285F4"
            weight={4}
            opacity={0.3}
            dashArray="5, 10"
          />
        )}

        {/* Start marker (green) */}
        <Marker position={startPoint} icon={startIcon}>
          <Popup>
            <div className="route-popup">
              <h4>🚀 Điểm xuất phát</h4>
              <p><strong>{routeData.segments[0].segment_id}</strong></p>
              <p>{routeData.segments[0].name}</p>
              {routeData.departure_time && (
                <p className="time-info">
                  🕐 {new Date(routeData.departure_time).toLocaleTimeString('vi-VN')}
                </p>
              )}
            </div>
          </Popup>
        </Marker>

        {/* End marker (red) */}
        <Marker position={endPoint} icon={endIcon}>
          <Popup>
            <div className="route-popup">
              <h4>🏁 Điểm đến</h4>
              <p><strong>{routeData.segments[routeData.segments.length - 1].segment_id}</strong></p>
              <p>{routeData.segments[routeData.segments.length - 1].name}</p>
              {routeData.estimated_arrival_time && (
                <p className="time-info">
                  🕐 {new Date(routeData.estimated_arrival_time).toLocaleTimeString('vi-VN')}
                </p>
              )}
            </div>
          </Popup>
        </Marker>

        {/* Waypoint markers for each segment */}
        {routeData.segments.slice(1, -1).map((segment, index) => {
          const coords = getSegmentDetailedCoordinates(segment.segment_id);
          if (!coords) return null;
          
          // Use middle point of the detailed coordinates
          const midIndex = Math.floor(coords.length / 2);
          const midPoint = coords[midIndex];

          return (
            <Marker
              key={segment.segment_id}
              position={midPoint}
              icon={L.divIcon({
                className: 'route-waypoint',
                html: `<div class="waypoint-number">${index + 2}</div>`,
                iconSize: [24, 24],
                iconAnchor: [12, 12],
              })}
            >
              <Popup>
                <div className="route-popup">
                  <h4>📍 Điểm {index + 2}</h4>
                  <p><strong>{segment.segment_id}</strong></p>
                  <p>{segment.name}</p>
                  <div className="segment-details">
                    <p>📏 Khoảng cách: {segment.distance_km} km</p>
                    <p>⚡ Tốc độ tối đa: {segment.max_speed} km/h</p>
                    {segment.arrival_time && (
                      <p className="time-info">
                        🕐 Tới lúc: {new Date(segment.arrival_time).toLocaleTimeString('vi-VN')}
                      </p>
                    )}
                    {segment.has_incident && (
                      <p className="warning">⚠️ Có sự cố trên đường</p>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Auto fit bounds to route */}
        <FitBounds route={routeCoordinates} />
      </MapContainer>

      {/* Route legend */}
      <div className="route-legend">
        <div className="legend-item">
          <div className="legend-marker start-marker"></div>
          <span>Điểm xuất phát</span>
        </div>
        <div className="legend-item">
          <div className="legend-marker end-marker"></div>
          <span>Điểm đến</span>
        </div>
        <div className="legend-item">
          <div className="legend-line"></div>
          <span>Tuyến đường AI-predicted</span>
        </div>
      </div>
    </div>
  );
};

export default RouteMap;
