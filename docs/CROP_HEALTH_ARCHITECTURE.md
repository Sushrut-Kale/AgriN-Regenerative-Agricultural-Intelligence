# 🔬 Crop Health & Disease Diagnostic Architecture

> **Module:** `backend/app/services/disease_service.py`  
> **Route:** `POST /api/crop-health/diagnose`  
> **Status:** `ARCHITECTURE READY` (API Contract & Image Validation Complete; Strict `MODEL_NOT_DEPLOYED` Guardrail)  

---

## 1. Architectural Design

The AgriN Crop Health pipeline establishes an end-to-end diagnostic workflow designed to integrate deep learning vision models (e.g., Vision Transformers or MobileNetV4 trained on PlantVillage/ICAR leaf pathology datasets) without breaking system stability:

```
               CROP IDENTIFIER
                      ↓
              PLANT LEAF IMAGE
                      ↓
         IMAGE INTEGRITY & VALIDATION
      (Size <= 10MB, Format JPEG/PNG/WebP,
       Payload Byte Signature Check)
                      ↓
          MODEL PROVIDER INTERFACE
                      ↓
        DISEASE & STRESS CLASSIFIER
                      ↓
     CONFIDENCE & EXPLAINABILITY ENGINE
                      ↓
          RECOMMENDED IPM ACTIONS
```

---

## 2. Responsible AI Guardrail: Zero Fabrication

If no weights are loaded or if the ML model service is offline, AgriN **never hallucinates** fake pathogen diagnoses. Instead, it returns an honest, standardized status:

```json
{
  "status": "MODEL_NOT_DEPLOYED",
  "crop": "Cotton",
  "message": "Leaf vision diagnostic inference engine is currently not deployed in this runtime environment.",
  "confidence": 0.0,
  "confidence_level": "INSUFFICIENT",
  "recommended_action": "Submit physical leaf sample to the nearest district Krishi Vigyan Kendra (KVK) for laboratory pathology examination.",
  "metadata": {
    "image_received": true,
    "filename": "leaf_sample.jpg",
    "filesize_bytes": 248900
  }
}
```

---

## 3. Image Validation Rules

Implemented in `backend/app/services/disease_service.py`:
- Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`.
- Maximum file size: 10,485,760 bytes (10 MB).
- Minimum byte size: 100 bytes (blocks empty payloads).
- Magic number / signature verification for image stream integrity.

---

## 4. Verification Evidence

Automated test: `tests/test_track4_evolution.py::test_disease_image_validation_and_model_not_deployed`
- Verified: Oversized payload (>10MB) returns `400 Bad Request`.
- Verified: Invalid extension returns `400 Bad Request`.
- Verified: Valid image yields `MODEL_NOT_DEPLOYED` with 0.0 confidence, adhering to the non-negotiable responsible AI charter.
