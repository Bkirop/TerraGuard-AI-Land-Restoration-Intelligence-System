
"""
Degradation risk calculation service
"""
from datetime import datetime
from typing import Dict
from app.database import supabase
from app.services.ml_models import DegradationPredictor


class DegradationRiskCalculator:
    """Calculate land degradation risk"""

    def __init__(self):
        self.predictor = DegradationPredictor()

    async def calculate_risk(self, location_id: int) -> Dict:
        """Calculate comprehensive degradation risk"""
        # Gather all relevant data
        features = await self._gather_features(location_id)

        # Predict risk
        risk_score = self.predictor.predict_risk_score(features)
        risk_level = self.predictor.classify_risk_level(risk_score)
        risk_factors = self.predictor.identify_risk_factors(features)

        return {
            "location_id": location_id,
            "assessment_date": datetime.now().date().isoformat(),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "factors": {
                "primary_concerns": risk_factors,
                "metrics": features
            }
        }

    async def _gather_features(self, location_id: int) -> Dict:
        """Gather all features for risk calculation"""
        features = {}

        # Get latest land health
        health = supabase.table("land_health").select("*")\
            .eq("location_id", location_id)\
            .order("assessment_date", desc=True)\
            .limit(1)\
            .execute()

        if health.data:
            h = health.data[0]
            features.update({
                "ndvi": h.get("ndvi", 0.5),
                "vegetation_cover": h.get("vegetation_cover", 50),
                "soil_organic_carbon": h.get("soil_organic_carbon", 2.0),
                "erosion_risk": h.get("erosion_risk", "moderate")
            })

        # Get recent climate data
        climate = supabase.table("climate_data").select("*")\
            .eq("location_id", location_id)\
            .order("date", desc=True)\
            .limit(30)\
            .execute()

        if climate.data:
            temps = [c["temperature"] for c in climate.data if c.get("temperature")]
            precips = [c["precipitation"] for c in climate.data if c.get("precipitation")]

            if temps:
                features["avg_temperature"] = sum(temps) / len(temps)
            if precips:
                features["avg_precipitation"] = sum(precips) / len(precips)

        return features