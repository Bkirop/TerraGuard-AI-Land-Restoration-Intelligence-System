

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from app.database import get_db
from app.schemas import Recommendation, RecommendationCreate, RecommendationUpdate

router = APIRouter()


@router.get("/{location_id}", response_model=List[Recommendation])
async def get_recommendations(
    location_id: UUID,  # ✅ changed from int → UUID
    supabase: Client = Depends(get_db)
):
    """Get active recommendations for a specific location"""
    try:
        response = (
            supabase.table('recommendations')
            .select("*")
            .eq('location_id', str(location_id))  # ✅ Supabase expects UUID as string
            .eq('is_active', True)
            .order('priority', desc=True)
            .order('created_at', desc=True)
            .execute()
        )

        if not response.data:
            return generate_sample_recommendations(location_id)

        return response.data
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return generate_sample_recommendations(location_id)


@router.post("/", response_model=Recommendation)
async def create_recommendation(
    recommendation: RecommendationCreate,
    supabase: Client = Depends(get_db)
):
    """Create a new recommendation"""
    try:
        # Convert UUIDs to strings before sending to Supabase
        data = recommendation.model_dump()
        data["id"] = str(uuid4())  # ✅ generate new UUID if not provided
        if "location_id" in data:
            data["location_id"] = str(data["location_id"])

        response = supabase.table('recommendations').insert(data).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create recommendation")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating recommendation: {str(e)}")


@router.put("/{recommendation_id}", response_model=Recommendation)
async def update_recommendation(
    recommendation_id: UUID,  # ✅ changed from int → UUID
    recommendation: RecommendationUpdate,
    supabase: Client = Depends(get_db)
):
    """Update a recommendation"""
    try:
        update_data = recommendation.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")

        response = (
            supabase.table('recommendations')
            .update(update_data)
            .eq('id', str(recommendation_id))  # ✅ cast UUID to string
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating recommendation: {str(e)}")


@router.delete("/{recommendation_id}")
async def delete_recommendation(
    recommendation_id: UUID,  # ✅ changed from int → UUID
    supabase: Client = Depends(get_db)
):
    """Delete a recommendation"""
    try:
        response = (
            supabase.table('recommendations')
            .delete()
            .eq('id', str(recommendation_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        return {"message": "Recommendation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting recommendation: {str(e)}")



def generate_sample_recommendations(location_id: str) -> List[dict]:
    """Generate sample recommendations aligned with schema (UUID-based)."""
    now = datetime.utcnow()

    return [
        {
            "id": str(uuid.uuid4()),
            "location_id": location_id,
            "risk_assessment_id": None,
            "priority": "high",
            "category": "irrigation",
            "action_title": "Implement Water Conservation",
            "action_description": "Soil moisture levels are below optimal. Use water-efficient irrigation systems to conserve water.",
            "recommended_start_date": now.date().isoformat(),
            "recommended_end_date": (now + timedelta(days=14)).date().isoformat(),
            "urgency_hours": 48,
            "expected_risk_reduction": 0.35,
            "expected_cost_usd": 1200.0,
            "recommended_species": {"plants": ["Mulberry", "Vetiver grass"]},
            "status": "pending",
            "is_active": True,
            "created_at": now.isoformat(),
            "completed_at": None,
        },
        {
            "id": str(uuid.uuid4()),
            "location_id": location_id,
            "risk_assessment_id": None,
            "priority": "medium",
            "category": "soil",
            "action_title": "Apply Lime to Adjust Soil pH",
            "action_description": "Soil tests indicate acidity. Apply agricultural lime to restore pH balance and enhance nutrient uptake.",
            "recommended_start_date": now.date().isoformat(),
            "recommended_end_date": (now + timedelta(days=7)).date().isoformat(),
            "urgency_hours": 72,
            "expected_risk_reduction": 0.25,
            "expected_cost_usd": 600.0,
            "recommended_species": None,
            "status": "pending",
            "is_active": True,
            "created_at": now.isoformat(),
            "completed_at": None,
        },
        {
            "id": str(uuid.uuid4()),
            "location_id": location_id,
            "risk_assessment_id": None,
            "priority": "low",
            "category": "monitoring",
            "action_title": "Increase Vegetation Monitoring",
            "action_description": "Monitor vegetation cover biweekly to detect early signs of degradation or erosion.",
            "recommended_start_date": now.date().isoformat(),
            "recommended_end_date": (now + timedelta(days=30)).date().isoformat(),
            "urgency_hours": 168,
            "expected_risk_reduction": 0.15,
            "expected_cost_usd": 300.0,
            "recommended_species": None,
            "status": "pending",
            "is_active": True,
            "created_at": now.isoformat(),
            "completed_at": None,
        },
    ]


