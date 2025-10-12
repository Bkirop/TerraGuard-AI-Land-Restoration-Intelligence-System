import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getClimateForecast } from '../services/api';

const ClimateChart = ({ locationId }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (locationId) {
      loadClimateData();
    }
  }, [locationId]);

  const loadClimateData = async () => {
    try {
      const response = await getClimateForecast(locationId, 7);
      setData(response.data.data);
    } catch (error) {
      console.error('Failed to load climate data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading climate data...</div>;
  }

  return (
    <div style={{
      background: 'white',
      padding: '20px',
      borderRadius: '12px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    }}>
      <h2 style={{ marginBottom: '20px', fontSize: '20px', color: '#333' }}>
        7-Day Weather Forecast
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="temperature"
            stroke="#ff5722"
            strokeWidth={2}
            name="Temperature (°C)"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="precipitation"
            stroke="#2196f3"
            strokeWidth={2}
            name="Precipitation (mm)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ClimateChart;