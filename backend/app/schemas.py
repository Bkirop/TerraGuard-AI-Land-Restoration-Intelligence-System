from datetime import datetime, date
from typing import List, Optional, Dict
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# ----------------------------
# Location Schemas
# ----------------------------
class LocationBase(BaseModel):
    name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    country: str
    region: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country: Optional[str] = None
    region: Optional[str] = None


class Location(LocationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CLIMATE DATA SCHEMAS
# ============================================================================

class ClimateDataBase(BaseModel):
    location_id: UUID
    date: date
    temperature: Optional[float] = None
    precipitation: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None

class ClimateDataCreate(ClimateDataBase):
    pass

class ClimateData(ClimateDataBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------
# Land Health Schemas
# ----------------------------
class LandHealthBase(BaseModel):
    location_id: UUID
    soil_moisture: float
    vegetation_index: float
    soil_ph: Optional[float] = None
    erosion_risk: float
    overall_health_score: float


class LandHealthCreate(LandHealthBase):
    pass


class LandHealth(LandHealthBase):
    id: UUID
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------
# Prediction Schemas
# ----------------------------
class PredictionBase(BaseModel):
    location_id: UUID
    target_date: datetime
    prediction_type: str
    predicted_value: float
    confidence_score: float
    model_version: Optional[str] = None


class PredictionCreate(PredictionBase):
    pass


class Prediction(PredictionBase):
    id: UUID
    prediction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------
# Recommendation Schemas
# ----------------------------
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, date
from uuid import UUID


class RecommendationBase(BaseModel):
    location_id: UUID
    risk_assessment_id: Optional[UUID] = None
    priority: str
    category: str
    action_title: str
    action_description: str
    recommended_start_date: Optional[date] = None
    recommended_end_date: Optional[date] = None
    urgency_hours: Optional[int] = None
    expected_risk_reduction: Optional[float] = None
    expected_cost_usd: Optional[float] = None
    recommended_species: Optional[Dict] = None
    status: Optional[str] = "pending"
    is_active: Optional[bool] = True

    model_config = {"protected_namespaces": ()}  # allows model_version-like fields elsewhere


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(BaseModel):
    priority: Optional[str] = None
    category: Optional[str] = None
    action_title: Optional[str] = None
    action_description: Optional[str] = None
    recommended_start_date: Optional[date] = None
    recommended_end_date: Optional[date] = None
    urgency_hours: Optional[int] = None
    expected_risk_reduction: Optional[float] = None
    expected_cost_usd: Optional[float] = None
    recommended_species: Optional[Dict] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class Recommendation(RecommendationBase):
    id: UUID
    created_at: datetime
    completed_at: Optional[datetime] = None

# ----------------------------
# Risk Assessment Schemas
# ----------------------------
class RiskAssessmentBase(BaseModel):
    location_id: UUID
    category: str
    risk_level: float
    risk_status: str
    factors: Optional[str] = None


class RiskAssessmentCreate(RiskAssessmentBase):
    pass


class RiskAssessment(RiskAssessmentBase):
    id: UUID
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------
# User Schemas
# ----------------------------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: UUID
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# ----------------------------
# Alert Schemas
# ----------------------------
class AlertBase(BaseModel):
    location_id: UUID
    alert_type: str
    title: str
    message: str
    severity: str = "medium"


class AlertCreate(AlertBase):
    pass


class Alert(AlertBase):
    id: UUID
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ----------------------------
# Dashboard Response Schema
# ----------------------------
class DashboardData(BaseModel):
    temperature: float
    precipitation: float
    landHealth: float
    riskLevel: str
    alerts: List[dict]


# ----------------------------
# API Response Schemas
# ----------------------------
class HealthResponse(BaseModel):
    status: str
    message: Optional[str] = None
