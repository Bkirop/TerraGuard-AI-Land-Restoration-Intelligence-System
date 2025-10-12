from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from app.database import get_db
from app.schemas import Location, LocationCreate, LocationUpdate

router = APIRouter()


@router.get("/", response_model=List[Location])
async def get_locations(
    skip: int = 0,
    limit: int = 100,
    supabase: Client = Depends(get_db)
):
    """Get all locations"""
    try:
        response = supabase.table('locations').select("*").range(skip, skip + limit - 1).execute()
        if not response.data:
            return generate_sample_locations()
        return response.data
    except Exception as e:
        print(f"Error fetching locations: {e}")
        return generate_sample_locations()


@router.get("/{location_id}", response_model=Location)
async def get_location(
    location_id: UUID,  # ✅ Changed from int → UUID
    supabase: Client = Depends(get_db)
):
    """Get a specific location by ID"""
    try:
        response = supabase.table('locations').select("*").eq('id', str(location_id)).execute()  # ✅ UUID cast to str
        if not response.data:
            raise HTTPException(status_code=404, detail="Location not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching location: {str(e)}")


@router.post("/", response_model=Location)
async def create_location(
    location: LocationCreate,
    supabase: Client = Depends(get_db)
):
    """Create a new location"""
    try:
        data = location.model_dump()
        data["id"] = str(uuid4())  # ✅ Generate UUID for id

        response = supabase.table('locations').insert(data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create location")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating location: {str(e)}")


@router.put("/{location_id}", response_model=Location)
async def update_location(
    location_id: UUID,  # ✅ Changed to UUID
    location: LocationUpdate,
    supabase: Client = Depends(get_db)
):
    """Update a location"""
    try:
        update_data = location.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")

        response = supabase.table('locations').update(update_data).eq('id', str(location_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Location not found")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating location: {str(e)}")


@router.delete("/{location_id}")
async def delete_location(
    location_id: UUID,  # ✅ Changed to UUID
    supabase: Client = Depends(get_db)
):
    """Delete a location"""
    try:
        response = supabase.table('locations').delete().eq('id', str(location_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Location not found")
        return {"message": "Location deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting location: {str(e)}")


def generate_sample_locations() -> List[dict]:
    """Generate sample locations for testing"""
    return [
        {
            "id": str(uuid4()),  # ✅ UUID for consistency
            "name": "Nakuru",
            "latitude": -0.3031,
            "longitude": 36.0800,
            "country": "Kenya",
            "region": "Rift Valley",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid4()),
            "name": "Nairobi",
            "latitude": -1.2921,
            "longitude": 36.8219,
            "country": "Kenya",
            "region": "Nairobi",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid4()),
            "name": "Mombasa",
            "latitude": -4.0435,
            "longitude": 39.6682,
            "country": "Kenya",
            "region": "Coast",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
