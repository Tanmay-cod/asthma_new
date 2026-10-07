import enum
from datetime import datetime

from sqlalchemy import (Column, Integer, Float, String, DateTime, ForeignKey,
                        Text, Boolean, Enum, Index)
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

    profile = relationship("Profile", back_populates="user", uselist=False)
    devices = relationship("Device", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String)
    date_of_birth = Column(DateTime, nullable=True)
    sex = Column(String, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    asthma_diagnosis_status = Column(String, nullable=True)  # CONFIRMED / SUSPECTED / UNKNOWN
    previous_exacerbations = Column(Integer, nullable=True)
    hospitalizations = Column(Integer, nullable=True)
    emergency_visits = Column(Integer, nullable=True)
    smoking_exposure = Column(String, nullable=True)
    preferred_units = Column(String, default="metric")
    baseline_pefr = Column(Float, nullable=True)  # user-reported personal best, L/min
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="profile")


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
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)


class DeviceStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    UNREGISTERED = "UNREGISTERED"


class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    device_code = Column(String, unique=True, index=True)  # e.g. ASTHMA-ESP8266-0001
    name = Column(String, nullable=True)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.UNREGISTERED)
    firmware_version = Column(String, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="devices")
    credentials = relationship("DeviceCredential", back_populates="device", uselist=False)


class DeviceCredential(Base):
    __tablename__ = "device_credentials"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"), unique=True)
    token_hash = Column(String, nullable=False)  # store hash, not plaintext
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)

    device = relationship("Device", back_populates="credentials")


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
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), index=True)
    session_id = Column(Integer, ForeignKey("measurement_sessions.id"), nullable=True, index=True)
    heart_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    heart_rate_valid = Column(Boolean, nullable=True)
    spo2_valid = Column(Boolean, nullable=True)
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    temperature_valid = Column(Boolean, nullable=True)
    humidity_valid = Column(Boolean, nullable=True)
    dust_indicator = Column(Float, nullable=True)
    dust_valid = Column(Boolean, nullable=True)
    wifi_rssi = Column(Float, nullable=True)
    recorded_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PefrReading(Base):
    __tablename__ = "pefr_readings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    pefr = Column(Float, nullable=False)  # L/min
    unit = Column(String, default="L/min")
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
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


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    model_version_id = Column(Integer, ForeignKey("model_versions.id"))
    probability = Column(Float)
    risk_category = Column(String)  # LOW / MODERATE / HIGH (configurable cutoffs)
    prediction_window = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class PredictionFeature(Base):
    __tablename__ = "prediction_features"
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey("risk_predictions.id"), index=True)
    feature_name = Column(String)
    feature_value = Column(Float)


class PredictionExplanation(Base):
    __tablename__ = "prediction_explanations"
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey("risk_predictions.id"), index=True)
    feature_name = Column(String)
    contribution = Column(Float)  # SHAP value
    explanation_version = Column(String, default="1.0.0")


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
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    event_type = Column(String)  # INVALID_RANGE / MISSING / STALE / SUSPECT
    detail = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
