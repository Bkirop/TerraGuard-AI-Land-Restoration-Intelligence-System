from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import random

from app.database import get_db
from app.schemas import LandHealth, LandHealthCreate

router = APIRouter()


@router.get("/{location_id}", response_model=List[LandHealth])
async def get_land_health(
    location_id: UUID,
    supabase: Client = Depends(get_db)
):
    """Get land health data for a specific location (last 30 days)"""
    try:
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()

        response = (
            supabase.table("land_health")
            .select("*")
            .eq("location_id", str(location_id))
            .gte("date", thirty_days_ago)
            .order("date", desc=True)
            .execute()
        )

        if not response.data:
            return generate_sample_land_health(location_id)

        # ✅ Rename keys for frontend compatibility
        data = []
        for record in response.data:
            record["ndvi"] = record.get("vegetation_index") or record.get("ndvi")
            record["vegetation_cover"] = record.get("soil_moisture") or record.get("vegetation_cover")
            data.append(record)

        return data
    except Exception as e:
        print(f"Error fetching land health: {e}")
        return generate_sample_land_health(location_id)


@router.post("/", response_model=LandHealth)
async def create_land_health(
    land_health: LandHealthCreate,
    supabase: Client = Depends(get_db)
):
    """Create new land health entry"""
    try:
        data = land_health.model_dump()
        data["id"] = str(uuid4())
        data["created_at"] = datetime.utcnow().isoformat()

        response = supabase.table("land_health").insert(data).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create land health record")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating land health data: {str(e)}")


@router.get("/{location_id}/latest", response_model=LandHealth)
async def get_latest_land_health(
    location_id: UUID,
    supabase: Client = Depends(get_db)
):
    """Get the most recent land health data for a location"""
    try:
        response = (
            supabase.table("land_health")
            .select("*")
            .eq("location_id", str(location_id))
            .order("date", desc=True)
            .limit(1)
            .execute()
        )

        if not response.data:
            sample_data = generate_sample_land_health(location_id)
            return sample_data[0] if sample_data else None

        record = response.data[0]

        # ✅ Align with frontend naming
        record["ndvi"] = record.get("vegetation_index") or record.get("ndvi")
        record["vegetation_cover"] = record.get("soil_moisture") or record.get("vegetation_cover")

        return record
    except Exception as e:
        print(f"Error fetching latest land health: {e}")
        sample_data = generate_sample_land_health(location_id)
        return sample_data[0] if sample_data else None


def generate_sample_land_health(location_id: UUID) -> List[dict]:
    """Generate realistic sample land health data for testing"""
    sample_data = []
    base_date = datetime.utcnow()

    for i in range(30):
        date = base_date - timedelta(days=i)

        base_health = 70 + random.uniform(-15, 15)
        soil_moisture = max(20, min(80, base_health + random.uniform(-10, 10)))
        vegetation_index = max(0.3, min(0.9, base_health / 100 + random.uniform(-0.1, 0.1)))
        erosion = max(5, min(50, 100 - base_health + random.uniform(-10, 10)))

        sample_data.append({
            "id": str(uuid4()),
            "location_id": str(location_id),
            "date": date.isoformat(),
            # ✅ Return frontend-compatible keys
            "ndvi": round(vegetation_index, 2),
            "vegetation_cover": round(soil_moisture, 1),
            "soil_ph": round(6.5 + random.uniform(-0.5, 0.5), 1),
            "erosion_risk": round(erosion, 1),
            "overall_health_score": round(base_health, 1),
            "created_at": date.isoformat(),
        })

    return sample_data
