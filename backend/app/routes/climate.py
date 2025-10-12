"""
Climate data endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from app.database import supabase
from app.services.weather_services import WeatherStreamingService

router = APIRouter(prefix="/api/climate", tags=["climate"])


@router.get("/{location_id}/current-weather")
async def get_current_weather(location_id: str):
    """Get real-time weather for location"""
    try:
        # Get location coordinates
        location = supabase.table("locations").select("*").eq("id", location_id).execute()
        
        if not location.data:
            raise HTTPException(status_code=404, detail="Location not found")
        
        loc = location.data[0]
        
        # Fetch real-time weather
        async with WeatherStreamingService() as weather_service:
            weather = await weather_service.get_current_weather(
                loc['latitude'],
                loc['longitude']
            )
        
        return {
            "location_id": location_id,
            "location_name": loc['name'],
            "weather": weather,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}/forecast")
async def get_weather_forecast(location_id: str, days: int = Query(default=7, le=16)):
    """Get weather forecast"""
    try:
        # Get location
        location = supabase.table("locations").select("*").eq("id", location_id).execute()
        
        if not location.data:
            raise HTTPException(status_code=404, detail="Location not found")
        
        loc = location.data[0]
        
        # Fetch forecast
        async with WeatherStreamingService() as weather_service:
            forecast = await weather_service.get_forecast(
                loc['latitude'],
                loc['longitude'],
                days
            )
        
        return {
            "location_id": location_id,
            "location_name": loc['name'],
            "forecast": forecast,
            "forecast_days": days
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))