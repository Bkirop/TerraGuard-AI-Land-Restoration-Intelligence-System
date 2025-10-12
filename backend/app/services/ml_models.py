"""
Machine Learning models for predictions
"""
import numpy as np
from typing import Dict, List


class DegradationPredictor:
    """ML model for land degradation prediction"""
    
    def predict_risk_score(self, features: Dict) -> float:
        """
        Predict degradation risk score (0-100)
        In production, this would use trained XGBoost/LSTM models
        """
        # Feature extraction
        ndvi = features.get("ndvi", 0.5)
        vegetation_cover = features.get("vegetation_cover", 50)
        soil_carbon = features.get("soil_organic_carbon", 2.0)
        precipitation = features.get("avg_precipitation", 100)
        temperature = features.get("avg_temperature", 25)
        
        # Simple risk calculation (replace with trained model)
        ndvi_score = (1 - ndvi) * 30  # Lower NDVI = higher risk
        cover_score = (100 - vegetation_cover) * 0.25
        carbon_score = max(0, (3 - soil_carbon) * 10)
        climate_score = abs(temperature - 20) * 1.5
        
        risk_score = ndvi_score + cover_score + carbon_score + climate_score
        
        return round(min(100, max(0, risk_score)), 2)
    
    def classify_risk_level(self, risk_score: float) -> str:
        """Classify risk level from score"""
        if risk_score < 30:
            return "low"
        elif risk_score < 60:
            return "moderate"
        elif risk_score < 80:
            return "high"
        else:
            return "critical"
    
    def identify_risk_factors(self, features: Dict) -> List[str]:
        """Identify key risk factors"""
        factors = []
        
        if features.get("ndvi", 1) < 0.3:
            factors.append("Very low vegetation index")
        if features.get("vegetation_cover", 100) < 30:
            factors.append("Sparse vegetation cover")
        if features.get("soil_organic_carbon", 5) < 1.5:
            factors.append("Poor soil quality")
        if features.get("erosion_risk") == "high":
            factors.append("High erosion risk")
        
        return factors