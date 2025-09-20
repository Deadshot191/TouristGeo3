/**
 * E-FIR API Service
 * Handles all API calls related to Electronic First Information Reports
 */

import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

// Create axios instance with base configuration
const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('E-FIR API Error:', error);
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const efirAPI = {
  // Create new E-FIR document
  createEFIR: async (efirData) => {
    try {
      const response = await api.post('/efir', efirData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Failed to create E-FIR document'
      };
    }
  },

  // Get list of E-FIR documents with optional filters
  getEFIRList: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          params.append(key, value);
        }
      });

      const response = await api.get(`/efir?${params.toString()}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Failed to fetch E-FIR documents'
      };
    }
  },

  // Get specific E-FIR document by ID
  getEFIR: async (efirId) => {
    try {
      const response = await api.get(`/efir/${efirId}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Failed to fetch E-FIR document'
      };
    }
  },

  // Update E-FIR document
  updateEFIR: async (efirId, updateData) => {
    try {
      const response = await api.put(`/efir/${efirId}`, updateData);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Failed to update E-FIR document'
      };
    }
  },

  // Delete E-FIR document
  deleteEFIR: async (efirId) => {
    try {
      const response = await api.delete(`/efir/${efirId}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Failed to delete E-FIR document'
      };
    }
  },

  // Add digital signature to E-FIR document
  signEFIR: async (efirId, signaturePassword) => {
    try {
      const response = await api.post(`/efir/${efirId}/sign`, {
        document_id: efirId,
        signature_password: signaturePassword
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Failed to sign E-FIR document'
      };
    }
  },

  // Generate PDF for E-FIR document
  generatePDF: async (efirId) => {
    try {
      const response = await api.post(`/efir/${efirId}/generate-pdf`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Failed to generate PDF'
      };
    }
  },

  // Download PDF of E-FIR document
  downloadPDF: async (efirId) => {
    try {
      const response = await api.get(`/efir/${efirId}/download-pdf`, {
        responseType: 'blob'
      });
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      
      // Extract filename from response headers if available
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'e-fir-document.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      // Create temporary link and click it to download
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return { success: true, data: { message: 'PDF downloaded successfully' } };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Failed to download PDF'
      };
    }
  },

  // Get version history of E-FIR document
  getEFIRHistory: async (efirId) => {
    try {
      const response = await api.get(`/efir/${efirId}/history`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Failed to fetch document history'
      };
    }
  },

  // Verify E-FIR document (public endpoint)
  verifyEFIR: async (firNumber, documentHash) => {
    try {
      // Remove auth token for public endpoint
      const response = await axios.get(
        `${BACKEND_URL}/api/efir/verify/${firNumber}?document_hash=${documentHash}`,
        {
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Failed to verify document'
      };
    }
  },

  // Search E-FIR documents
  searchEFIR: async (searchQuery, filters = {}) => {
    try {
      const searchFilters = {
        ...filters,
        search: searchQuery,
        limit: filters.limit || 50
      };
      return await efirAPI.getEFIRList(searchFilters);
    } catch (error) {
      return { 
        success: false, 
        error: error.message || 'Failed to search E-FIR documents'
      };
    }
  }
};

// E-FIR Types and Status Options for UI components
export const EFIR_TYPES = [
  { value: 'tourist_incident', label: 'Tourist Incident' },
  { value: 'safety_violation', label: 'Safety Violation' },
  { value: 'emergency_response', label: 'Emergency Response' },
  { value: 'property_damage', label: 'Property Damage' },
  { value: 'medical_emergency', label: 'Medical Emergency' },
  { value: 'missing_person', label: 'Missing Person' }
];

export const EFIR_PRIORITIES = [
  { value: 'low', label: 'Low', color: 'text-green-600 bg-green-100' },
  { value: 'medium', label: 'Medium', color: 'text-yellow-600 bg-yellow-100' },
  { value: 'high', label: 'High', color: 'text-orange-600 bg-orange-100' },
  { value: 'urgent', label: 'Urgent', color: 'text-red-600 bg-red-100' }
];

export const EFIR_STATUSES = [
  { value: 'draft', label: 'Draft', color: 'text-gray-600 bg-gray-100' },
  { value: 'submitted', label: 'Submitted', color: 'text-blue-600 bg-blue-100' },
  { value: 'under_investigation', label: 'Under Investigation', color: 'text-orange-600 bg-orange-100' },
  { value: 'closed', label: 'Closed', color: 'text-green-600 bg-green-100' }
];

export default efirAPI;