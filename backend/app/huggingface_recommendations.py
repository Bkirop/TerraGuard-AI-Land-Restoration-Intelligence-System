"""
HuggingFace AI Recommendation Service for TerraGuard AI
Generates land management recommendations using AI models
"""

import os
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

# Try to import HuggingFace Hub
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logger.warning("⚠️ huggingface_hub not installed. Install with: pip install huggingface_hub")


class HuggingFaceRecommendationService:
    """
    Service for generating AI-powered land management recommendations
    using HuggingFace Inference API
    """
    
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        """
        Initialize the HuggingFace recommendation service
        
        Args:
            model: HuggingFace model to use for generation
                   Popular options:
                   - mistralai/Mistral-7B-Instruct-v0.2 (default, good balance)
                   - mistralai/Mixtral-8x7B-Instruct-v0.1 (higher quality, slower)
                   - meta-llama/Llama-2-7b-chat-hf (good alternative)
                   - google/flan-t5-xxl (faster, structured output)
        """
        self.model = model
        self.client = None
        
        if not HF_AVAILABLE:
            logger.warning("⚠️ HuggingFace Hub not available. Recommendations will use rule-based fallback.")
            return
        
        # Get API token from environment
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_TOKEN")
        
        if not hf_token:
            logger.warning("⚠️ No HuggingFace API token found. Set HUGGINGFACE_API_TOKEN or HF_TOKEN in .env")
            logger.warning("Get your token at: https://huggingface.co/settings/tokens")
            return
        
        try:
            self.client = InferenceClient(token=hf_token)
            logger.info(f"✅ HuggingFace client initialized with model: {model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize HuggingFace client: {e}")
            self.client = None
    
    def generate_recommendations(
        self,
        location_data: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        land_health: Dict[str, Any],
        climate_forecast: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate AI-powered recommendations based on location data
        
        Args:
            location_data: Location information (name, coordinates, etc.)
            risk_assessment: Current risk assessment data
            land_health: Land health metrics (NDVI, vegetation cover, etc.)
            climate_forecast: Weather forecast data
            
        Returns:
            List of recommendation dictionaries
        """
        
        # If AI is not available, use rule-based fallback
        if not self.client:
            logger.info("📋 Using rule-based recommendations (AI not available)")
            return self._generate_rule_based_recommendations(
                location_data, risk_assessment, land_health, climate_forecast
            )
        
        try:
            # Build context for AI
            prompt = self._build_prompt(location_data, risk_assessment, land_health, climate_forecast)
            
            logger.info(f"🤖 Generating AI recommendations using {self.model}")
            logger.debug(f"Prompt: {prompt[:200]}...")
            
            # Call HuggingFace Inference API
            response = self.client.text_generation(
                prompt,
                model=self.model,
                max_new_tokens=800,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.1,
                do_sample=True
            )
            
            logger.info("✅ Received AI response")
            logger.debug(f"Raw response: {response[:200]}...")
            
            # Parse AI response into structured recommendations
            recommendations = self._parse_ai_response(response, risk_assessment)
            
            if not recommendations or len(recommendations) == 0:
                logger.warning("⚠️ AI generated no valid recommendations, falling back to rule-based")
                return self._generate_rule_based_recommendations(
                    location_data, risk_assessment, land_health, climate_forecast
                )
            
            logger.info(f"✅ Generated {len(recommendations)} AI-powered recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating AI recommendations: {e}")
            logger.exception("Full traceback:")
            logger.info("📋 Falling back to rule-based recommendations")
            return self._generate_rule_based_recommendations(
                location_data, risk_assessment, land_health, climate_forecast
            )
    
    def _build_prompt(
        self,
        location_data: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        land_health: Dict[str, Any],
        climate_forecast: List[Dict[str, Any]]
    ) -> str:
        """Build AI prompt from input data"""
        
        location_name = location_data.get("name", "Unknown Location")
        risk_level = risk_assessment.get("risk_level", "UNKNOWN")
        risk_score = risk_assessment.get("total_risk_score", 0)
        ndvi = land_health.get("ndvi", 0)
        veg_cover = land_health.get("vegetation_cover_pct", land_health.get("vegetation_cover", 0))
        
        # Calculate average temperature from forecast
        avg_temp = 0
        total_precip = 0
        if climate_forecast:
            temps = [f.get("temp_avg", f.get("temperature", 0)) for f in climate_forecast]
            precips = [f.get("precipitation", f.get("rainfall", 0)) for f in climate_forecast]
            avg_temp = sum(temps) / len(temps) if temps else 0
            total_precip = sum(precips) if precips else 0
        
        prompt = f"""You are an expert land management consultant specializing in land degradation prevention and restoration in Africa. Analyze the following data and provide 2-3 specific, actionable recommendations.

Location: {location_name}
Risk Level: {risk_level} (Score: {risk_score:.1f}/100)
Vegetation Index (NDVI): {ndvi:.3f}
Vegetation Cover: {veg_cover:.1f}%
Average Temperature (7-day): {avg_temp:.1f}°C
Total Precipitation (7-day): {total_precip:.1f}mm

Specific Risk Factors:
- Drought Risk: {risk_assessment.get('drought_risk', 0):.1f}
- Erosion Risk: {risk_assessment.get('erosion_risk', 0):.1f}
- Soil Degradation: {risk_assessment.get('soil_degradation_risk', 0):.1f}
- Vegetation Loss: {risk_assessment.get('vegetation_loss_risk', 0):.1f}

Provide 2-3 recommendations in the following JSON format only, no other text:
[
  {{
    "priority": "high|medium|low",
    "category": "restoration|irrigation|soil_management|vegetation|monitoring",
    "action_title": "Brief title (max 50 chars)",
    "action_description": "Detailed action plan (max 200 chars)",
    "urgency_hours": 168,
    "expected_risk_reduction": 15.5
  }}
]

Focus on practical, cost-effective actions suitable for African smallholder farmers."""

        return prompt
    
    def _parse_ai_response(self, response: str, risk_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AI response into structured recommendations"""
        
        try:
            # Try to find JSON array in response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("⚠️ No JSON array found in AI response")
                return []
            
            json_str = response[start_idx:end_idx]
            recommendations = json.loads(json_str)
            
            # Validate and clean recommendations
            cleaned = []
            for rec in recommendations:
                if not isinstance(rec, dict):
                    continue
                
                # Ensure required fields exist
                cleaned_rec = {
                    "priority": rec.get("priority", "medium").lower(),
                    "category": rec.get("category", "general"),
                    "action_title": rec.get("action_title", "")[:100],
                    "action_description": rec.get("action_description", "")[:500],
                    "urgency_hours": int(rec.get("urgency_hours", 168)),
                    "expected_risk_reduction": float(rec.get("expected_risk_reduction", 10.0)),
                    "expected_cost_usd": float(rec.get("expected_cost_usd", 0)),
                    "recommended_species": rec.get("recommended_species")
                }
                
                # Skip if missing critical info
                if not cleaned_rec["action_title"] or not cleaned_rec["action_description"]:
                    continue
                
                cleaned.append(cleaned_rec)
            
            return cleaned
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse AI response as JSON: {e}")
            logger.debug(f"Response: {response}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing AI response: {e}")
            return []
    
    def _generate_rule_based_recommendations(
        self,
        location_data: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        land_health: Dict[str, Any],
        climate_forecast: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations using rule-based logic
        (fallback when AI is not available)
        """
        
        recommendations = []
        risk_score = risk_assessment.get("total_risk_score", 50)
        risk_level = risk_assessment.get("risk_level", "MEDIUM")
        ndvi = land_health.get("ndvi", 0.5)
        veg_cover = land_health.get("vegetation_cover_pct", land_health.get("vegetation_cover", 50))
        drought_risk = risk_assessment.get("drought_risk", 0)
        erosion_risk = risk_assessment.get("erosion_risk", 0)
        
        # High risk - urgent intervention needed
        if risk_score >= 70 or risk_level == "CRITICAL":
            recommendations.append({
                "priority": "high",
                "category": "restoration",
                "action_title": "Urgent: Implement soil conservation measures",
                "action_description": "High degradation risk detected. Immediately establish contour bunds, plant cover crops, and restrict grazing to prevent further degradation.",
                "urgency_hours": 72,
                "expected_risk_reduction": 25.0,
                "expected_cost_usd": 500,
                "recommended_species": None
            })
        
        # Low vegetation - restoration needed
        if ndvi < 0.3 or veg_cover < 30:
            recommendations.append({
                "priority": "high",
                "category": "vegetation",
                "action_title": "Restore vegetation cover",
                "action_description": "Low vegetation detected (NDVI: {:.2f}). Plant native grass species and fast-growing trees. Consider agroforestry with Acacia or Moringa species.".format(ndvi),
                "urgency_hours": 168,
                "expected_risk_reduction": 20.0,
                "expected_cost_usd": 300,
                "recommended_species": [
                    {"name": "Acacia senegal", "type": "tree"},
                    {"name": "Vetiver grass", "type": "grass"}
                ]
            })
        
        # High drought risk - water conservation
        if drought_risk > 5:
            recommendations.append({
                "priority": "high",
                "category": "irrigation",
                "action_title": "Implement water conservation techniques",
                "action_description": "High drought risk detected. Install rainwater harvesting systems, apply mulching, and consider drip irrigation for critical crops.",
                "urgency_hours": 120,
                "expected_risk_reduction": 18.0,
                "expected_cost_usd": 400,
                "recommended_species": None
            })
        
        # High erosion risk - soil management
        if erosion_risk > 5:
            recommendations.append({
                "priority": "high",
                "category": "soil_management",
                "action_title": "Prevent soil erosion",
                "action_description": "High erosion risk detected. Establish terracing on slopes, plant windbreaks, and use cover crops to protect soil. Avoid bare soil during rainy season.",
                "urgency_hours": 96,
                "expected_risk_reduction": 22.0,
                "expected_cost_usd": 450,
                "recommended_species": [
                    {"name": "Leucaena leucocephala", "type": "tree"},
                    {"name": "Napier grass", "type": "grass"}
                ]
            })
        
        # Moderate risk - regular monitoring
        if risk_score >= 40 and risk_score < 70:
            recommendations.append({
                "priority": "medium",
                "category": "monitoring",
                "action_title": "Establish regular monitoring routine",
                "action_description": "Moderate risk level detected. Set up monthly soil and vegetation monitoring. Track rainfall and adjust management practices accordingly.",
                "urgency_hours": 168,
                "expected_risk_reduction": 15.0,
                "expected_cost_usd": 100,
                "recommended_species": None
            })
        
        # Low risk - maintenance
        if risk_score < 40:
            recommendations.append({
                "priority": "low",
                "category": "monitoring",
                "action_title": "Maintain current good practices",
                "action_description": "Land is in relatively good condition. Continue current management practices and monitor for any changes. Consider introducing nitrogen-fixing plants to improve soil fertility.",
                "urgency_hours": 336,
                "expected_risk_reduction": 10.0,
                "expected_cost_usd": 50,
                "recommended_species": [
                    {"name": "Sesbania sesban", "type": "tree"},
                    {"name": "Cowpea", "type": "crop"}
                ]
            })
        
        # Ensure we always return at least one recommendation
        if not recommendations:
            recommendations.append({
                "priority": "medium",
                "category": "general",
                "action_title": "Conduct comprehensive land assessment",
                "action_description": "Perform detailed soil testing, vegetation survey, and water availability assessment to develop targeted management plan.",
                "urgency_hours": 168,
                "expected_risk_reduction": 12.0,
                "expected_cost_usd": 200,
                "recommended_species": None
            })
        
        # Limit to top 3 recommendations
        return recommendations[:3]


# Utility function for testing
def test_service():
    """Test the recommendation service"""
    service = HuggingFaceRecommendationService()
    
    test_location = {"name": "Test Farm", "latitude": -1.2921, "longitude": 36.8219}
    test_risk = {
        "total_risk_score": 65.5,
        "risk_level": "HIGH",
        "drought_risk": 7.2,
        "erosion_risk": 5.8,
        "soil_degradation_risk": 4.5,
        "vegetation_loss_risk": 6.1
    }
    test_health = {
        "ndvi": 0.25,
        "vegetation_cover_pct": 22.5,
        "soil_moisture": 35,
        "overall_health_score": 45
    }
    test_forecast = [
        {"date": "2025-10-13", "temp_avg": 28, "precipitation": 2},
        {"date": "2025-10-14", "temp_avg": 29, "precipitation": 0},
        {"date": "2025-10-15", "temp_avg": 27, "precipitation": 5}
    ]
    
    recommendations = service.generate_recommendations(
        test_location, test_risk, test_health, test_forecast
    )
    
    print(f"\n✅ Generated {len(recommendations)} recommendations:\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec['priority'].upper()}] {rec['action_title']}")
        print(f"   {rec['action_description']}\n")


if __name__ == "__main__":
    test_service()