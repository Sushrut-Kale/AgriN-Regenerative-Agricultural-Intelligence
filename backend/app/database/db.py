"""
FarmFriend AI — Database Models & Connection
=============================================
SQLite with SQLAlchemy ORM. Includes Feedback System tables.
"""

import os
import uuid
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, Float, String,
    Boolean, DateTime, Text, JSON
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'backend', 'farmfriend.db')}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


class FarmerSession(Base):
    __tablename__ = "farmer_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, index=True)
    state = Column(String, default="Maharashtra")
    district = Column(String)
    season = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class SoilRecord(Base):
    __tablename__ = "soil_records"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    N = Column(Float, nullable=True)
    P = Column(Float, nullable=True)
    K = Column(Float, nullable=True)
    S = Column(Float, nullable=True)
    Zn = Column(Float, nullable=True)
    Fe = Column(Float, nullable=True)
    Cu = Column(Float, nullable=True)
    Mn = Column(Float, nullable=True)
    B = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    EC = Column(Float, nullable=True)
    OC = Column(Float, nullable=True)
    soil_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class EnvRecord(Base):
    __tablename__ = "env_records"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    model_version = Column(String, default="random_forest_v2")
    top_crop = Column(String)
    top_score = Column(Float)
    ranked_crops_json = Column(JSON)  # Full ranked list
    data_confidence = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class FeasibilityRecord(Base):
    __tablename__ = "feasibility_records"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    chosen_crop = Column(String)
    suitability_score = Column(Float)
    feasibility_outcome = Column(String)
    result_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)


class WhatIfRecord(Base):
    __tablename__ = "whatif_records"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    crop_name = Column(String)
    before_score = Column(Float)
    after_score = Column(Float)
    score_change = Column(Float)
    changed_params_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)


class FeedbackRecord(Base):
    __tablename__ = "feedback_records"

    id = Column(Integer, primary_key=True)
    feedback_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True)
    analysis_id = Column(String, nullable=True)
    recommended_crop = Column(String)
    selected_crop = Column(String, nullable=True)
    suitability_score = Column(Float, nullable=True)
    rating = Column(String)  # 'helpful', 'not_helpful', 'partially'
    reason = Column(String, nullable=True)
    free_text = Column(Text, nullable=True)
    outcome_status = Column(String, default="not_yet_grown")  # 'not_yet_grown', 'growing', 'harvested'
    crop_performance = Column(String, nullable=True)  # 'poor', 'average', 'good', 'excellent'
    actual_yield = Column(Float, nullable=True)
    yield_unit = Column(String, default="quintals_per_ha")
    model_version = Column(String, default="random_forest_v2")
    dataset_version = Column(String, default="v2.0")
    region = Column(String, nullable=True)
    season = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
