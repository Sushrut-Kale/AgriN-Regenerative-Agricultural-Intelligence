import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "knowledge", "crop_requirements.json")

with open(KNOWLEDGE_PATH, "r") as f:
    data = json.load(f)

# Scientific seasonal rainfall (mm) and nutrient updates
RAINFALL_UPDATES = {
    "rice":        {"optimal_min": 1000, "optimal_max": 1600, "critical_min": 750,  "critical_max": 2500, "notes": "High water requirement; puddling/flooding or heavy irrigation preferred"},
    "cotton":      {"optimal_min": 600,  "optimal_max": 1100, "critical_min": 450,  "critical_max": 1400, "notes": "Kharif crop; deep black cotton soils retain moisture; dry harvest period needed"},
    "maize":       {"optimal_min": 500,  "optimal_max": 800,  "critical_min": 350,  "critical_max": 1200, "notes": "Moderate rainfall required; sensitive to waterlogging at early growth"},
    "chickpea":    {"optimal_min": 350,  "optimal_max": 600,  "critical_min": 250,  "critical_max": 800,  "notes": "Rabi crop; rainfed or light irrigation"},
    "kidneybeans": {"optimal_min": 400,  "optimal_max": 650,  "critical_min": 300,  "critical_max": 900,  "notes": "Moderate rainfall, well-drained loamy soils"},
    "pigeonpeas":  {"optimal_min": 600,  "optimal_max": 1000, "critical_min": 450,  "critical_max": 1300, "notes": "Deep rooted Kharif pulse; drought tolerant once established"},
    "mothbeans":   {"optimal_min": 300,  "optimal_max": 500,  "critical_min": 200,  "critical_max": 750,  "notes": "Highly drought-tolerant arid pulse"},
    "mungbean":    {"optimal_min": 400,  "optimal_max": 750,  "critical_min": 300,  "critical_max": 950,  "notes": "Short duration Kharif/Summer crop"},
    "blackgram":   {"optimal_min": 400,  "optimal_max": 750,  "critical_min": 300,  "critical_max": 950,  "notes": "Short duration Kharif pulse"},
    "lentil":      {"optimal_min": 300,  "optimal_max": 500,  "critical_min": 200,  "critical_max": 700,  "notes": "Rabi cool-season crop"},
    "pomegranate": {"optimal_min": 500,  "optimal_max": 800,  "critical_min": 350,  "critical_max": 1100, "notes": "Semi-arid horticultural crop; dry flowering/harvest preferred"},
    "banana":      {"optimal_min": 1200, "optimal_max": 2200, "critical_min": 900,  "critical_max": 3000, "notes": "High water requirement year-round"},
    "mango":       {"optimal_min": 750,  "optimal_max": 1500, "critical_min": 500,  "critical_max": 2200, "notes": "Dry spell during flowering essential for fruit set"},
    "grapes":      {"optimal_min": 500,  "optimal_max": 800,  "critical_min": 350,  "critical_max": 1000, "notes": "Subtropical vine; needs dry weather during ripening"},
    "watermelon":  {"optimal_min": 400,  "optimal_max": 650,  "critical_min": 250,  "critical_max": 850,  "notes": "Warm season cucurbit; well-drained sandy loam"},
    "muskmelon":   {"optimal_min": 400,  "optimal_max": 650,  "critical_min": 250,  "critical_max": 850,  "notes": "Warm dry atmosphere preferred during fruit ripening"},
    "apple":       {"optimal_min": 800,  "optimal_max": 1250, "critical_min": 600,  "critical_max": 1600, "notes": "Temperate fruit crop; requires winter chilling"},
    "orange":      {"optimal_min": 800,  "optimal_max": 1200, "critical_min": 600,  "critical_max": 1500, "notes": "Citrus crop; requires well-drained soil"},
    "papaya":      {"optimal_min": 1000, "optimal_max": 1800, "critical_min": 750,  "critical_max": 2400, "notes": "Tropical fruit; sensitive to waterlogging"},
    "coconut":     {"optimal_min": 1300, "optimal_max": 2500, "critical_min": 1000, "critical_max": 3500, "notes": "Coastal/tropical palm; high humidity & rainfall"},
    "jute":        {"optimal_min": 1200, "optimal_max": 1800, "critical_min": 900,  "critical_max": 2500, "notes": "Humid tropical fiber crop"},
    "coffee":      {"optimal_min": 1500, "optimal_max": 2500, "critical_min": 1100, "critical_max": 3000, "notes": "Highland plantation crop; shade and high rainfall"}
}

for crop, r_data in RAINFALL_UPDATES.items():
    if crop in data["crops"]:
        data["crops"][crop]["rainfall"] = r_data
        # Ensure metadata source reference
        data["crops"][crop]["rainfall"]["source"] = "ICAR / FAO Crop Ecology Database / VNMKV Guidelines"

with open(KNOWLEDGE_PATH, "w") as f:
    json.dump(data, f, indent=2)

print("Updated crop_requirements.json successfully with scientific rainfall ranges.")
