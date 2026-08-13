import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(BASE_DIR, "knowledge", "crop_requirements.json")

with open(KB_PATH, "r") as f:
    data = json.load(f)

perennial_crops = {"grapes", "pomegranate", "mango", "banana", "citrus", "apple", "coffee", "coconut"}

for crop_key, crop_req in data["crops"].items():
    if crop_key in perennial_crops:
        crop_req["category_type"] = "perennial_horticulture"
    else:
        crop_req["category_type"] = "seasonal_field_crop"

    crop_req["source_name"] = "Government of India Soil Health Card & ICAR Research Guidelines"
    crop_req["source_url"] = "https://soilhealth.dac.gov.in/"
    crop_req["last_verified"] = "2026-08-13"

with open(KB_PATH, "w") as f:
    json.dump(data, f, indent=2)

print("Enriched crop_requirements.json with category_type and source metadata.")
