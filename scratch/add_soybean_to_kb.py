import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(BASE_DIR, "knowledge", "crop_requirements.json")

with open(KB_PATH, "r") as f:
    data = json.load(f)

if "soybean" not in data["crops"]:
    data["crops"]["soybean"] = {
        "common_name": "Soybean",
        "local_name": "Soya",
        "scientific_name": "Glycine max",
        "category": "pulse_oilseed",
        "maharashtra_suitability": "high",
        "maharashtra_regions": ["Marathwada", "Vidarbha", "Western Maharashtra"],
        "seasons": {
            "maharashtra": ["kharif"],
            "general": ["kharif"]
        },
        "soil": {
            "preferred_types": ["heavy_black", "medium_black", "clay_loam"],
            "source": "ICAR-IISR (Indian Institute of Soybean Research) Indore"
        },
        "ph": {
            "optimal_min": 6.0,
            "optimal_max": 7.5,
            "critical_min": 5.5,
            "critical_max": 8.5,
            "source": "ICAR-IISR Indore"
        },
        "nutrients": {
            "N": {"requirement": "medium", "level": "medium", "notes": "Legume; fixes atmospheric N", "source": "ICAR-IISR"},
            "P": {"requirement": "high", "level": "medium_to_high", "source": "ICAR-IISR"},
            "K": {"requirement": "medium", "level": "medium_to_high", "source": "ICAR-IISR"}
        },
        "temperature": {
            "optimal_min": 20,
            "optimal_max": 32,
            "critical_min": 15,
            "critical_max": 40,
            "source": "ICAR-IISR"
        },
        "humidity": {
            "optimal_min": 60,
            "optimal_max": 80,
            "source": "ICAR-IISR"
        },
        "rainfall": {
            "optimal_min": 600,
            "optimal_max": 900,
            "critical_min": 450,
            "critical_max": 1300,
            "notes": "Kharif oilseed pulse; requires well-distributed rainfall",
            "source": "ICAR-IISR / VNMKV Parbhani"
        },
        "irrigation": {
            "requirement": "moderate",
            "notes": "Rainfed in Kharif; protective irrigation at pod filling helps yield",
            "source": "Maharashtra State Dept of Agriculture"
        },
        "drainage": {
            "preferred": ["good", "moderate"],
            "source": "ICAR-IISR"
        }
    }

with open(KB_PATH, "w") as f:
    json.dump(data, f, indent=2)

print("Soybean added to knowledge base successfully.")
