import React, { useEffect, useState } from 'react';
import { getRiskTrend } from '../services/api';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const RiskChart = ({ locationId }) => {
  const [riskData, setRiskData] = useState([]);

  useEffect(() => {
    const loadRiskData = async () => {
      if (!locationId) return;
      try {
        const response = await getRiskTrend(locationId);
        const data = response.data?.data ?? response.data ?? [];
        console.log('📊 Risk trend data:', data);
        setRiskData(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Failed to load risk trend:', err);
      }
    };
    loadRiskData();
  }, [locationId]);

  if (!riskData.length) {
    return <p style={{ textAlign: 'center', color: '#666' }}>No risk trend data available</p>;
  }

  return (
    <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
      <h3 style={{ marginBottom: '10px', color: '#333' }}>Degradation Risk Trend</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={riskData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="risk_score" stroke="#f44336" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RiskChart;
