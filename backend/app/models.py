from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, Text, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

# ----------------------------
# LOCATION MODEL
# ----------------------------
class Location(Base):
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    country = Column(String, nullable=False)
    region = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    climate_data = relationship("ClimateData", back_populates="location", cascade="all, delete-orphan")
    land_health_data = relationship("LandHealth", back_populates="location", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="location", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="location", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="location", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="location", cascade="all, delete-orphan")


# ----------------------------
# CLIMATE DATA MODEL
# ----------------------------
class ClimateData(Base):
    __tablename__ = "climate_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    temperature = Column(Float)  # in Celsius
    precipitation = Column(Float)  # in mm
    humidity = Column(Float)  # percentage
    wind_speed = Column(Float, nullable=True)  # in km/h
    created_at = Column(DateTime, default=datetime.utcnow)

    location = relationship("Location", back_populates="climate_data")


# ----------------------------
# LAND HEALTH MODEL
# ----------------------------
class LandHealth(Base):
    __tablename__ = "land_health"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    soil_moisture = Column(Float)
    vegetation_index = Column(Float)
    soil_ph = Column(Float, nullable=True)
    erosion_risk = Column(Float)
    overall_health_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    location = relationship("Location", back_populates="land_health_data")


# ----------------------------
# PREDICTION MODEL
# ----------------------------
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    prediction_date = Column(DateTime, default=datetime.utcnow)
    target_date = Column(DateTime, nullable=False)
    prediction_type = Column(String)
    predicted_value = Column(Float)
    confidence_score = Column(Float)
    model_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    location = relationship("Location", back_populates="predictions")


# ----------------------------
# RECOMMENDATION MODEL
# ----------------------------
class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="medium")
    action = Column(Text, nullable=True)
    expected_impact = Column(String, nullable=True)
    category = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    location = relationship("Location", back_populates="recommendations")


# ----------------------------
# RISK ASSESSMENT MODEL
# ----------------------------
class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    category = Column(String, nullable=False)
    risk_level = Column(Float)
    risk_status = Column(String)
    factors = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    location = relationship("Location", back_populates="risk_assessments")


# ----------------------------
# USER MODEL
# ----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


# ----------------------------
# ALERT MODEL
# ----------------------------
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, default="medium")
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    location = relationship("Location", back_populates="alerts")
