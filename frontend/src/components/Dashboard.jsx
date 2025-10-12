import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { AlertCircle, Leaf, Cloud, TrendingUp, MapPin } from 'lucide-react';
import ClimateChart from './ClimateChart';
import RiskChart from './RiskChart';
import RecommendationsList from './RecommendationsList';
import RealtimeWeatherWidget from './RealtimeWeatherWidget';
import RealtimeAlerts from './RealtimeAlerts';
import { useSupabaseRealtime } from '../hooks/useSupabaseRealtime';
import { getLatestHealth, getLatestRisk, getClimateForecast } from '../services/api';

const Dashboard = ({ locationId, locationName }) => {
  const [health, setHealth] = useState(null);
  const [risk, setRisk] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // === STABLE REALTIME OPTIONS ===
  const healthOpts = useMemo(
    () => ({
      filter: locationId ? { location_id: locationId } : {},
      orderBy: { column: 'created_at', ascending: false },
      limit: 1,
    }),
    [locationId]
  );

  const riskOpts = useMemo(
    () => ({
      filter: locationId ? { location_id: locationId } : {},
      orderBy: { column: 'created_at', ascending: false },
      limit: 1,
    }),
    [locationId]
  );

  const forecastOpts = useMemo(
    () => ({
      filter: locationId ? { location_id: locationId } : {},
      orderBy: { column: 'timestamp', ascending: true },
      limit: 7,
    }),
    [locationId]
  );

  // === REALTIME SUBSCRIPTIONS ===
  const { data: liveHealth, loading: healthLoading, connected: healthConnected } = 
    useSupabaseRealtime('health', healthOpts);
    
  const { data: liveRisk, loading: riskLoading, connected: riskConnected } = 
    useSupabaseRealtime('risk', riskOpts);
    
  const { data: liveForecast, loading: forecastLoading, connected: forecastConnected } = 
    useSupabaseRealtime('climate_forecast', forecastOpts);

  // === NORMALIZE BACKEND RESPONSE ===
  const normalizeResponse = useCallback((res) => {
    if (!res) return null;
    const data = res?.data?.data ?? res?.data ?? res;
    return Array.isArray(data) ? data[0] : data;
  }, []);

  // === INITIAL DATA LOAD (FALLBACK) ===
  const loadDashboardData = useCallback(async () => {
    if (!locationId) {
      setLoading(false);
      return;
    }

    console.log('📍 Loading dashboard data for location:', locationId);
    setLoading(true);
    setError(null);

    try {
      const [healthRes, riskRes, forecastRes] = await Promise.allSettled([
        getLatestHealth(locationId),
        getLatestRisk(locationId),
        getClimateForecast(locationId, 7),
      ]);

      // Process Health
      if (healthRes.status === 'fulfilled' && healthRes.value) {
        const normalizedHealth = normalizeResponse(healthRes.value);
        if (normalizedHealth) {
          console.log('✅ Health data loaded:', normalizedHealth);
          setHealth(normalizedHealth);
        }
      } else {
        console.warn('⚠️ Health data unavailable:', healthRes.reason);
      }

      // Process Risk
      if (riskRes.status === 'fulfilled' && riskRes.value) {
        const normalizedRisk = normalizeResponse(riskRes.value);
        if (normalizedRisk) {
          console.log('✅ Risk data loaded:', normalizedRisk);
          setRisk(normalizedRisk);
        }
      } else {
        console.warn('⚠️ Risk data unavailable:', riskRes.reason);
      }

      // Process Forecast
      if (forecastRes.status === 'fulfilled' && forecastRes.value) {
        let normalizedForecast = normalizeResponse(forecastRes.value);
        
        // Ensure it's always an array
        if (!Array.isArray(normalizedForecast)) {
          normalizedForecast = normalizedForecast ? [normalizedForecast] : [];
        }
        
        console.log('✅ Forecast data loaded:', normalizedForecast);
        setForecast(normalizedForecast);
      } else {
        console.warn('⚠️ Forecast data unavailable:', forecastRes.reason);
      }

    } catch (err) {
      console.error('❌ Dashboard data load failed:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [locationId, normalizeResponse]);

  // === LOAD INITIAL DATA ON LOCATION CHANGE ===
  useEffect(() => {
    if (locationId) {
      loadDashboardData();
    } else {
      setHealth(null);
      setRisk(null);
      setForecast([]);
      setLoading(false);
    }
  }, [locationId, loadDashboardData]);

  // === SYNC REALTIME DATA TO LOCAL STATE ===
  useEffect(() => {
    if (liveHealth && liveHealth.length > 0) {
      console.log('🔄 Updating health from realtime:', liveHealth[0]);
      setHealth(liveHealth[0]);
    }
  }, [liveHealth]);

  useEffect(() => {
    if (liveRisk && liveRisk.length > 0) {
      console.log('🔄 Updating risk from realtime:', liveRisk[0]);
      setRisk(liveRisk[0]);
    }
  }, [liveRisk]);

  useEffect(() => {
    if (liveForecast && liveForecast.length > 0) {
      console.log('🔄 Updating forecast from realtime:', liveForecast);
      setForecast(liveForecast);
    }
  }, [liveForecast]);

  // === HELPER FUNCTIONS ===
  const getRiskColor = (level) => {
    const colors = {
      low: '#4caf50',
      moderate: '#ff9800',
      high: '#f44336',
      critical: '#d32f2f',
    };
    return colors[level?.toLowerCase?.()] || '#999';
  };

  const connectedAll = healthConnected && riskConnected && forecastConnected;

  // === LOADING STATE ===
  if (loading && !health && !risk && !forecast?.length) {
    return (
      <div style={{ 
        padding: '40px', 
        textAlign: 'center',
        fontSize: '18px',
        color: '#666'
      }}>
        <div>Loading dashboard data...</div>
        {locationId && (
          <div style={{ fontSize: '14px', marginTop: '10px', color: '#999' }}>
            Location ID: {locationId}
          </div>
        )}
      </div>
    );
  }

  // === NO LOCATION SELECTED ===
  if (!locationId) {
    return (
      <div style={{ 
        padding: '40px', 
        textAlign: 'center',
        fontSize: '18px',
        color: '#666'
      }}>
        <MapPin size={48} style={{ color: '#ccc', marginBottom: '20px' }} />
        <div>Please select a location to view dashboard</div>
      </div>
    );
  }

  // === ERROR STATE ===
  if (error) {
    return (
      <div style={{ 
        padding: '40px', 
        textAlign: 'center',
        fontSize: '16px',
        color: '#f44336'
      }}>
        <AlertCircle size={48} style={{ marginBottom: '20px' }} />
        <div>Error loading dashboard: {error}</div>
        <button 
          onClick={loadDashboardData}
          style={{
            marginTop: '20px',
            padding: '10px 20px',
            background: '#2c5f2d',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* === REALTIME CONNECTION STATUS === */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '8px' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '6px 12px',
            borderRadius: 999,
            background: connectedAll ? '#e6ffed' : '#f3f4f6',
            color: connectedAll ? '#065f46' : '#6b7280',
            fontSize: 13,
            fontWeight: 500,
          }}
        >
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: 999,
              background: connectedAll ? '#16a34a' : '#9ca3af',
              animation: connectedAll ? 'pulse 2s infinite' : 'none',
            }}
          />
          {connectedAll ? '🟢 Live' : '⚪ Offline'}
        </div>
      </div>

      {/* === ALERTS === */}
      <div style={{ marginBottom: '20px' }}>
        <RealtimeAlerts locationId={locationId} />
      </div>

      {/* === HEADER === */}
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ 
          fontSize: '32px', 
          color: '#2c5f2d', 
          marginBottom: '10px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <MapPin size={32} />
          {locationName || 'Dashboard'}
        </h1>
      </div>

      {/* === REALTIME WEATHER === */}
      <div style={{ marginBottom: '30px' }}>
        <RealtimeWeatherWidget locationId={locationId} />
      </div>

      {/* === METRICS GRID === */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px',
          marginBottom: '30px',
        }}
      >
        {/* DEGRADATION RISK */}
        <div
          style={{
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            borderLeft: `4px solid ${getRiskColor(risk?.risk_level)}`,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
            <AlertCircle size={24} color={getRiskColor(risk?.risk_level)} />
            <h3 style={{ marginLeft: '10px', fontSize: '16px', color: '#666' }}>
              Degradation Risk
            </h3>
          </div>
          <div
            style={{
              fontSize: '36px',
              fontWeight: 'bold',
              color: getRiskColor(risk?.risk_level),
            }}
          >
            {risk?.risk_score !== undefined && risk?.risk_score !== null 
              ? Number(risk.risk_score).toFixed(2)
              : 'N/A'}
          </div>
          <div style={{ fontSize: '14px', color: '#666', textTransform: 'uppercase' }}>
            {risk?.risk_level || 'Unknown'} Risk
          </div>
        </div>

        {/* VEGETATION INDEX (NDVI) */}
        <div
          style={{
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            borderLeft: '4px solid #4caf50',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
            <Leaf size={24} color="#4caf50" />
            <h3 style={{ marginLeft: '10px', fontSize: '16px', color: '#666' }}>
              Vegetation Index
            </h3>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#2c5f2d' }}>
            {health?.ndvi !== undefined && health?.ndvi !== null
              ? Number(health.ndvi).toFixed(3)
              : 'N/A'}
          </div>
          <div style={{ fontSize: '14px', color: '#666' }}>NDVI Score</div>
        </div>

        {/* VEGETATION COVER */}
        <div
          style={{
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            borderLeft: '4px solid #8bc34a',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
            <TrendingUp size={24} color="#8bc34a" />
            <h3 style={{ marginLeft: '10px', fontSize: '16px', color: '#666' }}>
              Vegetation Cover
            </h3>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#2c5f2d' }}>
            {health?.vegetation_cover_pct !== undefined && health?.vegetation_cover_pct !== null
              ? Number(health.vegetation_cover_pct).toFixed(1)
              : health?.vegetation_cover !== undefined && health?.vegetation_cover !== null
              ? Number(health.vegetation_cover).toFixed(1)
              : 'N/A'}%
          </div>
          <div style={{ fontSize: '14px', color: '#666' }}>Ground Coverage</div>
        </div>

        {/* WEATHER FORECAST */}
        <div
          style={{
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            borderLeft: '4px solid #2196f3',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
            <Cloud size={24} color="#2196f3" />
            <h3 style={{ marginLeft: '10px', fontSize: '16px', color: '#666' }}>
              Weather Forecast
            </h3>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#2196f3' }}>
            {forecast && forecast[0]?.temperature !== undefined && forecast[0]?.temperature !== null
              ? `${Number(forecast[0].temperature).toFixed(1)}°C`
              : 'N/A'}
          </div>
          <div style={{ fontSize: '14px', color: '#666' }}>
            {forecast && forecast[0] ? "Today's Temperature" : 'No forecast data'}
          </div>
        </div>
      </div>

      {/* === CHARTS === */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
          gap: '20px',
          marginBottom: '30px',
        }}
      >
        <ClimateChart forecast={forecast} locationId={locationId} />
        <RiskChart trend={undefined} locationId={locationId} />
      </div>

      {/* === RECOMMENDATIONS === */}
      <RecommendationsList locationId={locationId} />
    </div>
  );
};

export default Dashboard;