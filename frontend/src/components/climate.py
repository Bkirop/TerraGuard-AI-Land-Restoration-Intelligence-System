"""
Climate Data Routes
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging

from app.models import ClimateDataCreate, ClimateDataResponse
from app.database import supabase
from app.services.weather_services import fetch_climate_data_multi_source

router = APIRouter(prefix="/climate", tags=["Climate Data"])
logger = logging.getLogger(__name__)


@router.get("/{location_id}", response_model=List[ClimateDataResponse])
async def get_climate_data(
    location_id: str,
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    is_forecast: Optional[bool] = Query(None, description="Filter by forecast/historical"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return")
):
    """
    Get climate data for a location
    
    Returns historical or forecast climate data based on filters
    """
    try:
        query = supabase.table("climate_data")\
            .select("*")\
            .eq("location_id", location_id)
        
        if start_date:
            query = query.gte("date", start_date.isoformat())
        if end_date:
            query = query.lte("date", end_date.isoformat())
        if is_forecast is not None:
            query = query.eq("is_forecast", is_forecast)
        
        query = query.order("date", desc=True).limit(limit)
        result = query.execute()
        
        return result.data
    
    except Exception as e:
        logger.error(f"Error fetching climate data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ClimateDataResponse, status_code=201)
async def create_climate_data(climate_data: ClimateDataCreate):
    """
    Add climate data record
    
    Inserts or updates climate data for a specific location and date
    """
    try:
        data = climate_data.dict()
        data['date'] = data['date'].isoformat()
        
        result = supabase.table("climate_data").upsert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to insert climate data")
        
        return result.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating climate data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{location_id}/fetch", response_model=List[ClimateDataResponse])
async def fetch_and_store_climate_data(
    location_id: str,
    days_history: int = Query(90, ge=1, le=3650, description="Days of historical data to fetch")
):
    """
    Fetch climate data from external APIs and store in database
    
    Pulls data from World Bank, NASA POWER, or Open-Meteo APIs
    """
    try:
        # Get location details
        location_result = supabase.table("locations")\
            .select("latitude, longitude")\
            .eq("id", location_id)\
            .single()\
            .execute()
        
        if not location_result.data:
            raise HTTPException(status_code=404, detail="Location not found")
        
        location = location_result.data
        
        # Fetch climate data from external APIs
        climate_data = fetch_climate_data_multi_source(
            location['latitude'],
            location['longitude'],
            days_history
        )
        
        if not climate_data:
            raise HTTPException(
                status_code=503,
                detail="Failed to fetch climate data from external APIs"
            )
        
        # Prepare data for insertion
        records = []
        for record in climate_data:
            records.append({
                'location_id': location_id,
                'date': record.get('date'),
                'temp_avg': record.get('temp_avg'),
                'temp_max': record.get('temp_max'),
                'temp_min': record.get('temp_min'),
                'precipitation': record.get('precipitation'),
                'humidity': record.get('humidity'),
                'wind_speed': record.get('wind_speed'),
                'solar_radiation': record.get('solar_radiation'),
                'source': record.get('source', 'api'),
                'is_forecast': record.get('is_forecast', False)
            })
        
        # Bulk insert (upsert to avoid duplicates)
        result = supabase.table("climate_data").upsert(records).execute()
        
        logger.info(f"Stored {len(result.data)} climate records for location {location_id}")
        
        return result.data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching and storing climate data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}/summary")
async def get_climate_summary(
    location_id: str,
    days: int = Query(30, ge=1, le=365, description="Days to summarize")
):
    """
    Get climate summary statistics for a location
    
    Returns averages, min/max values for the specified period
    """
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        result = supabase.table("climate_data")\
            .select("*")\
            .eq("location_id", location_id)\
            .gte("date", start_date.isoformat())\
            .lte("date", end_date.isoformat())\
            .eq("is_forecast", False)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="No climate data found")
        
        data = result.data
        
        # Calculate statistics
        temps = [d['temp_avg'] for d in data if d.get('temp_avg') is not None]
        precips = [d['precipitation'] for d in data if d.get('precipitation') is not None]
        
        summary = {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'records_count': len(data),
            'temperature': {
                'avg': round(sum(temps) / len(temps), 2) if temps else None,
                'min': round(min(temps), 2) if temps else None,
                'max': round(max(temps), 2) if temps else None
            },
            'precipitation': {
                'total': round(sum(precips), 2) if precips else None,
                'avg_daily': round(sum(precips) / len(precips), 2) if precips else None,
                'max_daily': round(max(precips), 2) if precips else None
            }
        }
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating climate summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{location_id}")
async def delete_climate_data(
    location_id: str,
    before_date: Optional[date] = Query(None, description="Delete records before this date")
):
    """
    Delete climate data for a location
    
    Can optionally specify a date to delete only old records
    """
    try:
        query = supabase.table("climate_data").delete().eq("location_id", location_id)
        
        if before_date:
            query = query.lt("date", before_date.isoformat())
        
        result = query.execute()
        
        return {
            "message": "Climate data deleted successfully",
            "location_id": location_id,
            "deleted_count": len(result.data) if result.data else 0
        }
    
    except Exception as e:
        logger.error(f"Error deleting climate data: {e}")
        raise HTTPException(status_code=500, detail=str(e))