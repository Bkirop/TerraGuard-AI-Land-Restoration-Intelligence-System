# seed_full.py
import os
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone
import random
import time

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise Exception("Supabase URL or Key not found. Check your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
print("✅ Successfully connected to Supabase!")

# ---------- Helpers ----------
def now_iso():
    return datetime.now(timezone.utc).isoformat()

def try_table_insert(table_name, rows):
    """Try inserting into a table and return result or raise exception"""
    try:
        res = supabase.table(table_name).insert(rows).execute()
        # supabase returns .data in older client versions; handle missing gracefully
        data = getattr(res, "data", None) or res
        print(f"✓ Inserted {len(rows)} rows into `{table_name}`")
        return data
    except Exception as e:
        print(f"✖ Failed to insert into `{table_name}`: {e}")
        raise

# ---------- 1) Seed users ----------
def seed_users():
    print("Seeding users...")
    users = [
        {
            "id": str(uuid.uuid4()),
            "username": "admin_user",
            "email": "admin@example.com",
            "full_name": "Admin User",
            "is_active": True,
            "is_admin": True,
            "created_at": now_iso()
        },
        {
            "id": str(uuid.uuid4()),
            "username": "field_agent",
            "email": "agent@example.com",
            "full_name": "Field Agent",
            "is_active": True,
            "is_admin": False,
            "created_at": now_iso()
        },
        {
            "id": str(uuid.uuid4()),
            "username": "researcher",
            "email": "researcher@example.com",
            "full_name": "Data Researcher",
            "is_active": True,
            "is_admin": False,
            "created_at": now_iso()
        },
    ]

    return try_table_insert("users", users)

# ---------- 2) Seed locations ----------
def seed_locations():
    print("Seeding locations...")
    locations = [
        {
            "id": str(uuid.uuid4()),
            "name": "Lake Naivasha",
            "latitude": -0.716,
            "longitude": 36.430,
            "country": "Kenya",
            "region": "Nakuru County",
            "created_at": now_iso(),
            "updated_at": now_iso()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mara Conservancy",
            "latitude": -1.492,
            "longitude": 35.146,
            "country": "Kenya",
            "region": "Narok County",
            "created_at": now_iso(),
            "updated_at": now_iso()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Tsavo East",
            "latitude": -3.215,
            "longitude": 38.770,
            "country": "Kenya",
            "region": "Taita-Taveta",
            "created_at": now_iso(),
            "updated_at": now_iso()
        },
    ]

    return try_table_insert("locations", locations)

# ---------- 3) Seed climate_data ----------
def seed_climate_data(locations):
    print("Seeding climate_data...")
    rows = []
    today = datetime.now(timezone.utc).date()
    for i, loc in enumerate(locations):
        rows.append({
            "id": str(uuid.uuid4()),
            "location_id": loc["id"],
            "date": str(today - timedelta(days=(i+1))),
            "temp_avg": round(22.0 + random.uniform(-3, 3), 2),
            "temp_max": round(28.0 + random.uniform(-3, 3), 2),
            "temp_min": round(16.0 + random.uniform(-3, 3), 2),
            "precipitation": round(random.uniform(0, 150), 2),
            "humidity": round(50 + random.uniform(-15, 15), 2),
            "wind_speed": round(random.uniform(0.5, 8.0), 2),
            "solar_radiation": round(random.uniform(150, 350), 2),
            "evapotranspiration": round(random.uniform(1.0, 6.0), 2),
            "source": "demo_seed",
            "is_forecast": False,
            "created_at": now_iso()
        })
    return try_table_insert("climate_data", rows)

# ---------- 4) Seed land_health ----------
def seed_land_health(locations):
    print("Seeding land_health...")
    rows = []
    today = datetime.now(timezone.utc).date()
    for i, loc in enumerate(locations):
        rows.append({
            "id": str(uuid.uuid4()),
            "location_id": loc["id"],
            "observation_date": str(today - timedelta(days=(i+2))),
            "ndvi": round(0.35 + random.uniform(-0.1, 0.3), 3),
            "evi": round(0.30 + random.uniform(-0.1, 0.3), 3),
            "soil_moisture": round(20 + random.uniform(5, 40), 2),
            "soil_temperature": round(18 + random.uniform(-3, 6), 2),
            "vegetation_cover_pct": round(30 + random.uniform(10, 50), 2),
            "bare_soil_pct": round(10 + random.uniform(0, 30), 2),
            "erosion_risk_score": round(random.uniform(10, 80), 2),
            "drought_stress_score": round(random.uniform(10, 80), 2),
            "satellite_source": random.choice(["sentinel2", "landsat8", "modis"]),
            "created_at": now_iso()
        })
    return try_table_insert("land_health", rows)

# ---------- 5) Seed predictions (fallback to prediction_logs) ----------
def seed_predictions(locations):
    print("Seeding predictions...")
    rows = []
    for i, loc in enumerate(locations):
        rows.append({
            "id": str(uuid.uuid4()),
            "location_id": loc["id"],
            "prediction_date": now_iso(),
            "target_date": (datetime.now(timezone.utc) + timedelta(days=7)).date().isoformat(),
            "prediction_type": "temperature_forecast",
            "predicted_value": round(22 + random.uniform(-2, 5), 2),
            "confidence_score": round(random.uniform(0.6, 0.95), 3),
            "model_version": "v1.0.0",
            "created_at": now_iso()
        })

    # try canonical table name first
    try:
        return try_table_insert("predictions", rows)
    except Exception:
        print("Trying fallback table `prediction_logs`...")
        # adapt field names expected in prediction_logs if different
        fallback_rows = []
        for r in rows:
            fallback_rows.append({
                "id": r["id"],
                "location_id": r["location_id"],
                "prediction_type": r["prediction_type"],
                "model_name": "demo_model",
                "model_version": r["model_version"],
                "input_features": {"demo": True},
                "predictions": {"value": r["predicted_value"]},
                "confidence_score": r["confidence_score"],
                "prediction_date": r["prediction_date"],
                "target_date": r["target_date"]
            })
        return try_table_insert("prediction_logs", fallback_rows)

# ---------- 6) Seed degradation_risk (fallback to risk_assessments) ----------
def seed_degradation_risk(locations):
    print("Seeding degradation risk...")
    rows = []
    for i, loc in enumerate(locations):
        total_score = round(30 + random.uniform(-10, 50), 2)
        rows.append({
            "id": str(uuid.uuid4()),
            "location_id": loc["id"],
            "assessment_date": (datetime.now(timezone.utc) - timedelta(days=i)).date().isoformat(),
            "total_risk_score": total_score,
            "drought_risk": round(random.uniform(10, 80), 2),
            "erosion_risk": round(random.uniform(10, 80), 2),
            "soil_degradation_risk": round(random.uniform(10, 80), 2),
            "vegetation_loss_risk": round(random.uniform(10, 80), 2),
            "temperature_stress_risk": round(random.uniform(10, 80), 2),
            "water_scarcity_risk": round(random.uniform(10, 80), 2),
            "risk_factors": {"demo": "seed"},
            "forecast_horizon_days": 7,
            "created_at": now_iso()
        })

    try:
        return try_table_insert("degradation_risk", rows)
    except Exception:
        print("Trying fallback table `risk_assessments`...")
        # map columns to alternate schema
        fallback_rows = []
        for r in rows:
            fallback_rows.append({
                "id": r["id"],
                "location_id": r["location_id"],
                "date": r["assessment_date"],
                "category": "degradation",
                "risk_level": r["total_risk_score"],
                "risk_status": "HIGH" if r["total_risk_score"] > 60 else "MODERATE",
                "factors": '{"demo": "seed"}',
                "created_at": r["created_at"]
            })
        return try_table_insert("risk_assessments", fallback_rows)

# ---------- 7) Seed recommendations ----------
def seed_recommendations(locations, risk_rows):
    print("Seeding recommendations...")
    rows = []
    today = datetime.now(timezone.utc).date()
    # attempt to get risk ids to tie recommendations
    risk_ids = []
    if isinstance(risk_rows, list):
        for r in risk_rows:
            # r may be dict with 'id' or returned as rows, handle both
            if isinstance(r, dict) and "id" in r:
                risk_ids.append(r["id"])
            elif isinstance(r, list):
                # If nested results, flatten
                for rr in r:
                    if "id" in rr:
                        risk_ids.append(rr["id"])
    for i, loc in enumerate(locations):
        rows.append({
            "id": str(uuid.uuid4()),
            "location_id": loc["id"],
            "risk_assessment_id": risk_ids[i] if i < len(risk_ids) else None,
            "priority": "CRITICAL" if i % 2 == 0 else "HIGH",
            "category": "erosion_control",
            "action_title": f"Soil Conservation Plan {i+1}",
            "action_description": "Apply contour bunds and mulching to reduce erosion.",
            "recommended_start_date": str(today + timedelta(days=3)),
            "recommended_end_date": str(today + timedelta(days=60)),
            "urgency_hours": random.randint(48, 120),
            "expected_risk_reduction": round(random.uniform(10, 30), 2),
            "expected_cost_usd": round(random.uniform(2000, 8000), 2),
            "recommended_species": {"acacia": "preferred"},
            "status": "pending",
            "created_at": now_iso()
        })
    return try_table_insert("recommendations", rows)

# ---------- 8) Seed alerts ----------
def seed_alerts(locations):
    print("Seeding alerts...")
    rows = []
    today = datetime.now(timezone.utc).date()
    for i, loc in enumerate(locations):
        rows.append({
            "id": str(uuid.uuid4()),
            "location_id": loc["id"],
            "alert_type": "Climate Warning",
            "title": f"Extreme Weather Alert {i+1}",
            "message": "Heavy rainfall expected — prepare erosion controls.",
            "severity": "HIGH",
            "is_resolved": False,
            "alert_date": now_iso(),
            "event_date": str(today + timedelta(days=2)),
            "expiry_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "recommended_actions": {"action": "secure-soil"},
            "sent_sms": False,
            "sent_email": False,
            "created_at": now_iso()
        })
    return try_table_insert("alerts", rows)

# ---------- Verification ----------
def verify_data(tables):
    print("\nVerifying seeded data...")
    for table in tables:
        try:
            res = supabase.table(table).select("*", count="exact").limit(1).execute()
            cnt = getattr(res, "count", None)
            print(f"  {table}: count reported = {cnt}")
        except Exception as e:
            print(f"  {table}: could not verify (maybe missing) — {e}")

# ---------- Main ----------
def main():
    print("="*60)
    print("🚀 Starting UUID-based database seeding...")
    print("NOTE: Run `CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";` in Supabase SQL Editor before seeding.")
    print("="*60 + "\n")
    # small sleep to ensure supabase client ready
    time.sleep(0.5)

    # 1. users
    try:
        seed_users()
    except Exception:
        print("Continuing despite users insertion error...")

    # 2. locations
    locations = []
    try:
        locations = seed_locations()
    except Exception:
        # try to read existing locations if insert fails
        try:
            r = supabase.table("locations").select("*").execute()
            locations = getattr(r, "data", r) or []
            print(f"Loaded {len(locations)} existing locations from DB")
        except Exception as e:
            print("ERROR: Could not seed or fetch locations — aborting.")
            raise e

    # 3. climate
    try:
        seed_climate_data(locations)
    except Exception:
        print("Skipped climate_data seeding due to error.")

    # 4. land health
    try:
        seed_land_health(locations)
    except Exception:
        print("Skipped land_health seeding due to error.")

    # 5. predictions / prediction_logs
    prediction_rows = []
    try:
        prediction_rows = seed_predictions(locations)
    except Exception:
        print("Skipped predictions due to error.")

    # 6. degradation risk / risk_assessments
    risk_rows = []
    try:
        risk_rows = seed_degradation_risk(locations)
    except Exception:
        print("Skipped degradation risk due to error.")

    # 7. recommendations
    try:
        seed_recommendations(locations, risk_rows)
    except Exception:
        print("Skipped recommendations due to error.")

    # 8. alerts
    try:
        seed_alerts(locations)
    except Exception:
        print("Skipped alerts due to error.")

    # Verify
    verify_data(["users", "locations", "climate_data", "land_health", "predictions", "prediction_logs", "degradation_risk", "risk_assessments", "recommendations", "alerts"])

    print("\nSeeding run finished.")

if __name__ == "__main__":
    main()
