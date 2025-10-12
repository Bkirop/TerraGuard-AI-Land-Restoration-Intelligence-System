// src/supabaseClient.js
// Supabase client configuration for React App

import { createClient } from '@supabase/supabase-js'

// For Create React App, use process.env with REACT_APP_ prefix
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseserviceKey = process.env.REACT_APP_SUPABASE_SERVICE_KEY

// Validate environment variables
if (!supabaseUrl || !supabaseserviceKey) {
  console.error('Missing Supabase environment variables!')
  console.error('Make sure you have REACT_APP_SUPABASE_URL and REACT_APP_SUPABASE_SERVICE_KEY in your .env file')
}

// Create and export Supabase client
export const supabase = createClient(supabaseUrl, supabaseserviceKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

// Optional: Export helper functions for common operations
export const fetchLocations = async () => {
  const { data, error } = await supabase
    .from('locations')
    .select('*')
    .order('name')
  
  if (error) {
    console.error('Error fetching locations:', error)
    return { data: null, error }
  }
  
  return { data, error: null }
}

export const fetchClimateData = async (locationId = null) => {
  let query = supabase
    .from('climate_data')
    .select('*')
    .order('date', { ascending: false })
  
  if (locationId) {
    query = query.eq('location_id', locationId)
  }
  
  const { data, error } = await query
  
  if (error) {
    console.error('Error fetching climate data:', error)
    return { data: null, error }
  }
  
  return { data, error: null }
}

export const fetchLandHealth = async (locationId = null) => {
  let query = supabase
    .from('land_health')
    .select('*')
    .order('observation_date', { ascending: false })
  
  if (locationId) {
    query = query.eq('location_id', locationId)
  }
  
  const { data, error } = await query
  
  if (error) {
    console.error('Error fetching land health:', error)
    return { data: null, error }
  }
  
  return { data, error: null }
}

export const fetchDegradationRisk = async (locationId = null) => {
  let query = supabase
    .from('degradation_risk')
    .select('*')
    .order('assessment_date', { ascending: false })
  
  if (locationId) {
    query = query.eq('location_id', locationId)
  }
  
  const { data, error } = await query
  
  if (error) {
    console.error('Error fetching degradation risk:', error)
    return { data: null, error }
  }
  
  return { data, error: null }
}

export const fetchRecommendations = async (locationId = null, status = null) => {
  let query = supabase
    .from('recommendations')
    .select('*')
    .order('priority', { ascending: false })
  
  if (locationId) {
    query = query.eq('location_id', locationId)
  }
  
  if (status) {
    query = query.eq('status', status)
  }
  
  const { data, error } = await query
  
  if (error) {
    console.error('Error fetching recommendations:', error)
    return { data: null, error }
  }
  
  return { data, error: null }
}

// Helper function to fetch location with all related data
export const fetchLocationWithData = async (locationId) => {
  try {
    // Fetch location
    const { data: location, error: locationError } = await supabase
      .from('locations')
      .select('*')
      .eq('id', locationId)
      .single()
    
    if (locationError) throw locationError
    
    // Fetch related data in parallel
    const [climate, landHealth, risk, recommendations] = await Promise.all([
      fetchClimateData(locationId),
      fetchLandHealth(locationId),
      fetchDegradationRisk(locationId),
      fetchRecommendations(locationId)
    ])
    
    return {
      location,
      climateData: climate.data || [],
      landHealth: landHealth.data || [],
      degradationRisk: risk.data || [],
      recommendations: recommendations.data || [],
      error: null
    }
  } catch (error) {
    console.error('Error fetching location with data:', error)
    return { location: null, error }
  }
}

// Helper function to get dashboard summary
export const fetchDashboardSummary = async () => {
  try {
    const [locations, climateData, landHealth, risks, recommendations] = await Promise.all([
      supabase.from('locations').select('*', { count: 'exact' }),
      supabase.from('climate_data').select('*', { count: 'exact' }),
      supabase.from('land_health').select('*', { count: 'exact' }),
      supabase.from('degradation_risk').select('*').order('total_risk_score', { ascending: false }).limit(10),
      supabase.from('recommendations').select('*').eq('status', 'pending')
    ])
    
    return {
      totalLocations: locations.count || 0,
      totalClimateRecords: climateData.count || 0,
      totalLandHealthRecords: landHealth.count || 0,
      highRiskAreas: risks.data || [],
      pendingRecommendations: recommendations.data || [],
      error: null
    }
  } catch (error) {
    console.error('Error fetching dashboard summary:', error)
    return { error }
  }
}