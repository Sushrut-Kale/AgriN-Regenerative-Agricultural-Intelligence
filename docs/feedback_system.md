# FarmFriend AI — Feedback System & Closed-Loop ML Architecture

**Document Version**: 2.0  
**Updated**: 2026-08-13  
**Status**: Implemented / Active

---

## 1. Objectives & Safety Principles

The FarmFriend AI Feedback System provides farmers with a simple mechanism to rate recommendation usefulness and report actual crop performance, while ensuring that user feedback **never corrupts or poison the active production machine learning model**.

### Strict Safety Rules
1. **Zero Auto-Retraining**: Production ML models MUST NOT auto-update or retrain immediately upon receiving single user votes.
2. **Multi-Stage Feedback Validation**: User feedback passes through `raw` -> `aggregated` -> `verified` stages before candidate model evaluation.
3. **Privacy by Design**: No personal identification, Aadhaar numbers, or financial details are collected. Feedback records store only technical UUIDs, inputs, ratings, and optional agronomic outcomes.

---

## 2. Feedback Workflow & Pipeline Architecture

```
FARMER INTERFACE (👍 / 👎 / Crop Outcome)
       │
       ▼
POST /api/feedback  ──────► Database (SQLite / Postgres)
                              [FeedbackRecord Table]
                                      │
                                      ▼
                        Data Governance & Verification
                                      │
                         Is feedback validated by
                         agronomic experts / KVK?
                         /                        \
                      YES                          NO
                       │                            │
                       ▼                            ▼
         `data/feedback/validated/`     `data/feedback/rejected/`
                       │                            │
                       ▼                            └── (Stored for auditing)
       Candidate Retraining Pipeline
                       │
       Benchmark vs Current Production Model
                       │
       Passes Evaluation Thresholds?
                      /             \
                   YES               NO
                    │                 │
                    ▼                 ▼
          Deploy New Model     Keep Production Model
```

---

## 3. Database Schema (`backend/app/database/db.py`)

```sql
CREATE TABLE feedback_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id VARCHAR UNIQUE NOT NULL,
    session_id VARCHAR NOT NULL,
    analysis_id VARCHAR,
    recommended_crop VARCHAR NOT NULL,
    selected_crop VARCHAR,
    suitability_score FLOAT,
    rating VARCHAR NOT NULL,               -- 'helpful', 'not_helpful', 'partially'
    reason VARCHAR,                        -- 'soil_mismatch', 'weather_issue', 'market', etc.
    free_text TEXT,
    outcome_status VARCHAR DEFAULT 'not_yet_grown', -- 'not_yet_grown', 'growing', 'harvested'
    crop_performance VARCHAR,              -- 'poor', 'average', 'good', 'excellent'
    actual_yield FLOAT,                    -- Yield in quintals/ha or kg/acre
    yield_unit VARCHAR DEFAULT 'quintals_per_ha',
    model_version VARCHAR NOT NULL,
    dataset_version VARCHAR NOT NULL,
    region VARCHAR,
    season VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. REST API Endpoint Specifications

### 4.1 Submit Recommendation Feedback
- **Endpoint**: `POST /api/feedback/recommendation`
- **Payload**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "recommended_crop": "cotton",
  "selected_crop": "cotton",
  "suitability_score": 88.5,
  "rating": "helpful",
  "reason": "Accurate soil analysis",
  "free_text": "Cotton grows well in our black soil.",
  "model_version": "random_forest_v2",
  "region": "Parbhani",
  "season": "kharif"
}
```

### 4.2 Submit Crop Outcome Report
- **Endpoint**: `POST /api/feedback/outcome`
- **Payload**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "crop": "cotton",
  "outcome_status": "harvested",
  "crop_performance": "good",
  "actual_yield": 18.5,
  "yield_unit": "quintals_per_ha"
}
```

### 4.3 Technical Feedback Dashboard API
- **Endpoint**: `GET /api/analytics/feedback-summary`
- **Returns**: Aggregated counts, helpfulness percentages, crop-wise dispute lists, and feedback breakdown by district and model version.
