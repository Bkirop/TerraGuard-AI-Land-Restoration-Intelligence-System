"""
AI Predictions Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import logging
from datetime import datetime, timedelta

from app.models import DegradationRiskCreate, DegradationRiskResponse
from app.database import supabase
from app.services.degradation_services import DegradationRiskCalculator

router = APIRouter(prefix="/predictions", tags=["AI Predictions"])
logger = logging.getLogger(__name__)


@router.get("/risk/{location_id}", response_model=DegradationRiskResponse)
async def get_degradation_risk(location_id: str):
    """
    Get current degradation risk assessment
    
    Returns the most recent risk assessment for a location
    """
    try:
        result = supabase.table("degradation_risk")\
            .select("*")\
            .eq("location_id", location_id)\
            .order("assessment_date", desc=True)\
            .limit(1)\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="No risk assessment found for this location"
            )
        
        return result.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching degradation risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk/calculate/{location_id}", response_model=DegradationRiskResponse)
async def calculate_degradation_risk(location_id: str):
    """
    Calculate degradation risk for a location
    
    Uses AI models to assess multiple risk factors and generate overall score
    """
    try:
        # Get latest climate data (including forecasts)
        climate_result = supabase.table("climate_data")\
            .select("*")\
            .eq("location_id", location_id)\
            .order("date", desc=True)\
            .limit(60)\
            .execute()
        
        if not climate_result.data:
            raise HTTPException(
                status_code=404,
                detail="No climate data found for risk calculation"
            )
        
        climate_data = climate_result.data
        
        # Get latest land health data
        land_health_result = supabase.table("land_health")\
            .select("*")\
            .eq("location_id", location_id)\
            .order("observation_date", desc=True)\
            .limit(1)\
            .execute()
        
        if not land_health_result.data:
            raise HTTPException(
                status_code=404,
                detail="No land health data found for risk calculation"
            )
        
        land_health = land_health_result.data[0]
        
        # Get location data
        location_result = supabase.table("locations")\
            .select("*")\
            .eq("id", location_id)\
            .single()\
            .execute()
        
        location_data = location_result.data
        
        # Calculate risk using AI model
        calculator = DegradationRiskCalculator()
        risk_assessment = calculator.calculate_risk(
            climate_data,
            land_health,
            location_data
        )
        
        # Add location_id
        risk_assessment['location_id'] = location_id
        
        # Store in database
        result = supabase.table("degradation_risk").insert(risk_assessment).execute()
        
        logger.info(f"Calculated risk for location {location_id}: {risk_assessment['total_risk_score']}%")
        
        return result.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating degradation risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/{location_id}/history")
async def get_risk_history(
    location_id: str,
    limit: int = Query(30, ge=1, le=365, description="Number of assessments to retrieve")
):
    """
    Get historical risk assessments
    
    Returns time series of risk scores to show trends
    """
    try:
        result = supabase.table("degradation_risk")\
            .select("*")\
            .eq("location_id", location_id)\
            .order("assessment_date", desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data
    
    except Exception as e:
        logger.error(f"Error fetching risk history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-calculate")
async def batch_calculate_risks(location_ids: list[str] = None):
    """
    Calculate degradation risk for multiple locations
    
    Useful for updating all locations at once (e.g., daily cron job)
    """
    try:
        # If no location_ids provided, get all locations
        if not location_ids:
            locations_result = supabase.table("locations").select("id").execute()
            location_ids = [loc['id'] for loc in locations_result.data]
        
        results = []
        errors = []
        
        for location_id in location_ids:
            try:
                # Use the calculate endpoint logic
                result = await calculate_degradation_risk(location_id)
                results.append({
                    'location_id': location_id,
                    'status': 'success',
                    'risk_score': result['total_risk_score']
                })
            except Exception as e:
                errors.append({
                    'location_id': location_id,
                    'status': 'failed',
                    'error': str(e)
                })
                logger.error(f"Failed to calculate risk for {location_id}: {e}")
        
        return {
            'total': len(location_ids),
            'successful': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors
        }
    
    except Exception as e:
        logger.error(f"Error in batch risk calculation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/{location_id}")
async def get_degradation_forecast(
    location_id: str,
    days_ahead: int = Query(30, ge=7, le=90, description="Days to forecast")
):
    """
    Forecast future degradation risk
    
    Uses ML models to predict risk scores for future dates
    """
    try:
        # This is a placeholder for ML forecasting
        # In production, you would:
        # 1. Load trained LSTM/Prophet model
        # 2. Feed historical risk data
        # 3. Generate predictions
        
        # For now, return a simple forecast based on current trend
        history_result = supabase.table("degradation_risk")\
            .select("*")\
            .eq("location_id", location_id)\
            .order("assessment_date", desc=True)\
            .limit(10)\
            .execute()
        
        if not history_result.data:
            raise HTTPException(
                status_code=404,
                detail="Insufficient data for forecasting"
            )
        
        history = history_result.data
        
        # Simple trend-based forecast
        recent_scores = [h['total_risk_score'] for h in history[:5]]
        avg_score = sum(recent_scores) / len(recent_scores)
        
        # Calculate trend
        if len(history) >= 2:
            trend = history[0]['total_risk_score'] - history[-1]['total_risk_score']
            daily_change = trend / len(history)
        else:
            daily_change = 0
        
        # Generate forecast
        forecast = []
        for day in range(1, days_ahead + 1):
            predicted_score = min(100, max(0, avg_score + (daily_change * day)))
            forecast.append({
                'day': day,
                'date': (datetime.now() + timedelta(days=day)).date().isoformat(),
                'predicted_risk_score': round(predicted_score, 2),
                'confidence_lower': round(max(0, predicted_score - 10), 2),
                'confidence_upper': round(min(100, predicted_score + 10), 2)
            })
        
        return {
            'location_id': location_id,
            'forecast_days': days_ahead,
            'current_score': history[0]['total_risk_score'],
            'trend': 'increasing' if daily_change > 0 else 'decreasing',
            'forecast': forecast
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating degradation forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/yield-prediction/{location_id}")
async def predict_crop_yield(
    location_id: str,
    crop_type: str = Query(..., description="Type of crop (e.g., maize, beans)")
):
    """
    Predict crop yield based on land health and climate
    
    Uses ML models trained on historical yield data
    """
    try:
        # Get recent land health
        land_health_result = supabase.table("land_health")\
            .select("*")\
            .eq("location_id", location_id)\
            .order("observation_date", desc=True)\
            .limit(1)\
            .execute()
        
        if not land_health_result.data:
            raise HTTPException(status_code=404, detail="No land health data found")
        
        land_health = land_health_result.data[0]
        
        # Get climate summary
        climate_result = supabase.table("climate_data")\
            .select("*")\
            .eq("location_id", location_id)\
            .order("date", desc=True)\
            .limit(90)\
            .execute()
        
        climate_data = climate_result.data
        
        # Simple yield prediction model (placeholder)
        # In production, use trained ML model for specific crops
        
        # Factors affecting yield
        ndvi_factor = land_health.get('ndvi', 0.5) * 100
        moisture_factor = land_health.get('soil_moisture', 15) * 2
        
        # Calculate average rainfall
        rainfall = [c.get('precipitation', 0) for c in climate_data if c.get('precipitation')]
        avg_rainfall = sum(rainfall) / len(rainfall) if rainfall else 0
        rainfall_factor = min(avg_rainfall / 2, 50)
        
        # Baseline yield (tons per hectare)
        baseline_yields = {
            'maize': 2.5,
            'beans': 1.2,
            'wheat': 2.0,
            'coffee': 0.8
        }
        
        baseline = baseline_yields.get(crop_type.lower(), 1.5)
        
        # Calculate predicted yield
        health_score = (ndvi_factor + moisture_factor + rainfall_factor) / 3
        yield_multiplier = health_score / 50  # Normalize to ~1.0
        
        predicted_yield = baseline * yield_multiplier
        
        return {
            'location_id': location_id,
            'crop_type': crop_type,
            'predicted_yield_tons_per_hectare': round(predicted_yield, 2),
            'baseline_yield': baseline,
            'factors': {
                'ndvi_score': round(ndvi_factor, 1),
                'soil_moisture_score': round(moisture_factor, 1),
                'rainfall_score': round(rainfall_factor, 1),
                'overall_health_score': round(health_score, 1)
            },
            'confidence': 'moderate',
            'note': 'Prediction based on land health and climate factors'
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting crop yield: {e}")
        raise HTTPException(status_code=500, detail=str(e))