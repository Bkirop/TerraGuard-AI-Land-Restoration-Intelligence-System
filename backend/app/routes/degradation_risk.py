from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List
from uuid import UUID
from datetime import datetime, timedelta
from app.database import get_db
from app.schemas import DegradationRisk

router = APIRouter()

@router.get("/{location_id}/latest", response_model=DegradationRisk)
async def get_latest_risk(location_id: UUID, supabase: Client = Depends(get_db)):
    """Fetch the latest degradation risk record"""
    try:
        response = (
            supabase.table("degradation_risk")
            .select("*")
            .eq("location_id", str(location_id))
            .order("assessment_date", desc=True)
            .limit(1)
            .execute()
        )

        if not response.data:
            return {"risk_type": "Unknown", "risk_score": None, "assessment_date": datetime.utcnow().isoformat()}

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching latest risk: {e}")


@router.get("/{location_id}/trend")
async def get_risk_trend(location_id: UUID, months: int = 6, supabase: Client = Depends(get_db)):
    """Fetch degradation risk trend data for the past X months"""
    try:
        since_date = (datetime.utcnow() - timedelta(days=30 * months)).isoformat()

        response = (
            supabase.table("degradation_risk")
            .select("*")
            .eq("location_id", str(location_id))
            .gte("assessment_date", since_date)
            .order("assessment_date", desc=True)
            .execute()
        )

        if not response.data:
            return {"message": "No risk trend data available", "trend": []}

        # Simplify response for frontend chart usage
        trend_data = [
            {
                "date": r["assessment_date"],
                "risk_score": r.get("risk_score", 0),
                "risk_type": r.get("risk_type", "Unknown"),
            }
            for r in response.data
        ]

        return {"trend": trend_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching risk trend: {e}")
