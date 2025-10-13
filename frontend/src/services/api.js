import { supabase } from './supabase';
import axios from 'axios';


// ============================================
// AXIOS SETUP
// ============================================


const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';


const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});


// Global error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error?.response?.data || error.message);
    return Promise.reject(error);
  }
);


// Simple logger for debugging
const logger = {
  info: (...args) => console.log('[API Info]:', ...args),
  error: (...args) => console.error('[API Error]:', ...args),
};


// ============================================
// HEALTH DATA (land_health table via health view)
// ============================================


export const getLatestHealth = async (locationId) => {
  try {
    // Try Supabase first
    const { data, error } = await supabase
      .from('health')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: false })
      .limit(1)
      .single();


    if (error) throw error;
    return { data };
  } catch (error) {
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/land-health/${locationId}/latest`);
      return { data: response.data };
    } catch (apiError) {
      console.error('Error fetching health data:', error);
      return { data: null, error };
    }
  }
};


export const getHealthHistory = async (locationId, limit = 30) => {
  try {
    const { data, error } = await supabase
      .from('health')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: false })
      .limit(limit);


    if (error) throw error;
    return { data };
  } catch (error) {
    console.error('Error fetching health history:', error);
    return { data: [], error };
  }
};


// ============================================
// RISK DATA (degradation_risk table via risk view)
// ============================================


export const getLatestRisk = async (locationId) => {
  try {
    // Try Supabase first
    const { data, error } = await supabase
      .from('risk')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: false })
      .limit(1)
      .single();


    if (error) throw error;
    return { data };
  } catch (error) {
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/risk/${locationId}/latest`);
      return { data: response.data };
    } catch (apiError) {
      console.error('Error fetching risk data:', error);
      return { data: null, error };
    }
  }
};


export const getRiskTrend = async (locationId, days = 30, months = 6) => {
  try {
    // Try Supabase first
    const { data, error } = await supabase
      .from('risk')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: true })
      .limit(days);


    if (error) throw error;
    return { data };
  } catch (error) {
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/risk/${locationId}/trend`, {
        params: { months },
      });
      return { data: response.data };
    } catch (apiError) {
      console.error('Error fetching risk trend:', error);
      return { data: [], error };
    }
  }
};


// ============================================
// CLIMATE DATA (climate_data table via climate_forecast view)
// ============================================


export const getClimateForecast = async (locationId, days = 7) => {
  try {
    // Try Supabase first
    const { data, error } = await supabase
      .from('climate_forecast')
      .select('*')
      .eq('location_id', locationId)
      .order('timestamp', { ascending: true })
      .limit(days);


    if (error) throw error;
    return { data };
  } catch (error) {
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/climate/${locationId}/latest`, { params: { days } });
      return { data: response.data };
    } catch (apiError) {
      console.error('Error fetching climate forecast:', error);
      return { data: [], error };
    }
  }
};


export const getCurrentWeather = async (locationId) => {
  try {
    const { data, error } = await supabase
      .from('weather_realtime')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: false })
      .limit(1)
      .single();


    if (error) throw error;
    return { data };
  } catch (error) {
    console.error('Error fetching current weather:', error);
    return { data: null, error };
  }
};


// ============================================
// LOCATIONS
// ============================================


export const getLocations = async () => {
  try {
    // Try Supabase first
    const { data, error } = await supabase
      .from('locations')
      .select('*')
      .order('name', { ascending: true });


    if (error) throw error;
    return { data };
  } catch (error) {
    // Fallback to FastAPI
    try {
      const response = await api.get('/api/locations');
      return { data: response.data };
    } catch (apiError) {
      console.error('Error fetching locations:', error);
      return { data: [], error };
    }
  }
};


export const getLocationById = async (locationId) => {
  try {
    // Try Supabase first
    const { data, error } = await supabase
      .from('locations')
      .select('*')
      .eq('id', locationId)
      .single();


    if (error) throw error;
    return { data };
  } catch (error) {
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/locations/${locationId}`);
      return { data: response.data };
    } catch (apiError) {
      console.error('Error fetching location:', error);
      return { data: null, error };
    }
  }
};


// Alias for consistency with FastAPI version
export const getLocation = getLocationById;


// ============================================
// ALERTS
// ============================================


export const getActiveAlerts = async (locationId) => {
  try {
    const { data, error } = await supabase
      .from('alerts')
      .select('*')
      .eq('location_id', locationId)
      .eq('is_active', true)
      .order('created_at', { ascending: false });


    if (error) throw error;
    return { data };
  } catch (error) {
    console.error('Error fetching alerts:', error);
    return { data: [], error };
  }
};


export const markAlertAsRead = async (alertId) => {
  try {
    const { data, error } = await supabase
      .from('alerts')
      .update({ read_at: new Date().toISOString() })
      .eq('id', alertId)
      .select()
      .single();


    if (error) throw error;
    return { data };
  } catch (error) {
    console.error('Error marking alert as read:', error);
    return { data: null, error };
  }
};


// ============================================
// RECOMMENDATIONS
// ============================================


export const getRecommendations = async (locationId) => {
  try {
    // Try Supabase first
    const { data, error } = await supabase
      .from('recommendations')
      .select('*')
      .eq('location_id', locationId)
      .eq('is_active', true)
      .order('priority', { ascending: false })
      .order('created_at', { ascending: false });


    if (error) throw error;
    return { data };
  } catch (error) {
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/recommendations/${locationId}`);
      return { data: response.data };
    } catch (apiError) {
      console.error('Error fetching recommendations:', error);
      return { data: [], error };
    }
  }
};


export const updateRecommendationStatus = async (recommendationId, status) => {
  try {
    const updates = { status };
    if (status === 'completed') {
      updates.completed_at = new Date().toISOString();
    }


    const { data, error } = await supabase
      .from('recommendations')
      .update(updates)
      .eq('id', recommendationId)
      .select()
      .single();


    if (error) throw error;
    return { data };
  } catch (error) {
    console.error('Error updating recommendation:', error);
    return { data: null, error };
  }
};


export const generateRecommendations = async (locationId) => {
  try {
    logger.info(`Calling generateRecommendations for location: ${locationId}`);
    const response = await api.post(`/api/recommendations/generate/${locationId}`);
    logger.info('Generate recommendations response:', response.data);
    return response;
  } catch (error) {
    console.error('Failed to generate recommendations:', error);
    console.error('Error details:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
      url: error.config?.url,
    });
    throw error;
  }
};


// ============================================
// DASHBOARD SUMMARY
// ============================================


export const getDashboardSummary = async (locationId) => {
  try {
    const [health, risk, forecast, alerts, recommendations] = await Promise.all([
      getLatestHealth(locationId),
      getLatestRisk(locationId),
      getClimateForecast(locationId, 7),
      getActiveAlerts(locationId),
      getRecommendations(locationId),
    ]);


    return {
      data: {
        health: health.data,
        risk: risk.data,
        forecast: forecast.data,
        alerts: alerts.data,
        recommendations: recommendations.data,
      },
      error: null,
    };
  } catch (error) {
    console.error('Error fetching dashboard summary:', error);
    return { data: null, error };
  }
};


// ============================================
// EXPORT ALL
// ============================================


export default {
  // Health
  getLatestHealth,
  getHealthHistory,
 
  // Risk
  getLatestRisk,
  getRiskTrend,
 
  // Climate
  getClimateForecast,
  getCurrentWeather,
 
  // Locations
  getLocations,
  getLocationById,
  getLocation,
 
  // Alerts
  getActiveAlerts,
  markAlertAsRead,
 
  // Recommendations
  getRecommendations,
  updateRecommendationStatus,
  generateRecommendations,
 
  // Dashboard
  getDashboardSummary,
 
  // Axios instance (for custom requests)
  api,
};
