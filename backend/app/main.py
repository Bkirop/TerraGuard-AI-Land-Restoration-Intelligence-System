"""
FastAPI Backend - TerraGuard AI
Complete API with AI-powered recommendations
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from uuid import UUID, uuid4
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import HuggingFace service if available
try:
    from app.huggingface_recommendations import HuggingFaceRecommendationService
    HF_SERVICE_AVAILABLE = True
    logger.info("✅ HuggingFace service imported successfully")
except ImportError as e:
    HF_SERVICE_AVAILABLE = False
    logger.warning(f"⚠️ HuggingFace service not available: {e}")

# ----------------------------------------------------------------------------
# APP INITIALIZATION
# ----------------------------------------------------------------------------
app = FastAPI(
    title="TerraGuard AI API",
    version="1.3.0",
    description="Land restoration intelligence system with AI recommendations"
)

# ----------------------------------------------------------------------------
# CORS CONFIGURATION
# ----------------------------------------------------------------------------
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://*.vercel.app",
]

# Add custom frontend URL from environment
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

logger.info(f"🌐 CORS configured for origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ----------------------------------------------------------------------------
# SUPABASE CONNECTION
# ----------------------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing SUPABASE_URL or SUPABASE_KEY in environment")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Connected to Supabase")
except Exception as e:
    logger.error(f"❌ Failed to connect to Supabase: {e}")
    raise

# ----------------------------------------------------------------------------
# INITIALIZE AI SERVICE
# ----------------------------------------------------------------------------
if HF_SERVICE_AVAILABLE:
    try:
        recommendation_service = HuggingFaceRecommendationService()
        logger.info("✅ AI recommendation service initialized")
    except Exception as e:
        recommendation_service = None
        logger.warning(f"⚠️ AI service initialization failed: {e}")
else:
    recommendation_service = None
    logger.warning("⚠️ Running with rule-based recommendations only")

# ----------------------------------------------------------------------------
# PYDANTIC MODELS
# ----------------------------------------------------------------------------
class LocationCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    area_hectares: Optional[float] = None
    land_type: Optional[str] = None

class RecommendationUpdate(BaseModel):
    status: str

# ----------------------------------------------------------------------------
# HEALTH CHECK ENDPOINTS
# ----------------------------------------------------------------------------
@app.get("/")
async def root():
    """Root endpoint"""
    ai_status = "enabled" if recommendation_service else "rule-based"
    return {
        "status": "online",
        "service": "TerraGuard AI API",
        "version": "1.3.0",
        "ai_recommendations": ai_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        supabase.table("locations").select("id").limit(1).execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "ai_service": "available" if recommendation_service else "unavailable",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ----------------------------------------------------------------------------
# LOCATIONS
# ----------------------------------------------------------------------------
@app.get("/api/locations/")
async def get_locations():
    """Get all locations"""
    try:
        result = supabase.table("locations").select("*").order("name").execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Error fetching locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/locations/{location_id}")
async def get_location(location_id: UUID):
    """Get single location by ID"""
    try:
        result = (
            supabase.table("locations")
            .select("*")
            .eq("id", str(location_id))
            .single()
            .execute()
        )
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Location not found")
            
        return {"success": True, "data": result.data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching location {location_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# CLIMATE DATA
# ----------------------------------------------------------------------------
@app.get("/api/climate/{location_id}")
async def get_climate_data(location_id: UUID, days: int = 30):
    """Get climate data history"""
    try:
        result = (
            supabase.table("climate_data")
            .select("*")
            .eq("location_id", str(location_id))
            .order("date", desc=True)
            .limit(days)
            .execute()
        )
        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Error fetching climate data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/climate/{location_id}/latest")
async def get_latest_climate(location_id: UUID):
    """Get latest climate data"""
    try:
        result = (
            supabase.table("climate_data")
            .select("*")
            .eq("location_id", str(location_id))
            .order("date", desc=True)
            .limit(1)
            .single()
            .execute()
        )
        
        if not result.data:
            raise HTTPException(status_code=404, detail="No climate data found")
            
        return {"success": True, "data": result.data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest climate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/climate/{location_id}/forecast")
async def get_climate_forecast(location_id: UUID, days: int = 7):
    """Get climate forecast"""
    try:
        result = (
            supabase.table("climate_data")
            .select("date, temperature, humidity, precipitation")
            .eq("location_id", str(location_id))
            .order("date", desc=True)
            .limit(days)
            .execute()
        )

        forecast = [
            {
                "date": row.get("date"),
                "temperature": row.get("temperature", 0),
                "humidity": row.get("humidity"),
                "rainfall": row.get("precipitation", 0),
                "precipitation": row.get("precipitation", 0),
            }
            for row in (result.data or [])
        ]
        
        return {"success": True, "data": forecast}
    except Exception as e:
        logger.error(f"Error fetching forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# LAND HEALTH
# ----------------------------------------------------------------------------
@app.get("/api/land-health/{location_id}/latest")
async def get_latest_land_health(location_id: UUID):
    """Get latest land health data"""
    try:
        result = (
            supabase.table("land_health")
            .select("*")
            .eq("location_id", str(location_id))
            .order("observation_date", desc=True)
            .limit(1)
            .single()
            .execute()
        )

        if not result.data:
            return {
                "success": True, 
                "data": {
                    "ndvi": None, 
                    "vegetation_cover": None,
                    "soil_moisture": None
                }
            }

        data = result.data
        data["ndvi"] = data.get("ndvi") or 0.0
        data["vegetation_cover"] = data.get("vegetation_cover") or 0.0
        data["soil_moisture"] = data.get("soil_moisture") or 0.0
        
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching land health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# RISK DATA
# ----------------------------------------------------------------------------
@app.get("/api/risk/{location_id}/latest")
async def get_latest_risk(location_id: UUID):
    """Get latest risk assessment"""
    try:
        result = (
            supabase.table("degradation_risk")
            .select("*")
            .eq("location_id", str(location_id))
            .order("assessment_date", desc=True)
            .limit(1)
            .single()
            .execute()
        )
        
        if not result.data:
            raise HTTPException(status_code=404, detail="No risk data found")
            
        return {"success": True, "data": result.data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching risk data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk/{location_id}/trend")
async def get_risk_trend(location_id: UUID, months: int = 6):
    """Get risk trend over time"""
    try:
        start_date = (datetime.now() - timedelta(days=30 * months)).isoformat()

        result = (
            supabase.table("degradation_risk")
            .select("*")
            .eq("location_id", str(location_id))
            .gte("assessment_date", start_date)
            .order("assessment_date", desc=False)
            .execute()
        )

        return {"success": True, "data": result.data or []}
    except Exception as e:
        logger.error(f"Error fetching risk trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# RECOMMENDATIONS
# ----------------------------------------------------------------------------
@app.get("/api/recommendations/{location_id}")
async def get_recommendations(location_id: UUID, status: Optional[str] = None):
    """Get recommendations for a location"""
    try:
        query = (
            supabase.table("recommendations")
            .select("*")
            .eq("location_id", str(location_id))
        )
        
        if status:
            query = query.eq("status", status)
            
        result = query.order("priority", desc=True).execute()
        
        return {"success": True, "data": result.data or []}
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations/generate/{location_id}")
async def generate_recommendations(location_id: UUID):
    """Generate AI-powered recommendations"""
    try:
        logger.info(f"🤖 Generating recommendations for location: {location_id}")
        
        # Fetch location data
        location_result = await get_location(location_id)
        location_data = location_result.get("data", {})
        
        # Fetch risk assessment
        try:
            risk_result = await get_latest_risk(location_id)
            risk_assessment = risk_result.get("data", {})
        except:
            risk_assessment = {
                "total_risk_score": 50,
                "risk_level": "MEDIUM",
                "drought_risk": 40,
                "erosion_risk": 45,
            }
        
        # Fetch land health
        try:
            health_result = await get_latest_land_health(location_id)
            land_health = health_result.get("data", {})
        except:
            land_health = {
                "ndvi": 0.5,
                "vegetation_cover": 50,
                "soil_moisture": 50,
            }
        
        # Fetch climate forecast
        try:
            forecast_result = await get_climate_forecast(location_id, days=7)
            climate_forecast = forecast_result.get("data", [])
        except:
            climate_forecast = []
        
        # Generate recommendations using AI or rules
        if recommendation_service:
            logger.info("🧠 Using AI service for recommendations")
            recommendations = recommendation_service.generate_recommendations(
                location_data=location_data,
                risk_assessment=risk_assessment,
                land_health=land_health,
                climate_forecast=climate_forecast
            )
        else:
            logger.info("📋 Using rule-based recommendations")
            recommendations = generate_rule_based_recommendations(
                risk_assessment, land_health
            )
        
        # Save recommendations to database
        saved_recommendations = []
        for rec in recommendations:
            now = datetime.now()
            urgency_hours = rec.get("urgency_hours", 168)
            
            db_rec = {
                "id": str(uuid4()),
                "location_id": str(location_id),
                "priority": rec.get("priority", "MEDIUM").lower(),
                "category": rec.get("category", "general"),
                "action_title": rec.get("action_title", "Action required"),
                "action_description": rec.get("action_description", ""),
                "recommended_start_date": now.strftime("%Y-%m-%d"),
                "recommended_end_date": (now + timedelta(hours=urgency_hours)).strftime("%Y-%m-%d"),
                "urgency_hours": urgency_hours,
                "expected_risk_reduction": rec.get("expected_risk_reduction", 0.0),
                "expected_cost_usd": rec.get("expected_cost_usd", 0.0),
                "recommended_species": rec.get("recommended_species"),
                "status": "pending",
                "created_at": now.isoformat()
            }
            
            try:
                result = supabase.table("recommendations").insert(db_rec).execute()
                saved_recommendations.append(result.data[0] if result.data else db_rec)
                logger.info(f"✅ Saved: {db_rec['action_title']}")
            except Exception as insert_error:
                logger.error(f"Error saving recommendation: {insert_error}")
                continue
        
        if len(saved_recommendations) == 0:
            raise HTTPException(
                status_code=500,
                detail="Failed to save recommendations to database"
            )
        
        return {
            "success": True,
            "message": f"Generated {len(saved_recommendations)} recommendations",
            "data": saved_recommendations,
            "ai_powered": recommendation_service is not None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_rule_based_recommendations(risk_assessment, land_health):
    """Fallback rule-based recommendation generator"""
    recommendations = []
    
    # Risk-based recommendations
    risk_score = risk_assessment.get("total_risk_score", 0)
    if risk_score > 70:
        recommendations.append({
            "priority": "HIGH",
            "category": "risk_management",
            "action_title": "Urgent Risk Mitigation Required",
            "action_description": "Implement immediate erosion control and soil stabilization measures.",
            "urgency_hours": 72,
            "expected_risk_reduction": 30.0,
            "expected_cost_usd": 5000.0
        })
    elif risk_score > 50:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "monitoring",
            "action_title": "Enhanced Monitoring Setup",
            "action_description": "Increase monitoring frequency to track land degradation indicators.",
            "urgency_hours": 168,
            "expected_risk_reduction": 15.0,
            "expected_cost_usd": 1500.0
        })
    
    # Vegetation-based recommendations
    vegetation_cover = land_health.get("vegetation_cover", 0)
    if vegetation_cover < 50:
        recommendations.append({
            "priority": "HIGH",
            "category": "vegetation",
            "action_title": "Vegetation Restoration",
            "action_description": "Plant native species to increase vegetation cover and biodiversity.",
            "urgency_hours": 336,
            "expected_risk_reduction": 25.0,
            "expected_cost_usd": 3500.0,
            "recommended_species": [
                {"name": "Acacia", "count": 50},
                {"name": "Native Grass", "count": 100}
            ]
        })
    
    # Soil health recommendations
    ndvi = land_health.get("ndvi", 0)
    if ndvi < 0.4:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "soil_management",
            "action_title": "Soil Health Improvement",
            "action_description": "Add organic matter and implement conservation tillage practices.",
            "urgency_hours": 504,
            "expected_risk_reduction": 20.0,
            "expected_cost_usd": 2000.0
        })
    
    # Default recommendation if none generated
    if not recommendations:
        recommendations.append({
            "priority": "LOW",
            "category": "assessment",
            "action_title": "Baseline Assessment",
            "action_description": "Conduct comprehensive land assessment to establish baseline metrics.",
            "urgency_hours": 720,
            "expected_risk_reduction": 10.0,
            "expected_cost_usd": 1000.0
        })
    
    return recommendations

@app.put("/api/recommendations/{recommendation_id}")
async def update_recommendation(recommendation_id: UUID, update: RecommendationUpdate):
    """Update recommendation status"""
    try:
        updates = {"status": update.status}
        
        if update.status == "completed":
            updates["completed_at"] = datetime.now().isoformat()
        
        result = (
            supabase.table("recommendations")
            .update(updates)
            .eq("id", str(recommendation_id))
            .execute()
        )
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        return {"success": True, "data": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# ALERTS
# ----------------------------------------------------------------------------
@app.get("/api/alerts/{location_id}")
async def get_alerts(location_id: UUID, active_only: bool = True):
    """Get alerts for a location"""
    try:
        query = (
            supabase.table("alerts")
            .select("*")
            .eq("location_id", str(location_id))
        )
        
        if active_only:
            query = query.eq("is_active", True)
        
        result = query.order("created_at", desc=True).execute()
        
        return {"success": True, "data": result.data or []}
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# DASHBOARD SUMMARY
# ----------------------------------------------------------------------------
@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard summary statistics"""
    try:
        # Get counts
        locations = supabase.table("locations").select("*", count="exact").execute()
        climate_records = supabase.table("climate_data").select("*", count="exact").execute()
        health_records = supabase.table("land_health").select("*", count="exact").execute()
        
        # Get high-risk locations
        high_risk = (
            supabase.table("degradation_risk")
            .select("*")
            .gte("total_risk_score", 50)
            .order("total_risk_score", desc=True)
            .limit(5)
            .execute()
        )
        
        # Get pending recommendations
        pending_recs = (
            supabase.table("recommendations")
            .select("*")
            .eq("status", "pending")
            .order("priority", desc=True)
            .limit(10)
            .execute()
        )
        
        return {
            "success": True,
            "data": {
                "total_locations": locations.count or 0,
                "total_climate_records": climate_records.count or 0,
                "total_health_records": health_records.count or 0,
                "high_risk_locations": high_risk.data or [],
                "pending_recommendations": pending_recs.data or [],
            },
        }
    except Exception as e:
        logger.error(f"Error building dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------------
# TEST ENDPOINTS
# ----------------------------------------------------------------------------
@app.get("/api/test/ai-service")
async def test_ai_service():
    """Test if AI service is available"""
    return {
        "success": True,
        "data": {
            "service_available": HF_SERVICE_AVAILABLE,
            "service_initialized": recommendation_service is not None,
            "model": getattr(recommendation_service, "model", None) if recommendation_service else None
        }
    }

# ----------------------------------------------------------------------------
# RUN SERVER
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)