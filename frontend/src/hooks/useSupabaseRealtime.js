import { useEffect, useState, useRef } from 'react';
import { supabase } from '../services/supabase';

// Map view names to actual table names for realtime
const TABLE_MAPPING = {
  'health': 'land_health',
  'risk': 'degradation_risk',
  'climate_forecast': 'climate_data',
  'weather_realtime': 'climate_data',
  'alerts': 'alerts',
  'recommendations': 'recommendations'
};

// Transform data from base table to view format
const transformData = (tableName, data) => {
  if (!data) return data;
  
  if (tableName === 'land_health') {
    return {
      ...data,
      created_at: data.observation_date || data.created_at,
      updated_at: data.observation_date || data.updated_at,
    };
  }
  
  if (tableName === 'degradation_risk') {
    return {
      ...data,
      risk_score: data.total_risk_score,
      factors: data.risk_factors,
      created_at: data.assessment_date || data.created_at,
      updated_at: data.assessment_date || data.updated_at,
    };
  }
  
  if (tableName === 'climate_data') {
    return {
      ...data,
      timestamp: data.date,
      temperature: data.temperature || data.temp_avg,
    };
  }
  
  return data;
};

export function useSupabaseRealtime(viewName, options = {}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const channelRef = useRef(null);
  const retryTimeout = useRef(null);

  // Get actual table name for realtime
  const actualTable = TABLE_MAPPING[viewName] || viewName;
  
  // Stabilize options to prevent infinite loops
  const stableFilter = JSON.stringify(options.filter || {});
  const stableOrderBy = JSON.stringify(options.orderBy || {});
  const stableLimit = options.limit;

  useEffect(() => {
    const parsedFilter = JSON.parse(stableFilter);
    const parsedOrderBy = JSON.parse(stableOrderBy);

    const setup = async () => {
      try {
        console.log(`📊 Setting up realtime for: ${viewName} (base table: ${actualTable})`);
        
        // === FETCH INITIAL DATA FROM VIEW ===
        let query = supabase.from(viewName).select('*');
        
        // Apply filters
        if (parsedFilter && Object.keys(parsedFilter).length > 0) {
          for (const [key, value] of Object.entries(parsedFilter)) {
            query = query.eq(key, value);
          }
        }
        
        // Apply ordering
        if (parsedOrderBy && parsedOrderBy.column) {
          query = query.order(parsedOrderBy.column, { 
            ascending: parsedOrderBy.ascending ?? false 
          });
        }
        
        // Apply limit
        if (stableLimit) {
          query = query.limit(stableLimit);
        }

        const { data: initial, error } = await query;
        
        if (error) {
          console.error(`❌ Error fetching ${viewName}:`, error);
          throw error;
        }
        
        console.log(`✅ Initial ${viewName} data:`, initial);
        setData(initial || []);
        setLoading(false);

        // === SETUP REALTIME SUBSCRIPTION ON BASE TABLE ===
        if (channelRef.current) {
          await supabase.removeChannel(channelRef.current);
          channelRef.current = null;
        }

        const channelName = `realtime_${actualTable}_${Date.now()}`;
        
        // Build filter string for Supabase realtime
        let filterString = undefined;
        if (parsedFilter && Object.keys(parsedFilter).length > 0) {
          const firstKey = Object.keys(parsedFilter)[0];
          const firstValue = parsedFilter[firstKey];
          filterString = `${firstKey}=eq.${firstValue}`;
        }

        const channel = supabase
          .channel(channelName)
          .on(
            'postgres_changes',
            {
              event: '*',
              schema: 'public',
              table: actualTable,
              filter: filterString,
            },
            async (payload) => {
              console.log(`🔥 ${viewName} realtime update:`, payload);
              
              // Transform the payload data to match view format
              const transformedNew = payload.new ? transformData(actualTable, payload.new) : null;
              const transformedOld = payload.old ? transformData(actualTable, payload.old) : null;
              
              setData((prev) => {
                let updated = [...prev];
                
                if (payload.eventType === 'INSERT' && transformedNew) {
                  updated = [transformedNew, ...updated];
                  if (stableLimit) {
                    updated = updated.slice(0, stableLimit);
                  }
                } else if (payload.eventType === 'UPDATE' && transformedNew) {
                  updated = updated.map((record) =>
                    record.id === transformedNew.id ? transformedNew : record
                  );
                } else if (payload.eventType === 'DELETE' && transformedOld) {
                  updated = updated.filter((record) => record.id !== transformedOld.id);
                }
                
                // Re-sort if orderBy is specified
                if (parsedOrderBy && parsedOrderBy.column) {
                  updated.sort((a, b) => {
                    const aVal = a[parsedOrderBy.column];
                    const bVal = b[parsedOrderBy.column];
                    const compare = aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
                    return parsedOrderBy.ascending ? compare : -compare;
                  });
                }
                
                return updated;
              });
            }
          )
          .subscribe((status) => {
            console.log(`📡 ${viewName} subscription status:`, status);
            
            if (status === 'SUBSCRIBED') {
              setConnected(true);
              if (retryTimeout.current) {
                clearTimeout(retryTimeout.current);
                retryTimeout.current = null;
              }
            } else if (status === 'CLOSED' || status === 'CHANNEL_ERROR') {
              setConnected(false);
              
              if (!retryTimeout.current) {
                retryTimeout.current = setTimeout(() => {
                  console.warn(`🔁 Retrying ${viewName} connection...`);
                  retryTimeout.current = null;
                  setup();
                }, 5000);
              }
            } else if (status === 'TIMED_OUT') {
              setConnected(false);
              console.error(`⏱️ ${viewName} subscription timed out`);
            }
          });

        channelRef.current = channel;

      } catch (err) {
        console.error(`❌ ${viewName} realtime setup failed:`, err);
        setLoading(false);
        setConnected(false);
      }
    };

    setup();

    return () => {
      console.log(`🧹 Cleaning up ${viewName} subscription`);
      
      if (channelRef.current) {
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
      
      if (retryTimeout.current) {
        clearTimeout(retryTimeout.current);
        retryTimeout.current = null;
      }
    };
  }, [viewName, actualTable, stableFilter, stableOrderBy, stableLimit]);

  return { data, loading, connected };
}