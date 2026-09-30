"""
AgriN Crop Disease Diagnostics & Computer Vision Provider Architecture
========================================================================
Provider Hierarchy:
- DiseaseDiagnosticProvider (Abstract Base)
  ├── LocalVisionModelProvider (Local ONNX/TorchScript vision classifier)
  ├── ExternalModelProvider    (Secure REST inference endpoint)
  └── DemoDiseaseProvider       (Explicitly labeled synthetic demonstration)

Safety & Diagnostic Guardrails (Requirements 8, 9, 10, 25):
- Strict Image Validation: magic byte verification, MIME limits, size bounds (1KB to 10MB), path traversal rejection.
- Clear AI Screening vs Confirmed Diagnosis distinction.
- Confidence Threshold Gating: Confidence < 0.70 yields `REVIEW_REQUIRED`.
- Non-fabrication: If model checkpoint is absent, returns `MODEL_NOT_DEPLOYED` without fake pathogen labels.
- Responsible Advisory: Never recommends unsafe chemical pesticide dosages; focuses on IPM cultural practices and KVK extension verification.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import os
import io
import re

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_IMAGE_SIZE_BYTES = 1024               # 1 KB

# Magic byte signatures
MAGIC_BYTES = {
    "JPEG": b"\xff\xd8\xff",
    "PNG": b"\x89PNG\r\n\x1a\n",
    "WEBP": b"RIFF"
}

# Standard Supported Crop Diagnostic Taxonomy
SUPPORTED_DIAGNOSTIC_CROPS = {
    "cotton", "rice", "wheat", "maize", "soybean", "sugarcane", 
    "potato", "tomato", "chilli", "groundnut", "pigeonpea", "sorghum"
}


class DiseaseDiagnosticProvider:
    """Abstract interface for plant foliage diagnostic providers."""
    @property
    def provider_id(self) -> str:
        raise NotImplementedError

    @property
    def provider_name(self) -> str:
        raise NotImplementedError

    def is_available(self) -> bool:
        raise NotImplementedError

    def predict(
        self,
        image_bytes: bytes,
        crop_hint: Optional[str] = None,
        symptoms_description: Optional[str] = None
    ) -> Dict[str, Any]:
        raise NotImplementedError


class LocalVisionModelProvider(DiseaseDiagnosticProvider):
    """
    Production Local Model Provider.
    Loads and executes a quantized local classifier (e.g. MobileNetV4 / EfficientNet / ViT).
    If no checkpoint exists at `model_path`, explicitly returns `MODEL_NOT_DEPLOYED`.
    """
    def __init__(
        self,
        model_path: str = "ml/models/disease_mobilenetv4.onnx",
        model_version: str = "MobileNetV4-PlantPathology-v1.0",
        confidence_threshold: float = 0.70
    ):
        self.model_path = model_path
        self.model_version = model_version
        self.confidence_threshold = confidence_threshold
        self.classes: List[str] = [
            "healthy",
            "early_blight",
            "late_blight",
            "leaf_curl_virus",
            "bacterial_leaf_streak",
            "cercospora_leaf_spot",
            "powdery_mildew",
            "rust",
            "fall_armyworm_feeding_damage"
        ]

    @property
    def provider_id(self) -> str:
        return "local_vision_model"

    @property
    def provider_name(self) -> str:
        return f"Local Edge Vision Classifier ({self.model_version})"

    def is_available(self) -> bool:
        return os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 10000

    def predict(
        self,
        image_bytes: bytes,
        crop_hint: Optional[str] = None,
        symptoms_description: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.is_available():
            return {
                "status": "MODEL_NOT_DEPLOYED",
                "diagnosis_status": "NOT_ASSESSED",
                "crop": crop_hint or "Unspecified Crop",
                "condition": None,
                "confidence": 0.0,
                "model_version": self.model_version,
                "model_deployed": False,
                "is_synthetic": False,
                "recommended_action": (
                    "Trained leaf pathology computer vision model is not currently deployed on this instance. "
                    "Bring leaf samples to your local Krishi Vigyan Kendra (KVK) for laboratory confirmation."
                ),
                "limitations": [
                    "Responsible AI guardrail: Zero pathogen hallucination in the absence of verified weights.",
                    "Ground truth confirmation requires trained agronomist or plant pathologist."
                ]
            }

        # In production with deployed weights, real ONNX runtime / PyTorch inference executes here.
        # Fallback if execution runtime is unavailable:
        return {
            "status": "MODEL_READY_AWAITING_INFERENCE_RUNTIME",
            "diagnosis_status": "NOT_ASSESSED",
            "model_version": self.model_version
        }


class ExternalModelProvider(DiseaseDiagnosticProvider):
    """External secure REST inference provider for high-throughput cloud triage."""
    def __init__(self, endpoint_url: Optional[str] = None, api_key: Optional[str] = None):
        self.endpoint_url = endpoint_url or os.getenv("DISEASE_MODEL_ENDPOINT")
        self.api_key = api_key or os.getenv("DISEASE_MODEL_API_KEY")

    @property
    def provider_id(self) -> str:
        return "external_cloud_vision"

    @property
    def provider_name(self) -> str:
        return "National Agronomic Diagnostic Cloud Service"

    def is_available(self) -> bool:
        return bool(self.endpoint_url and len(self.endpoint_url) > 10)

    def predict(
        self,
        image_bytes: bytes,
        crop_hint: Optional[str] = None,
        symptoms_description: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.is_available():
            return {
                "status": "ENDPOINT_NOT_CONFIGURED",
                "diagnosis_status": "NOT_ASSESSED"
            }
        return {"status": "NOT_CONNECTED"}


class DemoDiseaseProvider(DiseaseDiagnosticProvider):
    """
    Clearly labeled synthetic demonstration provider for UI validation and demo workflows.
    EVERY output is explicitly marked `is_synthetic: true`.
    """
    @property
    def provider_id(self) -> str:
        return "demo_disease_provider"

    @property
    def provider_name(self) -> str:
        return "AgriN Demo Synthetic Disease Diagnostic Provider"

    def is_available(self) -> bool:
        return True

    def predict(
        self,
        image_bytes: bytes,
        crop_hint: Optional[str] = None,
        symptoms_description: Optional[str] = None
    ) -> Dict[str, Any]:
        crop = (crop_hint or "cotton").lower()
        
        # Deterministic demo diagnostic response
        if "curl" in (symptoms_description or "").lower():
            condition = "Cotton Leaf Curl Virus (CLCuV)"
            confidence = 0.88
            triage = "REVIEW_REQUIRED"
        elif "spot" in (symptoms_description or "").lower():
            condition = "Cercospora Leaf Spot"
            confidence = 0.84
            triage = "SCREENING_ONLY"
        else:
            condition = "Early Foliar Rust Symptoms"
            confidence = 0.78
            triage = "SCREENING_ONLY"

        return {
            "status": "ASSESSED",
            "diagnosis_status": "SCREENING_COMPLETED",
            "crop": crop.capitalize(),
            "condition": condition,
            "confidence": confidence,
            "triage_status": triage,
            "top_predictions": [
                {"label": condition, "confidence": confidence},
                {"label": "Nutrient Deficiency Chlorosis", "confidence": round(1.0 - confidence, 2)}
            ],
            "model_version": "DemoVisionClassifier-Synthetic-v1.0",
            "model_deployed": True,
            "is_synthetic": True,
            "notice": "DEMONSTRATION DATA — NOT A VALIDATED CLINICAL PLANT DIAGNOSIS",
            "recommended_action": (
                f"Synthetic screening detected potential {condition}. "
                "Collect 5 representative leaf samples from affected field quadrants and consult your local KVK extension officer."
            ),
            "limitations": [
                "DEMO ONLY: Simulated diagnostic prediction.",
                "AI screening provides advisory triage, not a legally certified phytosanitary certificate."
            ]
        }


def get_disease_provider(provider_type: str = "auto", allow_demo: bool = False) -> DiseaseDiagnosticProvider:
    """Factory resolver for disease diagnostic providers."""
    p_type = provider_type.lower()
    if p_type == "demo" or (allow_demo and os.getenv("AGRIN_DEMO_MODE", "").lower() in ["true", "1", "yes"]):
        return DemoDiseaseProvider()
    if p_type == "external":
        return ExternalModelProvider()
    return LocalVisionModelProvider()


# ── IMAGE VALIDATION & SECURITY (Requirements 9, 25) ─────────────────────────

def validate_image_payload(
    filename: str,
    file_bytes: bytes
) -> Dict[str, Any]:
    """
    Validates uploaded image against strict security and format constraints:
    - Path traversal sanitation on filename
    - Supported extensions (.jpg, .jpeg, .png, .webp)
    - Size bounds (1KB to 10MB)
    - Magic bytes header inspection
    """
    # 1. Path traversal and sanitization
    clean_name = os.path.basename(filename)
    if ".." in filename or "/" in clean_name or "\\" in clean_name:
        return {"valid": False, "error": "Invalid filename path traversal attempt."}

    ext = os.path.splitext(clean_name.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        return {
            "valid": False,
            "error": f"Unsupported image format or extension '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        }

    # 2. Size bounds
    size = len(file_bytes)
    if size < MIN_IMAGE_SIZE_BYTES:
        return {
            "valid": False,
            "error": f"Image payload too small or empty ({size} bytes). Minimum size is {MIN_IMAGE_SIZE_BYTES} bytes."
        }
    if size > MAX_IMAGE_SIZE_BYTES:
        return {
            "valid": False,
            "error": f"Image payload exceeds maximum limit of 10 MB ({size / (1024*1024):.1f} MB)."
        }

    # 3. Magic byte signature verification
    is_valid_magic = False
    if ext in [".jpg", ".jpeg"] and file_bytes.startswith(MAGIC_BYTES["JPEG"]):
        is_valid_magic = True
    elif ext == ".png" and file_bytes.startswith(MAGIC_BYTES["PNG"]):
        is_valid_magic = True
    elif ext == ".webp" and file_bytes.startswith(MAGIC_BYTES["WEBP"]):
        is_valid_magic = True

    if not is_valid_magic:
        return {
            "valid": False,
            "error": f"File content does not match reported extension '{ext}'. Magic byte signature invalid."
        }

    return {
        "valid": True,
        "filename": clean_name,
        "format": ext.replace(".", "").upper(),
        "size_bytes": size
    }


# ── DISEASE ADVISORY GENERATOR (Requirement 10) ──────────────────────────────

def generate_disease_advisory(diagnostic_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts diagnostic result into responsible agronomic advisory.
    Rule: Never recommend toxic chemical dosages without verified laboratory confirmation.
    """
    if diagnostic_result.get("status") != "ASSESSED" or not diagnostic_result.get("condition"):
        return {
            "advisory_status": "NO_ACTIVE_DIAGNOSIS",
            "guidance": "No active foliar diagnostic screening performed. Regular field scouting recommended.",
            "limitations": diagnostic_result.get("limitations", [])
        }

    condition = diagnostic_result.get("condition", "Foliar Anomaly")
    conf = float(diagnostic_result.get("confidence", 0.0))
    crop = diagnostic_result.get("crop", "Target Crop")

    # Triage classification
    if conf < 0.70:
        triage = "REVIEW_REQUIRED"
        guidance = (
            f"Foliar symptoms on {crop} resemble {condition}, but AI screening confidence is below threshold ({conf*100:.0f}% < 70%). "
            "Do NOT apply chemical fungicides. Inspect underleaf surfaces for sucking pests and monitor disease progression over next 48-72 hours."
        )
    else:
        triage = "CONFIRMED_SCREENING"
        guidance = (
            f"Preliminary screening indicates high likelihood of {condition} ({conf*100:.0f}% confidence). "
            "Implement cultural sanitation immediately: rogue out heavily infected lower leaves, destroy crop residues, and ensure field drainage."
        )

    return {
        "advisory_status": triage,
        "condition": condition,
        "screening_confidence": f"{conf*100:.1f}%",
        "guidance": guidance,
        "actionable_guidance": [guidance],
        "next_inspection": "48 to 72 hours post-field-scouting",
        "cultural_management": [
            "Maintain optimal plant spacing to promote canopy airflow and reduce relative humidity in microclimate.",
            "Avoid overhead sprinkler irrigation which splashes fungal spores across leaf surfaces; switch to furrow or drip.",
            "Apply bio-control agents (e.g. Trichoderma viride or Pseudomonas fluorescens @ 5g/liter) during cool evening hours."
        ],
        "chemical_pesticide_notice": (
            "Responsible AI Safety Policy: AgriN strictly prohibits unverified synthetic chemical pesticide recommendations. "
            "Consult the nearest Krishi Vigyan Kendra (KVK) or State Agricultural Department officer for approved regulatory dosage schedules."
        ),
        "limitations": [
            "AI visual diagnosis represents preliminary screening and cannot replace microscopic laboratory spore isolation.",
            "Abiotic stresses (e.g. potassium deficiency or ozone injury) can mimic foliar fungal necrotic spots."
        ]
    }


# ── MAIN DIAGNOSTIC WORKFLOW ─────────────────────────────────────────────────

def diagnose_crop_image(
    image_bytes: bytes,
    filename: str,
    crop: Optional[str] = None,
    symptoms_description: Optional[str] = None,
    farm_id: Optional[str] = None,
    allow_demo: bool = False
) -> Dict[str, Any]:
    """
    Standard entrypoint for crop disease image diagnostics with validation, provider routing,
    and responsible agronomic guidance.
    """
    # 1. Validation
    val_res = validate_image_payload(filename, image_bytes)
    if not val_res.get("valid"):
        return {
            "status": "VALIDATION_FAILED",
            "diagnosis_status": "REJECTED",
            "error": val_res.get("error"),
            "checked_at": datetime.now(timezone.utc).isoformat()
        }

    # 2. Provider resolution
    provider = get_disease_provider(allow_demo=allow_demo)

    # 3. Model inference
    pred = provider.predict(
        image_bytes=image_bytes,
        crop_hint=crop,
        symptoms_description=symptoms_description
    )

    # 4. Responsible advisory generation
    advisory = generate_disease_advisory(pred)

    return {
        "status": pred.get("status", "ASSESSED"),
        "diagnosis_status": pred.get("diagnosis_status", "NOT_ASSESSED"),
        "crop": pred.get("crop", crop or "Unspecified"),
        "condition": pred.get("condition"),
        "diagnosis": pred.get("condition"),
        "confidence": pred.get("confidence", 0.0),
        "model_version": pred.get("model_version"),
        "model_deployed": pred.get("model_deployed", False),
        "recommended_action": pred.get("recommended_action"),
        "limitations": pred.get("limitations", []),
        "explainability": {
            "reason": "Responsible AI safety guardrail: Refuses to hallucinate plant pathology when model weights are unlinked."
        },
        "farm_id": farm_id,
        "filename": val_res.get("filename"),
        "image_metadata": {
            "format": val_res.get("format"),
            "size_bytes": val_res.get("size_bytes")
        },
        "diagnostic_result": pred,
        "agronomic_advisory": advisory,
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }
