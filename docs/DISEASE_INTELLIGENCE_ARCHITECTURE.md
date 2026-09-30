# 🔬 AgriN — Crop Disease Intelligence Architecture

> **Document Version:** 1.0.0 (Phase 2.5)  
> **Status:** Architecture Specification & Diagnostic Protocol  
> **Standard:** ICAR Plant Pathology & Diagnostic Triage Workflow

---

## 1. Executive Summary & Honest Baseline

### Current State (Phase 2.5)
* **Architecture and Data Model Only.**
* AgriN provides the standardized `DiseaseObservation` schema and triage state machine.
* **No fake disease models or fabricated diagnostic predictions exist.** The system does not pretend to recognize leaf blights or rusts without an actual, peer-reviewed computer vision model. In all health snapshots and advisories, crop disease risk explicitly returns `UNAVAILABLE` with status `NOT_ASSESSED`.

### Next Implementation Phase (Phase 3.0)
* Integration of a validated Vision Transformer (ViT) or Convolutional Neural Network (CNN) trained on verified field pathology datasets (e.g., PlantVillage, ICAR Crop Disease Benchmark).
* Implementation of an expert agronomist review portal for ambiguous classifications.

---

## 2. End-to-End Diagnostic Pipeline

```text
┌────────────────────────────────────────────────────────┐
│                   1. Farmer Image                      │
│      (Leaf, Stem, or Fruit photograph via smartphone)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               2. Image Quality Check                   │
│   (Assess resolution, blur, lighting, leaf presence)   │
│         (Reject if out of focus or unidentifiable)     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               3. Crop Identification                   │
│     (Confirm crop matches claimed farm session crop)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                  4. Disease Model                      │
│     (Pathology neural network outputs probabilities)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│              5. Confidence Thresholding                │
│                                                        │
│   - Confidence >= 0.85 ──► LIKELY                      │
│   - 0.50 <= Conf < 0.85 ──► SUSPECTED (Second photo)   │
│   - Confidence < 0.50  ──► REVIEW_REQUIRED             │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│         6. Human / KVK Expert Review Loop              │
│    (Triggered when confidence < 0.85 or rare pathogen) │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│         7. Treatment / Management Advisory             │
│        (Canonical AgriculturalAdvisory generated)      │
│   (Bio-fungicides, cultural controls, approved sprays) │
└────────────────────────────────────────────────────────┘
```

---

## 3. Diagnostic States (`DiagnosisStatus`)

Every `DiseaseObservation` is governed by a strict lifecycle state:

| Status | Definition | Next System Action |
| :--- | :--- | :--- |
| `NOT_ASSESSED` | Default initial state. No diagnostic image or symptom log submitted. | Await farmer image or field scout input. |
| `SUSPECTED` | Symptom pattern matches known disease, but confidence is intermediate ($0.50 - 0.84$). | Request second angled photo or local weather verification. |
| `LIKELY` | High-confidence model identification ($\ge 0.85$) supported by prevailing weather triggers (e.g., high humidity). | Issue preliminary cultural management advisory. |
| `CONFIRMED` | Verified by a Krishi Vigyan Kendra (KVK) officer, extension entomologist/pathologist, or laboratory assay. | Issue targeted agronomic treatment advisory. |
| `REVIEW_REQUIRED` | Image ambiguous, novel symptom, or critical quarantine pest (e.g., Fall Armyworm in new zones). | Route to regional extension expert queue. |

---

## 4. Disease Observation Schema (`DiseaseObservation`)

Defined in `backend/app/models/intelligence_schemas.py`:

```python
class DiseaseObservation(BaseModel):
    farm_id: str
    crop: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    image_reference: Optional[str] = None
    symptoms: List[str] = []
    location: Optional[Dict[str, float]] = None
    model_prediction: Optional[str] = None
    confidence: Optional[float] = None
    diagnosis_status: DiagnosisStatus = DiagnosisStatus.NOT_ASSESSED
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    data_confidence: ConfidenceMetadata
```

---

## 5. Integrating Biophysical Context into Diagnosis

Computer vision models often fail because visual symptoms of nutrient deficiencies (e.g., Nitrogen or Iron chlorosis) look identical to viral or fungal yellowing.

AgriN solves this through **Multi-Modal Cross-Validation**:
1. **Soil Context Check:** Before classifying a leaf as *Yellow Vein Mosaic*, the engine checks `SoilRecord`:
   - If soil Nitrogen or Iron is severely deficient, the advisory warns: *"Visual chlorosis may stem from low soil nitrogen rather than viral disease."*
2. **Weather Risk Correlation:** Fungal blights require prolonged relative humidity ($> 85\%$) and moderate temperatures ($20 - 28^\circ\text{C}$). The engine cross-references live weather before confirming fungal disease likelihood.

---

## 6. Implementation Phasing Roadmap

| Phase | Milestone | Deliverables | Target Timeline |
| :--- | :--- | :--- | :--- |
| **Phase 2.5 (Current)** | Architecture & Schema | `DiseaseObservation` data model, triage states, honest `UNAVAILABLE` handling | **Completed** |
| **Phase 3.0** | Vision Model Integration | On-device / cloud CNN/ViT pipeline for 10 common Indian crop diseases | Next Phase |
| **Phase 3.5** | Extension Review Portal | Web dashboard for KVK scientists to review `REVIEW_REQUIRED` diagnostic tickets | Future Phase |
| **Phase 4.0** | Epidemiology Forecasting | Regional disease outbreak heatmaps using weather telemetry and farmer submissions | Future Phase |
