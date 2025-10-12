import React, { useEffect } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import { useSupabaseRealtime } from '../hooks/useSupabaseRealtime';

const RealtimeAlerts = ({ locationId }) => {
  const { data: alerts, connected } = useSupabaseRealtime('alerts', {
    filter: { location_id: locationId },
    orderBy: { column: 'alert_date', ascending: false },
    limit: 5
  });

  // Show browser notification for new alerts
  useEffect(() => {
    if (alerts.length > 0 && connected && Notification.permission === 'granted') {
      const latestAlert = alerts[0];
      new Notification('TerraGuard Alert', {
        body: latestAlert.message,
        icon: '/favicon.ico'
      });
    }
  }, [alerts, connected]);

  const getSeverityColor = (severity) => {
    const colors = {
      INFO: '#2196f3',
      WARNING: '#ff9800',
      CRITICAL: '#f44336'
    };
    return colors[severity] || '#999';
  };

  if (!alerts || alerts.length === 0) {
    return null;
  }

  return (
    <div style={{ marginBottom: '20px' }}>
      {alerts.map((alert) => (
        <div
          key={alert.id}
          style={{
            background: 'white',
            padding: '15px',
            borderRadius: '8px',
            marginBottom: '10px',
            borderLeft: `4px solid ${getSeverityColor(alert.severity)}`,
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '15px'
          }}
        >
          <AlertTriangle size={24} color={getSeverityColor(alert.severity)} />
          <div style={{ flex: 1 }}>
            <div style={{ 
              fontWeight: 'bold', 
              marginBottom: '5px',
              color: getSeverityColor(alert.severity)
            }}>
              {alert.title}
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              {alert.message}
            </div>
            <div style={{ fontSize: '12px', color: '#999', marginTop: '5px' }}>
              {new Date(alert.alert_date).toLocaleString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default RealtimeAlerts;