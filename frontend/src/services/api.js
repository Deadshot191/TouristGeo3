import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance with interceptors
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};

// Tourists API
export const touristsAPI = {
  getTourists: async (filters = {}) => {
    const params = new URLSearchParams();
    
    if (filters.status) params.append('status', filters.status);
    if (filters.nationality) params.append('nationality', filters.nationality);
    if (filters.search) params.append('search', filters.search);
    if (filters.skip) params.append('skip', filters.skip);
    if (filters.limit) params.append('limit', filters.limit);
    
    const response = await api.get(`/tourists?${params.toString()}`);
    return response.data;
  },
  
  getTourist: async (touristId) => {
    const response = await api.get(`/tourists/${touristId}`);
    return response.data;
  },
  
  updateTouristStatus: async (touristId, status, reason) => {
    const response = await api.put(`/tourists/${touristId}/status`, {
      status,
      reason
    });
    return response.data;
  },
  
  getTouristLocationHistory: async (touristId, limit = 100) => {
    const response = await api.get(`/tourists/${touristId}/location-history`, {
      params: { limit }
    });
    return response.data;
  }
};

// Location API
export const locationAPI = {
  updateLocation: async (locationData) => {
    const response = await api.post('/location/update', locationData);
    return response.data;
  },
  
  getLiveLocations: async () => {
    const response = await api.get('/location/live');
    return response.data;
  }
};

// Alerts API
export const alertsAPI = {
  getAlerts: async (filters = {}) => {
    const params = new URLSearchParams();
    
    if (filters.alert_type) params.append('alert_type', filters.alert_type);
    if (filters.status) params.append('status', filters.status);
    if (filters.severity) params.append('severity', filters.severity);
    if (filters.search) params.append('search', filters.search);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.skip) params.append('skip', filters.skip);
    if (filters.limit) params.append('limit', filters.limit);
    
    const response = await api.get(`/alerts?${params.toString()}`);
    return response.data;
  },
  
  createPanicAlert: async (touristId, longitude, latitude, address) => {
    const response = await api.post('/alerts/panic', {
      tourist_id: touristId,
      longitude,
      latitude,
      address
    });
    return response.data;
  },
  
  updateAlertStatus: async (alertId, status, resolvedBy, resolutionNotes) => {
    const response = await api.put(`/alerts/${alertId}/status`, {
      status,
      resolved_by: resolvedBy,
      resolution_notes: resolutionNotes
    });
    return response.data;
  },
  
  addResponseAction: async (alertId, action) => {
    const response = await api.post(`/alerts/${alertId}/actions`, null, {
      params: { action }
    });
    return response.data;
  }
};

// Geofences API
export const geofencesAPI = {
  getGeofences: async (activeOnly = true) => {
    const response = await api.get('/geofences', {
      params: { active_only: activeOnly }
    });
    return response.data;
  },
  
  createGeofence: async (geofenceData) => {
    const response = await api.post('/geofences', geofenceData);
    return response.data;
  },
  
  checkGeofences: async (longitude, latitude) => {
    const response = await api.get('/geofences/check', {
      params: { longitude, latitude }
    });
    return response.data;
  }
};

// Analytics API
export const analyticsAPI = {
  getDashboardKPIs: async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  },
  
  getSafetyScore: async (touristId) => {
    const response = await api.get(`/analytics/safety-score/${touristId}`);
    return response.data;
  },
  
  getLocationAnalytics: async (hours = 24) => {
    const response = await api.get('/analytics/location', {
      params: { hours }
    });
    return response.data;
  },
  
  getAlertAnalytics: async (days = 7) => {
    const response = await api.get('/analytics/alerts', {
      params: { days }
    });
    return response.data;
  }
};

// WebSocket connections
export class WebSocketManager {
  constructor() {
    this.dashboardWS = null;
    this.callbacks = {
      location_update: [],
      new_alert: [],
      status_change: [],
      alert_resolved: [],
      emergency: []
    };
  }
  
  connectDashboard() {
    const wsUrl = `${BACKEND_URL.replace('http', 'ws')}/api/ws/dashboard`;
    
    this.dashboardWS = new WebSocket(wsUrl);
    
    this.dashboardWS.onopen = () => {
      console.log('Dashboard WebSocket connected');
    };
    
    this.dashboardWS.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
      }
    };
    
    this.dashboardWS.onclose = () => {
      console.log('Dashboard WebSocket disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        this.connectDashboard();
      }, 5000);
    };
    
    this.dashboardWS.onerror = (error) => {
      console.error('Dashboard WebSocket error:', error);
    };
  }
  
  handleMessage(message) {
    const { type, data } = message;
    
    if (this.callbacks[type]) {
      this.callbacks[type].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket callback for ${type}:`, error);
        }
      });
    }
  }
  
  subscribe(eventType, callback) {
    if (this.callbacks[eventType]) {
      this.callbacks[eventType].push(callback);
    }
  }
  
  unsubscribe(eventType, callback) {
    if (this.callbacks[eventType]) {
      const index = this.callbacks[eventType].indexOf(callback);
      if (index > -1) {
        this.callbacks[eventType].splice(index, 1);
      }
    }
  }
  
  disconnect() {
    if (this.dashboardWS) {
      this.dashboardWS.close();
      this.dashboardWS = null;
    }
  }
  
  sendPing() {
    if (this.dashboardWS && this.dashboardWS.readyState === WebSocket.OPEN) {
      this.dashboardWS.send(JSON.stringify({ type: 'ping' }));
    }
  }
}

// Create global WebSocket manager instance
export const wsManager = new WebSocketManager();

export default api;