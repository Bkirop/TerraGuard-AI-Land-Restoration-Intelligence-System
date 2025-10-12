from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import random

from app.database import get_db
from app.schemas import Prediction, PredictionCreate

router = APIRouter()


@router.get("/{location_id}", response_model=List[Prediction])
async def get_predictions(
    location_id: UUID,  # ✅ changed from int → UUID
    supabase: Client = Depends(get_db)
):
    """Get predictions for a specific location"""
    try:
        response = (
            supabase.table('predictions')
            .select("*")
            .eq('location_id', str(location_id))  # ✅ UUID → string for Supabase
            .order('target_date', desc=True)
            .limit(10)
            .execute()
        )

        if not response.data:
            return generate_sample_predictions(location_id)

        return response.data
    except Exception as e:
        print(f"Error fetching predictions: {e}")
        return generate_sample_predictions(location_id)


@router.post("/", response_model=Prediction)
async def create_prediction(
    prediction: PredictionCreate,
    supabase: Client = Depends(get_db)
):
    """Create a new prediction"""
    try:
        data = prediction.model_dump()
        data["id"] = str(uuid4())  # ✅ Ensure UUID primary key
        data["location_id"] = str(data["location_id"])  # ✅ Cast to string

        response = supabase.table('predictions').insert(data).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create prediction")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating prediction: {str(e)}")


@router.get("/{location_id}/latest", response_model=Prediction)
async def get_latest_prediction(
    location_id: UUID,  # ✅ changed from int → UUID
    prediction_type: str,
    supabase: Client = Depends(get_db)
):
    """Get the latest prediction of a specific type for a location"""
    try:
        response = (
            supabase.table('predictions')
            .select("*")
            .eq('location_id', str(location_id))  # ✅ UUID → string
            .eq('prediction_type', prediction_type)
            .order('prediction_date', desc=True)
            .limit(1)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="No predictions found")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching prediction: {str(e)}")


def generate_sample_predictions(location_id: UUID) -> List[dict]:
    """Generate sample predictions for testing"""
    sample_predictions = []
    base_date = datetime.utcnow()

    prediction_types = [
        ("temperature", 25.0, 5.0),
        ("precipitation", 30.0, 20.0),
        ("risk_level", 45.0, 25.0)
    ]

    for pred_type, base_value, variance in prediction_types:
        for j in range(7):  # 7 days of predictions
            target_date = base_date + timedelta(days=j + 1)
            sample_predictions.append({
                "id": str(uuid4()),  # ✅ Use UUID for sample data
                "location_id": str(location_id),
                "prediction_date": base_date.isoformat(),
                "target_date": target_date.isoformat(),
                "prediction_type": pred_type,
                "predicted_value": round(base_value + random.uniform(-variance, variance), 2),
                "confidence_score": round(random.uniform(0.7, 0.95), 2),
                "model_version": "v1.0",
                "created_at": base_date.isoformat()
            })

    return sample_predictions
