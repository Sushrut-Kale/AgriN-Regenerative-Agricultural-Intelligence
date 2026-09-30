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
    country = Column(String, default="India")
    state = Column(String, default="Maharashtra")
    district = Column(String)
    sub_district = Column(String, nullable=True)  # Taluka / Tehsil / Block
    village = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    area_hectares = Column(Float, nullable=True)
    boundary_geojson = Column(JSON, nullable=True)
    agro_climatic_zone = Column(String, nullable=True)
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


class FarmObservationRecord(Base):
    __tablename__ = "farm_observations"

    id = Column(Integer, primary_key=True)
    observation_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String, index=True)  # session_id or registered farm UUID
    timestamp = Column(DateTime, default=datetime.now, index=True)
    observation_type = Column(String, index=True)  # SOIL, WEATHER, CROP, SATELLITE, DISEASE, IRRIGATION, FIELD_VISIT
    parameter_name = Column(String, index=True)
    value = Column(Float)
    unit = Column(String)
    source = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class AdvisoryRecord(Base):
    __tablename__ = "agricultural_advisories"

    id = Column(Integer, primary_key=True)
    advisory_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    farm_id = Column(String, index=True)
    category = Column(String, index=True)  # CROP_SELECTION, SOIL_HEALTH, REGENERATIVE, etc.
    priority = Column(String, default="MEDIUM")
    title = Column(String)
    recommendation = Column(Text)
    reasoning_json = Column(JSON, nullable=True)
    supporting_observations_json = Column(JSON, nullable=True)
    actions_json = Column(JSON, nullable=True)
    confidence_json = Column(JSON, nullable=True)
    data_sources_json = Column(JSON, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class AdvisoryFeedbackRecord(Base):
    __tablename__ = "advisory_feedback"

    id = Column(Integer, primary_key=True)
    feedback_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    advisory_id = Column(String, index=True)
    farm_id = Column(String, index=True)
    action_taken = Column(String)  # accepted, rejected, partially_followed, not_applicable
    outcome = Column(String, default="unknown")  # outcome_positive, outcome_negative, unknown
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


def init_db():
    """Create all tables and perform non-destructive schema migrations."""
    Base.metadata.create_all(bind=engine)
    
    # Non-destructive migration for newly added geographic and boundary columns in existing SQLite DB
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        if "farmer_sessions" in inspector.get_table_names():
            existing_cols = {col["name"] for col in inspector.get_columns("farmer_sessions")}
            new_columns = [
                ("country", "TEXT DEFAULT 'India'"),
                ("sub_district", "TEXT"),
                ("village", "TEXT"),
                ("latitude", "REAL"),
                ("longitude", "REAL"),
                ("area_hectares", "REAL"),
                ("boundary_geojson", "TEXT"),
                ("agro_climatic_zone", "TEXT"),
            ]
            with engine.connect() as conn:
                for col_name, col_type in new_columns:
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE farmer_sessions ADD COLUMN {col_name} {col_type}"))
                conn.commit()
    except Exception as e:
        print(f"Notice: Non-destructive DB migration check: {e}")


def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
