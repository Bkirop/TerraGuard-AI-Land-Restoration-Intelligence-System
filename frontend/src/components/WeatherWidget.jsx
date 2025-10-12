import React, { useState, useEffect } from 'react';
import { Cloud, Droplets, Wind, Thermometer } from 'lucide-react';
import axios from 'axios';

const WeatherWidget = ({ locationId }) => {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (locationId) {
      fetchWeather();
      // Refresh every 15 minutes
      const interval = setInterval(fetchWeather, 900000);
      return () => clearInterval(interval);
    }
  }, [locationId]);

  const fetchWeather = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/climate/${locationId}/current-weather`
      );
      setWeather(response.data.weather);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch weather:', error);
      setLoading(false);
    }
  };

  if (loading) return <div>Loading weather...</div>;
  if (!weather) return null;

  return (
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      padding: '20px',
      borderRadius: '12px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: '48px', fontWeight: 'bold' }}>
            {weather.temperature}°C
          </div>
          <div style={{ fontSize: '16px', opacity: 0.9 }}>
            {weather.description}
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
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{weather.humidity}%</div>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Wind size={20} />
          <div>
            <div style={{ fontSize: '12px', opacity: 0.8 }}>Wind</div>
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{weather.wind_speed} m/s</div>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Thermometer size={20} />
          <div>
            <div style={{ fontSize: '12px', opacity: 0.8 }}>Feels Like</div>
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{weather.temp_max}°C</div>
          </div>
        </div>
      </div>

      <div style={{ 
        marginTop: '15px', 
        fontSize: '12px', 
        opacity: 0.7,
        textAlign: 'center'
      }}>
        Updated: {new Date(weather.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
};

export default WeatherWidget;