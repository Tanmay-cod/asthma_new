from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    age = Column(Integer)
    gender = Column(String)
    smoking = Column(String, default="never")  # never/former/current
    personal_best_pefr = Column(Float)  # user's own best PEFR (L/min)
    baseline_spo2 = Column(Float, default=97.0)
    baseline_pulse = Column(Float, default=75.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    readings = relationship("SensorReading", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    spo2 = Column(Float)          # %
    pulse = Column(Float)         # bpm
    temperature = Column(Float)   # C
    humidity = Column(Float)      # %
    dust = Column(Float)          # mg/m^3 (approx from GP2Y1010AU0F)
    pefr = Column(Float, nullable=True)  # L/min, manual
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="readings")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    risk_score = Column(Float)        # 0-100
    risk_level = Column(String)       # Low/Moderate/High
    shap_json = Column(Text)          # JSON string of feature contributions
    features_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")
