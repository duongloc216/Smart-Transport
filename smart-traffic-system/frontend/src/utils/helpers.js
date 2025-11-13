/**
 * Helper utility functions
 */

// Get color by congestion status
export const getColorByCongestion = (status) => {
  const colors = {
    'FREE_FLOW': '#00ff00',      // Green
    'FLOWING': '#00ff00',         // Green
    'MODERATE': '#ffff00',        // Yellow
    'HEAVY_CONGESTION': '#ff0000',// Red
    'CONGESTED': '#ff0000',       // Red
  };
  return colors[status] || '#999999';
};

// Get color by speed
export const getColorBySpeed = (speed, maxSpeed = 40) => {
  const ratio = speed / maxSpeed;
  if (ratio > 0.7) return '#00ff00'; // Green - good speed
  if (ratio > 0.4) return '#ffff00'; // Yellow - moderate
  return '#ff0000'; // Red - slow
};

// Format date/time
export const formatDateTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('vi-VN');
};

// Format time only
export const formatTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
};

// Format duration (minutes to readable string)
export const formatDuration = (minutes) => {
  if (minutes < 60) {
    return `${Math.round(minutes)} phút`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  return `${hours}h ${mins}m`;
};

// Format distance
export const formatDistance = (km) => {
  if (km < 1) {
    return `${Math.round(km * 1000)} m`;
  }
  return `${km.toFixed(1)} km`;
};

// Calculate congestion level from probability
export const getCongestionLevel = (probability) => {
  if (probability < 0.3) return 'Thông thoáng';
  if (probability < 0.6) return 'Trung bình';
  return 'Kẹt xe';
};

// Get status badge color
export const getStatusBadgeColor = (status) => {
  const colors = {
    'FREE_FLOW': 'success',
    'FLOWING': 'success',
    'MODERATE': 'warning',
    'HEAVY_CONGESTION': 'error',
    'CONGESTED': 'error',
  };
  return colors[status] || 'default';
};
