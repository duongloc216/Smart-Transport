/**
 * API Service
 * Handles all API calls to backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Traffic API
export const trafficAPI = {
  // Get all traffic segments real-time
  getAllTraffic: async () => {
    const response = await api.get('/traffic/realtime/all');
    return response.data;
  },

  // Get current traffic for one segment
  getCurrentTraffic: async (segmentId) => {
    const response = await api.get(`/traffic/current/${segmentId}`);
    return response.data;
  },

  // Get traffic history
  getHistory: async (segmentId, limit = 288) => {
    const response = await api.get(`/traffic/history/${segmentId}`, {
      params: { limit }
    });
    return response.data;
  },

  // Predict future traffic
  predictTraffic: async (segmentId, horizon = 15, modelType = 'ensemble') => {
    const response = await api.post('/traffic/predict', {
      road_segment_id: segmentId,
      prediction_horizon: horizon,
      model_type: modelType
    });
    return response.data;
  },

  // Get models info
  getModelsInfo: async () => {
    const response = await api.get('/traffic/models/info');
    return response.data;
  },
};

// Routing API
export const routingAPI = {
  // Find optimal route
  findRoute: async (origin, destination, departureTime = null) => {
    const response = await api.post('/routing/find-route', {
      origin,
      destination,
      departure_time: departureTime,
      mode: 'optimal'
    });
    return response.data;
  },

  // Find alternative routes
  findAlternatives: async (origin, destination, numRoutes = 3) => {
    const response = await api.post('/routing/alternative-routes', {
      origin,
      destination,
      num_alternatives: numRoutes
    });
    return response.data;
  },

  // Get road status
  getRoadStatus: async (segmentId) => {
    const response = await api.get(`/routing/road-status/${segmentId}`);
    return response.data;
  },
};

// Incidents API
export const incidentsAPI = {
  // Get all accidents
  getAccidents: async () => {
    const response = await api.get('/incidents/accidents');
    return response.data;
  },

  // Get all roadworks
  getRoadworks: async () => {
    const response = await api.get('/incidents/roadworks');
    return response.data;
  },

  // Get all incidents
  getAllIncidents: async () => {
    const response = await api.get('/incidents/all-incidents');
    return response.data;
  },
};

export default api;
