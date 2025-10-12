"""
Degradation Risk Calculation and Claude AI Integration
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
import logging
import os
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# ============================================================================
# DEGRADATION RISK CALCULATOR
# ============================================================================

class DegradationRiskCalculator:
    """
    Calculate land degradation risk from multiple factors
    """
    
    @staticmethod
    def calculate_risk(
        climate_data: List[Dict],
        land_health: Dict,
        location_data: Dict
    ) -> Dict:
        """
        Calculate comprehensive degradation risk
        
        Args:
            climate_data: Recent and forecast climate data
            land_health: Current land health metrics
            location_data: Location information (slope, etc.)
            
        Returns:
            Risk assessment with scores and factors
        """
        risk_factors = {}
        
        # 1. DROUGHT RISK (0-100)
        drought_risk = DegradationRiskCalculator._calculate_drought_risk(climate_data)
        risk_factors['drought'] = drought_risk
        
        # 2. EROSION RISK (0-100)
        erosion_risk = DegradationRiskCalculator._calculate_erosion_risk(
            climate_data, land_health, location_data
        )
        risk_factors['erosion'] = erosion_risk
        
        # 3. SOIL DEGRADATION RISK (0-100)
        soil_risk = DegradationRiskCalculator._calculate_soil_degradation_risk(
            land_health, climate_data
        )
        risk_factors['soil_degradation'] = soil_risk
        
        # 4. VEGETATION LOSS RISK (0-100)
        veg_risk = DegradationRiskCalculator._calculate_vegetation_risk(
            land_health, climate_data
        )
        risk_factors['vegetation_loss'] = veg_risk
        
        # 5. TEMPERATURE STRESS RISK (0-100)
        temp_risk = DegradationRiskCalculator._calculate_temperature_stress(climate_data)
        risk_factors['temperature_stress'] = temp_risk
        
        # 6. WATER SCARCITY RISK (0-100)
        water_risk = DegradationRiskCalculator._calculate_water_scarcity(
            climate_data, land_health
        )
        risk_factors['water_scarcity'] = water_risk
        
        # Calculate weighted total risk
        weights = {
            'drought': 0.25,
            'erosion': 0.20,
            'soil_degradation': 0.20,
            'vegetation_loss': 0.15,
            'temperature_stress': 0.10,
            'water_scarcity': 0.10
        }
        
        total_risk = sum(
            risk_factors[factor] * weights[factor]
            for factor in weights
        )
        
        # Determine risk level
        risk_level = DegradationRiskCalculator._classify_risk_level(total_risk)
        
        # Identify critical factors
        critical_factors = [
            factor for factor, score in risk_factors.items()
            if score >= 70
        ]
        
        return {
            'total_risk_score': round(total_risk, 2),
            'risk_level': risk_level,
            'drought_risk': round(risk_factors['drought'], 2),
            'erosion_risk': round(risk_factors['erosion'], 2),
            'soil_degradation_risk': round(risk_factors['soil_degradation'], 2),
            'vegetation_loss_risk': round(risk_factors['vegetation_loss'], 2),
            'temperature_stress_risk': round(risk_factors['temperature_stress'], 2),
            'water_scarcity_risk': round(risk_factors['water_scarcity'], 2),
            'risk_factors': {
                'critical_factors': critical_factors,
                'primary_threat': max(risk_factors, key=risk_factors.get),
                'trend': DegradationRiskCalculator._determine_trend(land_health)
            },
            'assessment_date': datetime.now().date().isoformat()
        }
    
    @staticmethod
    def _calculate_drought_risk(climate_data: List[Dict]) -> float:
        """Calculate drought risk from rainfall data"""
        if not climate_data:
            return 50.0  # Default moderate risk
        
        # Get forecast rainfall (next 30 days)
        forecast = [d for d in climate_data if d.get('is_forecast', False)][:30]
        
        if not forecast:
            return 50.0
        
        total_rainfall = sum(d.get('precipitation', 0) for d in forecast)
        
        # Risk thresholds (mm per month)
        if total_rainfall < 20:
            risk = 100  # Severe drought
        elif total_rainfall < 50:
            risk = 80  # High drought risk
        elif total_rainfall < 100:
            risk = 60  # Moderate risk
        elif total_rainfall < 150:
            risk = 30  # Low risk
        else:
            risk = 10  # Very low risk
        
        return float(risk)
    
    @staticmethod
    def _calculate_erosion_risk(
        climate_data: List[Dict],
        land_health: Dict,
        location_data: Dict
    ) -> float:
        """Calculate erosion risk"""
        risk = 0.0
        
        # Factor 1: Heavy rainfall forecast
        forecast = [d for d in climate_data if d.get('is_forecast', False)][:7]
        max_daily_rain = max((d.get('precipitation', 0) for d in forecast), default=0)
        
        if max_daily_rain > 50:
            risk += 40
        elif max_daily_rain > 30:
            risk += 25
        elif max_daily_rain > 15:
            risk += 10
        
        # Factor 2: Vegetation cover
        veg_cover = land_health.get('vegetation_cover_pct', 50)
        if veg_cover < 20:
            risk += 30
        elif veg_cover < 40:
            risk += 20
        elif veg_cover < 60:
            risk += 10
        
        # Factor 3: Slope
        slope = land_health.get('slope_degrees', location_data.get('slope', 5))
        if slope > 20:
            risk += 20
        elif slope > 10:
            risk += 10
        elif slope > 5:
            risk += 5
        
        # Factor 4: Current erosion score
        current_erosion = land_health.get('erosion_risk_score', 0)
        risk += current_erosion * 0.1
        
        return min(risk, 100.0)
    
    @staticmethod
    def _calculate_soil_degradation_risk(land_health: Dict, climate_data: List[Dict]) -> float:
        """Calculate soil degradation risk"""
        risk = 0.0
        
        # Factor 1: NDVI (vegetation health indicator)
        ndvi = land_health.get('ndvi', 0.5)
        if ndvi < 0.2:
            risk += 40
        elif ndvi < 0.4:
            risk += 25
        elif ndvi < 0.6:
            risk += 10
        
        # Factor 2: Soil moisture
        soil_moisture = land_health.get('soil_moisture', 20)
        if soil_moisture < 10:
            risk += 30
        elif soil_moisture < 15:
            risk += 20
        elif soil_moisture < 20:
            risk += 10
        
        # Factor 3: Temperature extremes
        forecast = [d for d in climate_data if d.get('is_forecast', False)][:7]
        max_temp = max((d.get('temp_max', 25) for d in forecast), default=25)
        
        if max_temp > 35:
            risk += 20
        elif max_temp > 30:
            risk += 10
        
        # Factor 4: Bare soil percentage
        bare_soil = land_health.get('bare_soil_pct', 30)
        risk += bare_soil * 0.2
        
        return min(risk, 100.0)
    
    @staticmethod
    def _calculate_vegetation_risk(land_health: Dict, climate_data: List[Dict]) -> float:
        """Calculate vegetation loss risk"""
        risk = 0.0
        
        # Factor 1: Current NDVI status
        ndvi = land_health.get('ndvi', 0.5)
        if ndvi < 0.3:
            risk += 50
        elif ndvi < 0.5:
            risk += 30
        
        # Factor 2: NDVI trend
        ndvi_trend = land_health.get('ndvi_trend', 0)
        if ndvi_trend < -10:
            risk += 30
        elif ndvi_trend < -5:
            risk += 20
        elif ndvi_trend < 0:
            risk += 10
        
        # Factor 3: Drought conditions
        drought_risk = DegradationRiskCalculator._calculate_drought_risk(climate_data)
        risk += drought_risk * 0.2
        
        return min(risk, 100.0)
    
    @staticmethod
    def _calculate_temperature_stress(climate_data: List[Dict]) -> float:
        """Calculate temperature stress risk"""
        forecast = [d for d in climate_data if d.get('is_forecast', False)][:7]
        
        if not forecast:
            return 20.0
        
        # Count days above threshold
        days_above_32 = sum(1 for d in forecast if d.get('temp_max', 0) > 32)
        days_above_35 = sum(1 for d in forecast if d.get('temp_max', 0) > 35)
        
        risk = (days_above_32 * 10) + (days_above_35 * 15)
        
        return min(risk, 100.0)
    
    @staticmethod
    def _calculate_water_scarcity(climate_data: List[Dict], land_health: Dict) -> float:
        """Calculate water scarcity risk"""
        # Combine rainfall deficit and soil moisture
        drought_risk = DegradationRiskCalculator._calculate_drought_risk(climate_data)
        
        soil_moisture = land_health.get('soil_moisture', 20)
        moisture_risk = (30 - soil_moisture) * 3 if soil_moisture < 30 else 0
        
        risk = (drought_risk * 0.6) + (moisture_risk * 0.4)
        
        return min(risk, 100.0)
    
    @staticmethod
    def _classify_risk_level(score: float) -> str:
        """Classify risk level from score"""
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MODERATE'
        else:
            return 'LOW'
    
    @staticmethod
    def _determine_trend(land_health: Dict) -> str:
        """Determine if conditions are improving or worsening"""
        ndvi_trend = land_health.get('ndvi_trend', 0)
        
        if ndvi_trend > 5:
            return 'improving'
        elif ndvi_trend < -5:
            return 'worsening'
        else:
            return 'stable'