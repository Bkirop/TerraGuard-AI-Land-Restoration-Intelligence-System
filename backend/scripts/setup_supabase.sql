-- =========================================================
-- 🌍 TerraGuardAI Database Schema (UUID + Timestamp version)
-- =========================================================
-- Designed for Supabase / PostgreSQL
-- Run this in your Supabase SQL Editor
-- =========================================================

-- Enable UUID & crypto extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- =========================================================
-- USERS
-- =========================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- =========================================================
-- LOCATIONS
-- =========================================================
CREATE TABLE IF NOT EXISTS locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    country TEXT NOT NULL,
    region TEXT,
    geom GEOGRAPHY(Point, 4326) GENERATED ALWAYS AS (
        ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    ) STORED,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- CLIMATE DATA
-- =========================================================
CREATE TABLE IF NOT EXISTS climate_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    temperature DOUBLE PRECISION NOT NULL,
    precipitation DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL,
    wind_speed DOUBLE PRECISION,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- LAND HEALTH
-- =========================================================
CREATE TABLE IF NOT EXISTS land_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    soil_moisture DOUBLE PRECISION NOT NULL,
    vegetation_index DOUBLE PRECISION NOT NULL,
    soil_ph DOUBLE PRECISION,
    erosion_risk DOUBLE PRECISION NOT NULL,
    overall_health_score DOUBLE PRECISION NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- PREDICTIONS
-- =========================================================
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    target_date DATE NOT NULL,
    prediction_type TEXT NOT NULL,
    predicted_value DOUBLE PRECISION NOT NULL,
    confidence_score DOUBLE PRECISION NOT NULL,
    model_version TEXT,
    prediction_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- DEGRADATION RISK
-- =========================================================
CREATE TABLE IF NOT EXISTS degradation_risk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    risk_level DOUBLE PRECISION NOT NULL,
    risk_status TEXT NOT NULL,
    factors TEXT,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- RISK ASSESSMENTS
-- =========================================================
CREATE TABLE IF NOT EXISTS risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    risk_level DOUBLE PRECISION NOT NULL,
    risk_status TEXT NOT NULL,
    factors TEXT,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================================
-- RECOMMENDATIONS
-- =========================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT DEFAULT 'medium',
    action TEXT,
    expected_impact TEXT,
    category TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- =========================================================
-- ALERTS
-- =========================================================
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    severity TEXT DEFAULT 'medium',
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- =========================================================
-- 🔧 TRIGGERS (Auto-update timestamps)
-- =========================================================
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_locations
BEFORE UPDATE ON locations
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- =========================================================
-- 📊 HELPER VIEWS
-- =========================================================

-- View: average climate per location
CREATE OR REPLACE VIEW v_avg_climate AS
SELECT 
    l.id AS location_id,
    l.name AS location_name,
    AVG(c.temperature) AS avg_temperature,
    AVG(c.precipitation) AS avg_precipitation,
    AVG(c.humidity) AS avg_humidity
FROM locations l
LEFT JOIN climate_data c ON c.location_id = l.id
GROUP BY l.id, l.name;

-- View: latest land health snapshot
CREATE OR REPLACE VIEW v_latest_land_health AS
SELECT DISTINCT ON (location_id)
    location_id,
    soil_moisture,
    vegetation_index,
    soil_ph,
    erosion_risk,
    overall_health_score,
    date
FROM land_health
ORDER BY location_id, date DESC;

-- View: active alerts per location
CREATE OR REPLACE VIEW v_active_alerts AS
SELECT 
    l.name AS location_name,
    a.title,
    a.severity,
    a.created_at
FROM alerts a
JOIN locations l ON l.id = a.location_id
WHERE a.is_resolved = FALSE;

-- =========================================================
-- ✅ END OF SCHEMA
-- =========================================================
