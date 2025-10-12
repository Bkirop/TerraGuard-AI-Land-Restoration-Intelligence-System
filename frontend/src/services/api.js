import { supabase } from './supabase';
import axios from 'axios';

// ============================================
// AXIOS SETUP
// ============================================

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://terraguard-api.onrender.com';
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
  warn: (...args) => console.warn('[API Warn]:', ...args),
  debug: (...args) => console.debug('[API Debug]:', ...args),
};

// ============================================
// HEALTH DATA (land_health table via health view)
// ============================================

export const getLatestHealth = async (locationId) => {
  try {
    logger.debug(`Fetching latest health for location: ${locationId}`);
    
    // Try Supabase first
    const { data, error } = await supabase
      .from('health')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: false })
      .limit(1)
      .single();

    if (error) throw error;
    
    logger.debug('✅ Health data fetched from Supabase');
    return { data };
  } catch (error) {
    logger.warn('Supabase health fetch failed, trying FastAPI fallback');
    
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/land-health/${locationId}/latest`);
      logger.debug('✅ Health data fetched from FastAPI');
      return { data: response.data };
    } catch (apiError) {
      logger.error('Error fetching health data from both sources:', error);
      return { data: null, error };
    }
  }
};

export const getHealthHistory = async (locationId, limit = 30) => {
  try {
    logger.debug(`Fetching health history for location: ${locationId}, limit: ${limit}`);
    
    const { data, error } = await supabase
      .from('health')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) throw error;
    
    logger.debug(`✅ Fetched ${data?.length || 0} health history records`);
    return { data };
  } catch (error) {
    logger.error('Error fetching health history:', error);
    return { data: [], error };
  }
};

// ============================================
// RISK DATA (degradation_risk table via risk view)
// ============================================

export const getLatestRisk = async (locationId) => {
  try {
    logger.debug(`Fetching latest risk for location: ${locationId}`);
    
    // Try Supabase first
    const { data, error } = await supabase
      .from('risk')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: false })
      .limit(1)
      .single();

    if (error) throw error;
    
    logger.debug('✅ Risk data fetched from Supabase');
    return { data };
  } catch (error) {
    logger.warn('Supabase risk fetch failed, trying FastAPI fallback');
    
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/risk/${locationId}/latest`);
      logger.debug('✅ Risk data fetched from FastAPI');
      return { data: response.data };
    } catch (apiError) {
      logger.error('Error fetching risk data from both sources:', error);
      return { data: null, error };
    }
  }
};

export const getRiskTrend = async (locationId, days = 30, months = 6) => {
  try {
    logger.debug(`Fetching risk trend for location: ${locationId}`);
    
    // Try Supabase first
    const { data, error } = await supabase
      .from('risk')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: true })
      .limit(days);

    if (error) throw error;
    
    logger.debug(`✅ Fetched ${data?.length || 0} risk trend records`);
    return { data };
  } catch (error) {
    logger.warn('Supabase risk trend fetch failed, trying FastAPI fallback');
    
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/risk/${locationId}/trend`, {
        params: { months },
      });
      logger.debug('✅ Risk trend fetched from FastAPI');
      return { data: response.data };
    } catch (apiError) {
      logger.error('Error fetching risk trend from both sources:', error);
      return { data: [], error };
    }
  }
};

// ============================================
// CLIMATE DATA (climate_data table via climate_forecast view)
// ============================================

export const getClimateForecast = async (locationId, days = 7) => {
  try {
    logger.debug(`Fetching climate forecast for location: ${locationId}, days: ${days}`);
    
    // Try Supabase first
    const { data, error } = await supabase
      .from('climate_forecast')
      .select('*')
      .eq('location_id', locationId)
      .order('timestamp', { ascending: true })
      .limit(days);

    if (error) throw error;
    
    logger.debug(`✅ Fetched ${data?.length || 0} climate forecast records`);
    return { data };
  } catch (error) {
    logger.warn('Supabase climate forecast fetch failed, trying FastAPI fallback');
    
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/climate/${locationId}/latest`, { params: { days } });
      logger.debug('✅ Climate forecast fetched from FastAPI');
      return { data: response.data };
    } catch (apiError) {
      logger.error('Error fetching climate forecast from both sources:', error);
      return { data: [], error };
    }
  }
};

export const getCurrentWeather = async (locationId) => {
  try {
    logger.debug(`Fetching current weather for location: ${locationId}`);
    
    const { data, error } = await supabase
      .from('weather_realtime')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: false })
      .limit(1)
      .single();

    if (error) throw error;
    
    logger.debug('✅ Current weather fetched');
    return { data };
  } catch (error) {
    logger.error('Error fetching current weather:', error);
    return { data: null, error };
  }
};

// ============================================
// LOCATIONS
// ============================================

export const getLocations = async () => {
  try {
    logger.debug('Fetching all locations');
    
    // Try Supabase first
    const { data, error } = await supabase
      .from('locations')
      .select('*')
      .order('name', { ascending: true });

    if (error) throw error;
    
    logger.debug(`✅ Fetched ${data?.length || 0} locations from Supabase`);
    return { data };
  } catch (error) {
    logger.warn('Supabase locations fetch failed, trying FastAPI fallback');
    
    // Fallback to FastAPI
    try {
      const response = await api.get('/api/locations');
      logger.debug('✅ Locations fetched from FastAPI');
      return { data: response.data };
    } catch (apiError) {
      logger.error('Error fetching locations from both sources:', error);
      return { data: [], error };
    }
  }
};

export const getLocationById = async (locationId) => {
  try {
    logger.debug(`Fetching location by ID: ${locationId}`);
    
    // Try Supabase first
    const { data, error } = await supabase
      .from('locations')
      .select('*')
      .eq('id', locationId)
      .single();

    if (error) throw error;
    
    logger.debug('✅ Location fetched from Supabase');
    return { data };
  } catch (error) {
    logger.warn('Supabase location fetch failed, trying FastAPI fallback');
    
    // Fallback to FastAPI
    try {
      const response = await api.get(`/api/locations/${locationId}`);
      logger.debug('✅ Location fetched from FastAPI');
      return { data: response.data };
    } catch (apiError) {
      logger.error('Error fetching location from both sources:', error);
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
    logger.debug(`Fetching active alerts for location: ${locationId}`);
    
    const { data, error } = await supabase
      .from('alerts')
      .select('*')
      .eq('location_id', locationId)
      .eq('is_active', true)
      .order('created_at', { ascending: false });

    if (error) throw error;
    
    logger.debug(`✅ Fetched ${data?.length || 0} active alerts`);
    return { data };
  } catch (error) {
    logger.error('Error fetching alerts:', error);
    return { data: [], error };
  }
};

export const markAlertAsRead = async (alertId) => {
  try {
    logger.debug(`Marking alert as read: ${alertId}`);
    
    const { data, error } = await supabase
      .from('alerts')
      .update({ read_at: new Date().toISOString() })
      .eq('id', alertId)
      .select()
      .single();

    if (error) throw error;
    
    logger.debug('✅ Alert marked as read');
    return { data };
  } catch (error) {
    logger.error('Error marking alert as read:', error);
    return { data: null, error };
  }
};

// ============================================
// RECOMMENDATIONS (FIXED)
// ============================================

export const getRecommendations = async (locationId) => {
  logger.info(`📋 Fetching recommendations for location: ${locationId}`);
  
  try {
    // Try Supabase first - REMOVED is_active filter as it might not exist or be set
    const { data, error } = await supabase
      .from('recommendations')
      .select('*')
      .eq('location_id', locationId)
      .order('created_at', { ascending: false })
      .limit(10);

    if (error) {
      logger.error('❌ Supabase error fetching recommendations:', error.message);
      throw error;
    }
    
    const count = data?.length || 0;
    logger.info(`✅ Fetched ${count} recommendation${count !== 1 ? 's' : ''} from Supabase`);
    
    if (count > 0) {
      logger.debug('Sample recommendation:', data[0]);
    }
    
    return { data: data || [] };
    
  } catch (supabaseError) {
    // Fallback to FastAPI
    logger.warn('⚠️ Trying FastAPI fallback for recommendations...');
    
    try {
      const response = await api.get(`/api/recommendations/${locationId}`);
      logger.debug('FastAPI raw response:', response.data);
      
      // Handle different response structures from backend
      let recommendations = 
        response.data?.data?.data ||        // Nested data object
        response.data?.data ||              // Single data wrapper
        response.data?.recommendations ||   // Named recommendations field
        response.data ||                    // Direct array
        [];
      
      // Ensure it's always an array
      if (!Array.isArray(recommendations)) {
        if (recommendations && typeof recommendations === 'object') {
          recommendations = [recommendations];
        } else {
          recommendations = [];
        }
      }
      
      const count = recommendations.length;
      logger.info(`✅ Fetched ${count} recommendation${count !== 1 ? 's' : ''} from FastAPI`);
      
      if (count > 0) {
        logger.debug('Sample recommendation:', recommendations[0]);
      }
      
      return { data: recommendations };
      
    } catch (apiError) {
      logger.error('❌ Error fetching recommendations from both sources:', {
        supabaseError: supabaseError.message,
        apiError: apiError.response?.data || apiError.message,
        apiStatus: apiError.response?.status
      });
      
      // Return empty array instead of throwing to prevent UI from breaking
      return { data: [], error: apiError };
    }
  }
};

export const updateRecommendationStatus = async (recommendationId, status) => {
  try {
    logger.debug(`Updating recommendation ${recommendationId} status to: ${status}`);
    
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
    
    logger.debug('✅ Recommendation status updated');
    return { data };
  } catch (error) {
    logger.error('Error updating recommendation:', error);
    return { data: null, error };
  }
};

export const generateRecommendations = async (locationId) => {
  try {
    logger.info(`🤖 Generating recommendations for location: ${locationId}`);
    
    const response = await api.post(`/api/recommendations/generate/${locationId}`);
    
    logger.info('✅ Generate recommendations response:', {
      status: response.status,
      success: response.data?.success,
      message: response.data?.message,
      count: response.data?.data?.length || 0,
      aiPowered: response.data?.ai_powered
    });
    
    if (response.data?.data && Array.isArray(response.data.data)) {
      logger.debug('Generated recommendations:', response.data.data);
    }
    
    // Return the data object directly for easier handling in components
    return response.data;
    
  } catch (error) {
    logger.error('❌ Failed to generate recommendations:', {
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
    logger.info(`📊 Fetching dashboard summary for location: ${locationId}`);
    
    const [health, risk, forecast, alerts, recommendations] = await Promise.all([
      getLatestHealth(locationId),
      getLatestRisk(locationId),
      getClimateForecast(locationId, 7),
      getActiveAlerts(locationId),
      getRecommendations(locationId),
    ]);

    const summary = {
      health: health.data,
      risk: risk.data,
      forecast: forecast.data,
      alerts: alerts.data,
      recommendations: recommendations.data,
    };
    
    logger.info('✅ Dashboard summary loaded:', {
      hasHealth: !!summary.health,
      hasRisk: !!summary.risk,
      forecastCount: summary.forecast?.length || 0,
      alertsCount: summary.alerts?.length || 0,
      recommendationsCount: summary.recommendations?.length || 0
    });

    return {
      data: summary,
      error: null,
    };
  } catch (error) {
    logger.error('Error fetching dashboard summary:', error);
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