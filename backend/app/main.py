"""
FastAPI Backend - TerraGuard AI
Includes: Locations, Climate, Land Health, Risk, Recommendations & Dashboard Summary
WITH HuggingFace AI Integration
READY FOR DEPLOYMENT
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

# Enable detailed logs FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import your HuggingFace recommendation service
try:
    from app.huggingface_recommendations import HuggingFaceRecommendationService
    HF_SERVICE_AVAILABLE = True
    logger.info("✅ HuggingFace Recommendation Service imported successfully")
except ImportError as e:
    HF_SERVICE_AVAILABLE = False
    logger.warning(f"⚠️ HuggingFace service not available: {e}")
    logger.warning("Will use simple fallback recommendations")

# ----------------------------------------------------------------------------
# APP INITIALIZATION
# ----------------------------------------------------------------------------
app = FastAPI(title="TerraGuard AI API", version="1.2.0")

# Enable detailed logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# CORS SETUP - UPDATED FOR DEPLOYMENT
# ----------------------------------------------------------------------------
# Get allowed origins from environment variable or use defaults
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,https://*.vercel.app"
).split(",")

# Add common deployment domains
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://*.vercel.app",  # All Vercel deployments
    "https://vercel.app",
    "*://*.vercel.app",  # With wildcard protocol
]

# Add custom domains from environment if provided
if os.getenv("FRONTEND_URL"):
    CORS_ORIGINS.append(os.getenv("FRONTEND_URL"))

logger.info(f"🌐 CORS enabled for origins: {CORS_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# For production, use this more secure version:
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "https://your-app.vercel.app",  # Replace with your actual domain
#         "https://terraguard.vercel.app",
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )

# ----------------------------------------------------------------------------
# SUPABASE CONNECTION
# ----------------------------------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
logger.info("✅ Connected to Supabase successfully.")

# ----------------------------------------------------------------------------
# INITIALIZE HUGGINGFACE SERVICE
# ----------------------------------------------------------------------------

#  Use default model (Mistral-7B-Instruct)
if HF_SERVICE_AVAILABLE:
    recommendation_service = HuggingFaceRecommendationService()
    logger.info("✅ HuggingFace Recommendation Service initialized with default model")
else:
    recommendation_service = None
    logger.warning("⚠️ Running without AI recommendation service (will use rule-based)")


# ----------------------------------------------------------------------------
# RESPONSE MODELS
# ----------------------------------------------------------------------------
class Recommendation(BaseModel):
    id: UUID
    location_id: UUID
    priority: str
    category: str
    action_title: str
    action_description: str
    recommended_start_date: str
    recommended_end_date: str
    urgency_hours: int
    expected_risk_reduction: float
    expected_cost_usd: float
    recommended_species: Optional[List[dict]] = None
    status: str


# ----------------------------------------------------------------------------
# LOCATIONS
# ----------------------------------------------------------------------------
@app.get("/api/locations/")
async def get_locations():
    """Fetch all locations"""
    try:
        result = supabase.table("locations").select("*").execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Error fetching locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/locations/{location_id}")
async def get_location(location_id: UUID):
    """Fetch single location"""
    try:
        result = (
            supabase.table("locations")
            .select("*")
            .eq("id", str(location_id))
            .single()
            .execute()
        )
        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Error fetching location {location_id}: {e}")
        raise HTTPException(status_code=404, detail="Location not found")


# ----------------------------------------------------------------------------
# CLIMATE DATA
# ----------------------------------------------------------------------------

@app.get("/api/climate/{location_id}")
async def get_climate_data(location_id: UUID, days: int = 30):
    """Get climate history for a location"""
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
    """Get latest climate record"""
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
        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Error fetching latest climate data: {e}")
        raise HTTPException(status_code=404, detail="No climate data found")
    

# Climate forecast

@app.get("/api/climate/{location_id}/forecast")
async def get_climate_forecast(location_id: UUID, days: int = 7):
    """
    Return recent climate forecast data for the next X days.
    React dashboard expects a list with 'temperature' and 'date'.
    """
    try:
        result = (
            supabase.table("climate_data")
            .select("date, temperature, humidity, precipitation")
            .eq("location_id", str(location_id))
            .order("date", desc=True)
            .limit(days)
            .execute()
        )

        if not result.data:
            return {"success": True, "data": []}

        # Normalize for dashboard readability
        forecast = [
            {
                "date": row.get("date"),
                "temperature": row.get("temperature") or 0,
                "humidity": row.get("humidity"),
                "rainfall": row.get("precipitation") or 0,  # Map precipitation to rainfall for backward compatibility
                "precipitation": row.get("precipitation") or 0,
            }
            for row in result.data
        ]
        return {"success": True, "data": forecast}

    except Exception as e:
        logger.error(f"Error fetching forecast for {location_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------------
# LAND HEALTH
# ----------------------------------------------------------------------------
@app.get("/api/land-health/{location_id}/latest")
async def get_latest_land_health(location_id: UUID):
    """
    Get latest land health observation.
    Returns ndvi and vegetation_cover for dashboard display.
    """
    try:
        result = (
            supabase.table("land_health")
            .select("id, location_id, ndvi, vegetation_cover, observation_date")
            .eq("location_id", str(location_id))
            .order("observation_date", desc=True)
            .limit(1)
            .single()
            .execute()
        )

        if not result.data:
            return {"success": True, "data": {"ndvi": None, "vegetation_cover": None}}

        # Normalize
        data = result.data
        data["ndvi"] = data.get("ndvi") or 0.0
        data["vegetation_cover"] = data.get("vegetation_cover") or 0.0
        return {"success": True, "data": data}

    except Exception as e:
        logger.error(f"Error fetching land health for {location_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------------
# RISK DATA
# ----------------------------------------------------------------------------
@app.get("/api/risk/{location_id}/latest")
async def get_latest_risk(location_id: UUID):
    """Fetch latest risk record"""
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
        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Error fetching risk data: {e}")
        raise HTTPException(status_code=404, detail="No risk data found")


@app.get("/api/risk/{location_id}/trend")
async def get_risk_trend(location_id: UUID, months: int = 6):
    """Fetch degradation risk trend for given location"""
    try:
        start_date = (datetime.utcnow() - timedelta(days=30 * months)).isoformat()

        response = (
            supabase.table("degradation_risk")
            .select("*")
            .eq("location_id", str(location_id))
            .gte("assessment_date", start_date)
            .order("assessment_date", desc=False)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="No risk trend data found")

        return {"success": True, "data": response.data}
    except Exception as e:
        logger.error(f"Error fetching risk trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------------
# RECOMMENDATIONS
# ----------------------------------------------------------------------------
@app.get("/api/recommendations/{location_id}")
async def get_recommendations(location_id: UUID, status: Optional[str] = None):
    """Fetch recommendations for a location"""
    try:
        query = supabase.table("recommendations").select("*").eq("location_id", str(location_id))
        if status:
            query = query.eq("status", status)
        result = query.order("priority", desc=True).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommendations/generate/{location_id}")
async def generate_recommendations(location_id: UUID):
    """
    Generate AI-powered recommendations using HuggingFace
    Falls back to rule-based if AI service is unavailable
    """
    try:
        logger.info(f"🤖 Generating recommendations for location: {location_id}")
        
        # Fetch required data from database
        try:
            location_result = await get_location(location_id)
            location_data = location_result.get("data", {})
            if not location_data:
                raise HTTPException(status_code=404, detail=f"Location {location_id} not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching location: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch location data: {str(e)}")
        
        # Fetch latest risk assessment
        try:
            risk_result = await get_latest_risk(location_id)
            risk_assessment = risk_result.get("data", {})
            logger.info(f"✅ Fetched risk data: {risk_assessment}")
        except Exception as e:
            logger.warning(f"⚠️ No risk data found for {location_id}: {e}, using defaults")
            risk_assessment = {
                "total_risk_score": 50,
                "risk_level": "MEDIUM",
                "drought_risk": 40,
                "erosion_risk": 45,
                "soil_degradation_risk": 50,
                "vegetation_loss_risk": 40
            }
        
        # Fetch latest land health
        try:
            health_result = await get_latest_land_health(location_id)
            land_health = health_result.get("data", {})
            logger.info(f"✅ Fetched health data: {land_health}")
            
            # Ensure required fields exist
            land_health.setdefault("ndvi", 0.5)
            land_health.setdefault("vegetation_cover", 50)
            land_health.setdefault("vegetation_cover_pct", land_health.get("vegetation_cover", 50))
            land_health.setdefault("soil_moisture", 50)
            land_health.setdefault("overall_health_score", 50)
            
        except Exception as e:
            logger.warning(f"⚠️ No health data found for {location_id}: {e}, using defaults")
            land_health = {
                "ndvi": 0.5,
                "vegetation_cover": 50,
                "vegetation_cover_pct": 50,
                "soil_moisture": 50,
                "overall_health_score": 50
            }
        
        # Fetch climate forecast
        try:
            forecast_result = await get_climate_forecast(location_id, days=14)
            climate_forecast = forecast_result.get("data", [])
            logger.info(f"✅ Fetched {len(climate_forecast)} climate forecast records")
            
            # Transform to expected format
            climate_forecast = [
                {
                    "date": item.get("date"),
                    "temp_avg": item.get("temperature", 25),
                    "precipitation": item.get("rainfall", 0)
                }
                for item in climate_forecast
            ]
        except Exception as e:
            logger.warning(f"⚠️ No climate data found for {location_id}: {e}, using defaults")
            climate_forecast = [
                {"date": "2025-10-13", "temp_avg": 25, "precipitation": 5},
                {"date": "2025-10-14", "temp_avg": 26, "precipitation": 10},
                {"date": "2025-10-15", "temp_avg": 24, "precipitation": 2},
            ]
        
        # Generate recommendations using AI or rule-based
        try:
            if recommendation_service:
                logger.info("🧠 Using HuggingFace AI for recommendations")
                recommendations = recommendation_service.generate_recommendations(
                    location_data=location_data,
                    risk_assessment=risk_assessment,
                    land_health=land_health,
                    climate_forecast=climate_forecast
                )
            else:
                logger.info("📋 Using rule-based recommendations (no AI service)")
                # Simple fallback without needing import
                recommendations = [
                    {
                        "priority": "HIGH",
                        "category": "general",
                        "action_title": "Monitor land health closely",
                        "action_description": "Regular monitoring recommended based on current risk levels. AI recommendations unavailable.",
                        "urgency_hours": 168,
                        "expected_risk_reduction": 15.0,
                        "recommended_species": None
                    }
                ]
            
            if not recommendations or len(recommendations) == 0:
                raise ValueError("No recommendations generated")
                
            logger.info(f"✅ Generated {len(recommendations)} recommendations")
            
        except Exception as gen_error:
            logger.error(f"❌ Error in recommendation generation: {gen_error}")
            logger.exception("Generation error traceback:")
            # Use absolute fallback
            recommendations = [
                {
                    "priority": "MEDIUM",
                    "category": "monitoring",
                    "action_title": "Establish regular monitoring routine",
                    "action_description": "Set up a monitoring schedule to track land health indicators. This will help identify issues early.",
                    "urgency_hours": 168,
                    "expected_risk_reduction": 10.0,
                    "recommended_species": None
                }
            ]
        
        # Save recommendations to database
        saved_recommendations = []
        for rec in recommendations:
            try:
                # Prepare database record
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
                
                # Insert into database
                result = supabase.table("recommendations").insert(db_rec).execute()
                saved_recommendations.append(result.data[0] if result.data else db_rec)
                
                logger.info(f"✅ Saved recommendation: {db_rec['action_title']}")
                
            except Exception as insert_error:
                logger.error(f"Error saving recommendation: {insert_error}")
                continue
        
        if len(saved_recommendations) == 0:
            raise HTTPException(
                status_code=500, 
                detail="Generated recommendations but failed to save to database"
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
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate recommendations: {str(e)}"
        )


# ----------------------------------------------------------------------------
# DASHBOARD SUMMARY
# ----------------------------------------------------------------------------
@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Summary stats for dashboard"""
    try:
        locations_count = supabase.table("locations").select("*", count="exact").execute()
        climate_count = supabase.table("climate_data").select("*", count="exact").execute()
        health_count = supabase.table("land_health").select("*", count="exact").execute()

        high_risk = (
            supabase.table("degradation_risk")
            .select("*")
            .gte("total_risk_score", 50)
            .order("total_risk_score", desc=True)
            .limit(5)
            .execute()
        )

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
                "total_locations": locations_count.count or 0,
                "total_climate_records": climate_count.count or 0,
                "total_health_records": health_count.count or 0,
                "high_risk_locations": high_risk.data or [],
                "pending_recommendations": pending_recs.data or [],
            },
        }
    except Exception as e:
        logger.error(f"Error building dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------------
# HEALTH CHECK
# ----------------------------------------------------------------------------
@app.get("/")
async def root():
    ai_status = "enabled" if recommendation_service else "disabled (rule-based fallback)"
    return {
        "status": "online", 
        "message": "TerraGuard AI API", 
        "version": "1.2.0",
        "ai_recommendations": ai_status
    }


@app.get("/health")
async def health_check():
    try:
        supabase.table("locations").select("id").limit(1).execute()
        ai_status = "available" if recommendation_service else "unavailable"
        return {
            "status": "healthy", 
            "timestamp": datetime.now().isoformat(),
            "ai_service": ai_status
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e), 
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/test/recommendation-service")
async def test_recommendation_service():
    """Test endpoint to verify recommendation service is working"""
    try:
        result = {
            "service_available": HF_SERVICE_AVAILABLE,
            "service_initialized": recommendation_service is not None,
        }
        
        if recommendation_service:
            result["model"] = recommendation_service.model
            result["has_api_key"] = recommendation_service.client is not None
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ----------------------------------------------------------------------------
# RUN LOCALLY
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)