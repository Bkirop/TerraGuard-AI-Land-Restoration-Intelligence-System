import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Sparkles, AlertCircle, CheckCircle, RefreshCw, Clock } from 'lucide-react';
import { getRecommendations, generateRecommendations } from '../services/api';
import { useSupabaseRealtime } from '../hooks/useSupabaseRealtime';

const RecommendationsList = ({ locationId }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  // === REALTIME SUBSCRIPTION OPTIONS ===
  const recsOpts = useMemo(
    () => ({
      filter: locationId ? { location_id: locationId } : {},
      orderBy: { column: 'created_at', ascending: false },
      limit: 10,
    }),
    [locationId]
  );

  // === REALTIME SUBSCRIPTION ===
  const { 
    data: liveRecs, 
    loading: recsLoading, 
    connected: recsConnected 
  } = useSupabaseRealtime('recommendations', recsOpts);

  // === NORMALIZE RESPONSE DATA ===
  const normalizeRecommendations = useCallback((response) => {
    console.log('📦 Raw recommendations response:', response);
    
    // Handle different response structures
    let recs = 
      response?.data?.data ||           // {data: {data: [...]}}
      response?.data?.recommendations || // {data: {recommendations: [...]}}
      response?.data ||                  // {data: [...]}
      response?.recommendations ||       // {recommendations: [...]}
      response ||                        // [...]
      [];

    // Ensure it's an array
    const recsArray = Array.isArray(recs) ? recs : (recs ? [recs] : []);
    
    console.log('✅ Normalized recommendations:', recsArray.length, 'items');
    if (recsArray.length > 0) {
      console.log('Sample recommendation fields:', Object.keys(recsArray[0]));
    }
    return recsArray;
  }, []);

  // === LOAD RECOMMENDATIONS ===
  const loadRecommendations = useCallback(async () => {
    if (!locationId) {
      setRecommendations([]);
      setLoading(false);
      return;
    }

    console.log('📋 Loading recommendations for location:', locationId);
    setLoading(true);
    setError(null);

    try {
      const response = await getRecommendations(locationId);
      const recs = normalizeRecommendations(response);
      console.log('✅ Loaded', recs.length, 'recommendations');
      setRecommendations(recs);
    } catch (err) {
      console.error('❌ Failed to load recommendations:', err);
      setError(err.message);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  }, [locationId, normalizeRecommendations]);

  // === GENERATE NEW RECOMMENDATIONS ===
  const handleGenerate = async () => {
    if (!locationId || generating) return;

    console.log('🤖 Generating recommendations for location:', locationId);
    setGenerating(true);
    setError(null);

    try {
      const response = await generateRecommendations(locationId);
      console.log('✅ Generate response:', response);
      
      // Wait a moment for realtime to pick up the changes, or reload manually
      setTimeout(() => {
        loadRecommendations();
      }, 1000);
    } catch (err) {
      console.error('❌ Failed to generate recommendations:', err);
      setError(err.message);
      alert('Failed to generate recommendations. Check console for details.');
    } finally {
      setGenerating(false);
    }
  };

  // === LOAD ON MOUNT OR LOCATION CHANGE ===
  useEffect(() => {
    if (locationId) {
      loadRecommendations();
    } else {
      setRecommendations([]);
      setLoading(false);
    }
  }, [locationId, loadRecommendations]);

  // === SYNC REALTIME DATA ===
  useEffect(() => {
    if (liveRecs && Array.isArray(liveRecs)) {
      console.log('🔄 Updating recommendations from realtime:', liveRecs.length, 'items');
      if (liveRecs.length > 0) {
        console.log('Realtime recommendation sample:', liveRecs[0]);
      }
      setRecommendations(liveRecs);
    }
  }, [liveRecs]);

  // === HELPER FUNCTIONS ===
  const getPriorityColor = (priority) => {
    const p = (priority || 'medium').toLowerCase();
    const colors = {
      high: '#f44336',
      critical: '#d32f2f',
      medium: '#ff9800',
      moderate: '#ff9800',
      low: '#4caf50',
      info: '#2196f3'
    };
    return colors[p] || '#999';
  };

  const getPriorityIcon = (priority) => {
    const p = (priority || 'medium').toLowerCase();
    if (p === 'high' || p === 'critical') return <AlertCircle size={20} />;
    if (p === 'low') return <CheckCircle size={20} />;
    return <AlertCircle size={20} />;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return dateStr;
    }
  };

  // === LOADING STATE ===
  if (loading && recommendations.length === 0) {
    return (
      <div
        style={{
          background: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          textAlign: 'center',
          color: '#666'
        }}
      >
        <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite', margin: '0 auto' }} />
        <p style={{ marginTop: '10px' }}>Loading recommendations...</p>
      </div>
    );
  }

  // === ERROR STATE ===
  if (error && recommendations.length === 0) {
    return (
      <div
        style={{
          background: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}
      >
        <AlertCircle size={32} color="#f44336" style={{ margin: '0 auto 10px' }} />
        <p style={{ color: '#f44336', marginBottom: '15px' }}>{error}</p>
        <button
          onClick={loadRecommendations}
          style={{
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
    <div
      style={{
        background: 'white',
        padding: '20px',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      {/* === HEADER === */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
        }}
      >
        <h2 style={{ fontSize: '20px', color: '#333', margin: 0 }}>
          AI Recommendations
        </h2>
        <button
          onClick={handleGenerate}
          disabled={generating || !locationId}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 20px',
            background: generating ? '#ccc' : '#2c5f2d',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: generating || !locationId ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            opacity: generating ? 0.6 : 1,
          }}
        >
          <Sparkles size={16} />
          {generating ? 'Generating...' : 'Generate New'}
        </button>
      </div>

      {/* === REALTIME STATUS === */}
      {recsConnected && (
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '4px 10px',
          background: '#e6ffed',
          color: '#065f46',
          borderRadius: 999,
          fontSize: 12,
          fontWeight: 500,
          marginBottom: 15
        }}>
          <div style={{
            width: 8,
            height: 8,
            borderRadius: 999,
            background: '#16a34a',
            animation: 'pulse 2s infinite'
          }} />
          Live Updates Active
        </div>
      )}

      {/* === RECOMMENDATIONS LIST === */}
      {recommendations.length === 0 ? (
        <div
          style={{
            textAlign: 'center',
            padding: '40px',
            color: '#666',
          }}
        >
          <Sparkles size={48} style={{ color: '#ddd', margin: '0 auto 15px' }} />
          <p style={{ fontSize: '16px', marginBottom: '10px' }}>
            No recommendations yet.
          </p>
          <p style={{ fontSize: '14px', color: '#999' }}>
            Click "Generate New" to get AI-powered recommendations based on current land conditions.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {recommendations.map((rec, index) => {
            // CRITICAL: Handle the actual field names from your backend
            const title = 
              rec.action_title ||           // ← YOUR BACKEND USES THIS
              rec.recommendation_text || 
              rec.recommendation || 
              rec.text || 
              rec.title ||
              'No title provided';
            
            const description = 
              rec.action_description ||     // ← YOUR BACKEND USES THIS
              rec.description || 
              rec.details ||
              '';
            
            const priority = rec.priority || 'medium';
            const category = rec.category || rec.type || 'General';
            const status = rec.status || 'pending';
            const urgencyHours = rec.urgency_hours;
            const riskReduction = rec.expected_risk_reduction;
            const startDate = rec.recommended_start_date;
            const endDate = rec.recommended_end_date;
            const createdAt = rec.created_at;

            return (
              <div
                key={rec.id || index}
                style={{
                  padding: '16px',
                  border: '1px solid #e0e0e0',
                  borderRadius: '8px',
                  borderLeft: `4px solid ${getPriorityColor(priority)}`,
                  background: '#fafafa',
                  transition: 'all 0.2s'
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px',
                  }}
                >
                  <div
                    style={{
                      color: getPriorityColor(priority),
                      marginTop: '2px',
                      flexShrink: 0
                    }}
                  >
                    {getPriorityIcon(priority)}
                  </div>
                  <div style={{ flex: 1 }}>
                    {/* Header Row */}
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '8px',
                      flexWrap: 'wrap',
                      gap: '8px'
                    }}>
                      <div
                        style={{
                          fontSize: '12px',
                          fontWeight: 'bold',
                          color: getPriorityColor(priority),
                          textTransform: 'uppercase',
                        }}
                      >
                        {priority} Priority
                      </div>
                      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                        {category && (
                          <span style={{
                            padding: '2px 8px',
                            background: 'white',
                            border: '1px solid #e0e0e0',
                            borderRadius: '4px',
                            fontSize: '11px',
                            color: '#666',
                            textTransform: 'capitalize'
                          }}>
                            {category}
                          </span>
                        )}
                        {status && (
                          <span style={{
                            padding: '2px 8px',
                            background: status === 'completed' ? '#e6ffed' : '#fff3cd',
                            border: `1px solid ${status === 'completed' ? '#16a34a' : '#ffc107'}`,
                            borderRadius: '4px',
                            fontSize: '11px',
                            color: status === 'completed' ? '#065f46' : '#856404',
                            textTransform: 'capitalize'
                          }}>
                            {status}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Title */}
                    <h4 style={{
                      fontSize: '16px',
                      color: '#1f2937',
                      fontWeight: '600',
                      margin: '0 0 8px 0',
                      lineHeight: '1.4'
                    }}>
                      {title}
                    </h4>

                    {/* Description */}
                    {description && (
                      <p
                        style={{
                          fontSize: '14px',
                          color: '#4b5563',
                          lineHeight: '1.6',
                          margin: '0 0 12px 0',
                        }}
                      >
                        {description}
                      </p>
                    )}

                    {/* Metadata Row */}
                    <div style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '12px',
                      fontSize: '12px',
                      color: '#6b7280',
                      marginTop: '12px',
                      paddingTop: '12px',
                      borderTop: '1px solid #e5e7eb'
                    }}>
                      {urgencyHours && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={14} />
                          <span>{urgencyHours}h urgency</span>
                        </div>
                      )}
                      {riskReduction !== null && riskReduction !== undefined && (
                        <div>
                          Risk reduction: <strong>{riskReduction.toFixed(1)}%</strong>
                        </div>
                      )}
                      {startDate && endDate && (
                        <div>
                          {formatDate(startDate)} → {formatDate(endDate)}
                        </div>
                      )}
                    </div>

                    {/* Created timestamp */}
                    {createdAt && (
                      <div style={{
                        fontSize: '11px',
                        color: '#9ca3af',
                        marginTop: '8px'
                      }}>
                        Created: {new Date(createdAt).toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default RecommendationsList;