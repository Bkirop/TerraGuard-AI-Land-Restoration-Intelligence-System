import React from 'react';
import { Cloud, Droplets, Wind, Thermometer, Wifi, WifiOff } from 'lucide-react';
import { useSupabaseRealtime } from '../hooks/useSupabaseRealtime';

const RealtimeWeatherWidget = ({ locationId }) => {
  const { data, loading, connected } = useSupabaseRealtime('climate_data', {
    filter: { location_id: locationId, is_forecast: false },
    orderBy: { column: 'date', ascending: false },
    limit: 1
  });

  const weather = data[0];

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading weather...</div>;
  }

  if (!weather) {
    return <div style={{ padding: '20px' }}>No weather data available</div>;
  }

  return (
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      padding: '20px',
      borderRadius: '12px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      position: 'relative'
    }}>
      {/* Real-time connection indicator */}
      <div style={{
        position: 'absolute',
        top: '15px',
        right: '15px',
        display: 'flex',
        alignItems: 'center',
        gap: '5px',
        fontSize: '12px',
        background: connected ? 'rgba(76, 175, 80, 0.3)' : 'rgba(244, 67, 54, 0.3)',
        padding: '5px 10px',
        borderRadius: '20px'
      }}>
        {connected ? <Wifi size={14} /> : <WifiOff size={14} />}
        {connected ? 'Live' : 'Offline'}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: '48px', fontWeight: 'bold' }}>
            {weather.temp_avg?.toFixed(1) || 'N/A'}°C
          </div>
          <div style={{ fontSize: '16px', opacity: 0.9 }}>
            Current Weather
          </div>
        </div>
        <Cloud size={64} style={{ opacity: 0.8 }} />
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: '15px',
        marginTop: '20px',
        paddingTop: '20px',
        borderTop: '1px solid rgba(255,255,255,0.3)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Droplets size={20} />
          <div>
            <div style={{ fontSize: '12px', opacity: 0.8 }}>Humidity</div>
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
              {weather.humidity || 'N/A'}%
            </div>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Wind size={20} />
          <div>
            <div style={{ fontSize: '12px', opacity: 0.8 }}>Wind</div>
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
              {weather.wind_speed?.toFixed(1) || 'N/A'} m/s
            </div>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Thermometer size={20} />
          <div>
            <div style={{ fontSize: '12px', opacity: 0.8 }}>High</div>
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
              {weather.temp_max?.toFixed(1) || 'N/A'}°C
            </div>
          </div>
        </div>
      </div>

      <div style={{ 
        marginTop: '15px', 
        fontSize: '12px', 
        opacity: 0.7,
        textAlign: 'center'
      }}>
        Updated: {new Date(weather.date).toLocaleDateString()}
      </div>
    </div>
  );
};

export default RealtimeWeatherWidget;