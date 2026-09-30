"""
AgriN Crop Disease Diagnostic Architecture
Implements the diagnostic pipeline contract:
Plant Image -> Image Validation & Quality Check -> Model Provider Interface -> Confidence & Triage.

STRICT NON-FABRICATION RULE:
If no trained model weights exist, the service explicitly returns:
`status = "MODEL_NOT_DEPLOYED"`
without fabricating mock pathogen names, fake bounding boxes, or synthetic diagnostic probabilities.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import os

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_IMAGE_SIZE_BYTES = 1024               # 1 KB


class DiseaseModelProvider:
    """Interface for pluggable plant leaf pathology computer vision models."""
    def is_available(self) -> bool:
        raise NotImplementedError

    def predict(self, image_bytes: bytes, crop_hint: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError


class DeployedVisionTransformerProvider(DiseaseModelProvider):
    """
    Production Vision Transformer / MobileNet model provider.
    Checks for the existence of trained weight checkpoints in `ml/models/disease_vit.onnx` or `.pt`.
    """
    def __init__(self, model_path: str = "ml/models/disease_vit.onnx"):
        self.model_path = model_path

    def is_available(self) -> bool:
        return os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 10000

    def predict(self, image_bytes: bytes, crop_hint: Optional[str] = None) -> Dict[str, Any]:
        if not self.is_available():
            return {
                "status": "MODEL_NOT_DEPLOYED",
                "diagnosis": None,
                "confidence": 0.0,
                "diagnosis_status": "NOT_ASSESSED",
                "possible_causes": [],
                "recommended_action": "Trained leaf pathology computer vision model is not currently deployed. Consult your nearest Krishi Vigyan Kendra (KVK) extension specialist.",
                "explainability": {
                    "pipeline_stage": "IMAGE_VALIDATED_AWAITING_MODEL",
                    "reason": "System adheres to strict Responsible AI guidelines: no simulated pathogen diagnoses without clinically validated model weights."
                }
            }
        # In future phases, ONNX / PyTorch inference execution happens here
        return {}


def validate_image_payload(
    filename: str,
    file_bytes: bytes
) -> Dict[str, Any]:
    """
    Validates uploaded plant image integrity, format, and size bounds.
    """
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        return {
            "valid": False,
            "error": f"Unsupported image format '{ext}'. Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        }

    size = len(file_bytes)
    if size < MIN_IMAGE_SIZE_BYTES:
        return {
            "valid": False,
            "error": f"Image file is corrupt or too small ({size} bytes). Minimum size is {MIN_IMAGE_SIZE_BYTES} bytes."
        }
    if size > MAX_IMAGE_SIZE_BYTES:
        return {
            "valid": False,
            "error": f"Image file exceeds maximum allowable size ({size / (1024*1024):.1f} MB > 10 MB limit)."
        }

    return {
        "valid": True,
        "format": ext.replace(".", "").upper(),
        "size_bytes": size,
        "filename": filename
    }


def diagnose_crop_image(
    image_bytes: bytes,
    filename: str,
    crop: Optional[str] = None,
    symptoms_description: Optional[str] = None,
    farm_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the validated crop disease triage pipeline.
    """
    validation = validate_image_payload(filename, image_bytes)
    if not validation["valid"]:
        return {
            "status": "VALIDATION_FAILED",
            "error": validation["error"],
            "diagnosis_status": "NOT_ASSESSED",
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

    provider = DeployedVisionTransformerProvider()
    prediction_result = provider.predict(image_bytes, crop_hint=crop)

    return {
        "status": prediction_result.get("status", "MODEL_NOT_DEPLOYED"),
        "farm_id": farm_id,
        "crop": crop,
        "symptoms_reported": symptoms_description,
        "image_metadata": {
            "filename": filename,
            "format": validation["format"],
            "size_kb": round(validation["size_bytes"] / 1024.0, 1)
        },
        "diagnosis": prediction_result.get("diagnosis"),
        "confidence": prediction_result.get("confidence", 0.0),
        "diagnosis_status": prediction_result.get("diagnosis_status", "NOT_ASSESSED"),
        "possible_causes": prediction_result.get("possible_causes", []),
        "recommended_action": prediction_result.get("recommended_action"),
        "explainability": prediction_result.get("explainability", {
            "architecture": "MobileNetV4 / Vision Transformer (ViT) Triage State Machine",
            "current_state": "Model weights unlinked. Live diagnostic inference disabled to prevent false-positive spray recommendations."
        }),
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }
