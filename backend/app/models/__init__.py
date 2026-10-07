import enum
from datetime import datetime

from sqlalchemy import (Column, Integer, Float, String, DateTime, ForeignKey,
                        Text, Boolean, Enum, Index, JSON)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Role(str, enum.Enum):
    PATIENT = "PATIENT"
    CLINICIAN = "CLINICIAN"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    supabase_id = Column(String, unique=True, index=True, nullable=True)  # auth identity
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(Enum(Role), default=Role.PATIENT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Profile(Base):
    """Maps the existing Supabase `profiles` table (live schema)."""
    __tablename__ = "profiles"
    id = Column(String, primary_key=True, default=lambda: str(__import__("uuid").uuid4()))  # uuid as string
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class MedicalHistory(Base):
    __tablename__ = "medical_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    condition = Column(String)
    onset_date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class Allergy(Base):
    __tablename__ = "allergies"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    allergen = Column(String)
    severity = Column(String, nullable=True)


class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String)
    type = Column(String, nullable=True)
    schedule = Column(String, nullable=True)
    active = Column(Boolean, default=True)


class Trigger(Base):
    __tablename__ = "triggers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String)  # dust, smoke, pollen, cold air, exercise, pets, ...


class Consent(Base):
    __tablename__ = "consents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    consent_type = Column(String)
    granted = Column(Boolean)
    granted_at = Column(DateTime, default=datetime.utcnow)


class SessionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MeasurementSession(Base):
    __tablename__ = "measurement_sessions"
    id = Column(String, primary_key=True, default=lambda: str(__import__("uuid").uuid4()))  # uuid
    user_id = Column(String, nullable=False, index=True)
    device_id = Column(String, ForeignKey("devices.id"), index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DeviceStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    UNREGISTERED = "UNREGISTERED"


class Device(Base):
    """Maps the existing Supabase `devices` table (shared device, no permanent user)."""
    __tablename__ = "devices"
    id = Column(String, primary_key=True, default=lambda: str(__import__("uuid").uuid4()))  # uuid as string
    device_code = Column(String, unique=True, index=True)
    device_name = Column(String, nullable=True)
    device_token_hash = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_seen_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class SensorType(str, enum.Enum):
    SPO2 = "spo2"
    HEART_RATE = "heart_rate"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    DUST = "dust"


class DataQuality(str, enum.Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    MISSING = "MISSING"
    STALE = "STALE"
    SUSPECT = "SUSPECT"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"


class SensorReading(Base):
    """Maps the Supabase sensor_readings table (wide row per reading)."""
    __tablename__ = "sensor_readings"
    id = Column(String, primary_key=True, default=lambda: str(__import__("uuid").uuid4()))  # uuid
    session_id = Column(String, ForeignKey("measurement_sessions.id"), nullable=True, index=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=True, index=True)
    heart_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    heart_rate_valid = Column(Boolean, nullable=False, default=False)
    spo2_valid = Column(Boolean, nullable=False, default=False)
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    temperature_valid = Column(Boolean, nullable=False, default=False)
    humidity_valid = Column(Boolean, nullable=False, default=False)
    dust_indicator = Column(Float, nullable=True)
    dust_valid = Column(Boolean, nullable=False, default=False)
    wifi_rssi = Column(Integer, nullable=True)
    recorded_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PefrReading(Base):
    __tablename__ = "pef_readings"
    id = Column(String, primary_key=True, default=lambda: str(__import__("uuid").uuid4()))  # uuid
    user_id = Column(String, nullable=False, index=True)
    pef_l_min = Column(Float, nullable=False)
    personal_best_l_min = Column(Float, nullable=True)
    recorded_at = Column(DateTime, nullable=False, index=True)
    source = Column(String, default="manual")
    created_at = Column(DateTime, default=datetime.utcnow)


class SymptomAssessment(Base):
    __tablename__ = "symptom_assessments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    cough = Column(Integer)          # 0-3 prototype severity, NOT a validated score
    wheezing = Column(Integer)
    shortness_of_breath = Column(Integer)
    chest_tightness = Column(Integer)
    night_symptoms = Column(Boolean)
    exercise_limitation = Column(Boolean)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class EnvironmentalReading(Base):
    __tablename__ = "environmental_readings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    dust = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class PersonalBaseline(Base):
    __tablename__ = "personal_baselines"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    metric = Column(String)  # pefr, heart_rate, spo2, ...
    baseline_value = Column(Float)
    baseline_period_start = Column(DateTime)
    baseline_period_end = Column(DateTime)
    observation_count = Column(Integer)
    quality = Column(String)  # e.g. sufficient / insufficient
    calculation_version = Column(String, default="1.0.0")
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(String)
    feature_schema_version = Column(String)
    training_dataset_version = Column(String, nullable=True)
    training_date = Column(DateTime, nullable=True)
    is_development_model = Column(Boolean, default=True)  # True => NOT clinically validated
    artifact_path = Column(String, nullable=True)


class Prediction(Base):
    """Maps the existing Supabase `predictions` table."""
    __tablename__ = "predictions"
    id = Column(String, primary_key=True, default=lambda: str(__import__("uuid").uuid4()))  # uuid
    user_id = Column(String, nullable=False, index=True)
    pef_reading_id = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    prediction_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    data_quality = Column(String, nullable=True)
    explanation = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    text = Column(Text)
    trigger_factor = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    type = Column(String)  # HIGH_RISK / OFFLINE / DATA_QUALITY / EMERGENCY_SIGNAL
    message = Column(Text)
    channel = Column(String, nullable=True)  # telegram / email / in_app
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    actor = Column(String)  # user id / device id / system
    action = Column(String)
    resource = Column(String)
    result = Column(String)  # SUCCESS / FAILURE
    detail = Column(Text, nullable=True)


class DataQualityEvent(Base):
    __tablename__ = "data_quality_events"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=True)
    event_type = Column(String)  # INVALID_RANGE / MISSING / STALE / SUSPECT
    detail = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
