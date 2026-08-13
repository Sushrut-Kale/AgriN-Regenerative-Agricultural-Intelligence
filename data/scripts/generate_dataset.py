"""
FarmFriend AI — Dataset Generation Script
==========================================

PURPOSE:
    Creates a realistic synthetic/augmented training dataset for the crop 
    recommendation ML model based on published agricultural literature.

DISCLOSURE:
    This is SYNTHETIC/AUGMENTED data generated from published crop requirement
    tables from ICAR, TNAU, FAO, and similar credible sources.
    
    It is NOT raw field observation data.
    It is clearly labeled as synthetic in all documentation.
    
    The distributions are parameterised from:
    - Kaggle Crop Recommendation Dataset (Atharva Ingle, 2020)
      - URL: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
      - Note: That dataset itself is augmented from public Indian agricultural data
    - ICAR crop production guides (2015-2023)
    - TNAU crop production technology (2020)
    - FAO crop requirements database
    
    Limitation: This synthetic dataset cannot represent the full complexity
    of real Indian agricultural conditions including variety effects, 
    management practices, and year-to-year variability.

OUTPUT:
    data/raw/crop_recommendation_synthetic.csv
    data/raw/dataset_metadata.json

USAGE:
    python data/scripts/generate_dataset.py
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime

# Reproducibility
SEED = 42
np.random.seed(SEED)

# Output paths
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Crop parameter distributions ────────────────────────────────────────────
# Format: (mean, std, min_clip, max_clip)
# Sources: ICAR crop production guides; TNAU; FAO; 
#          Kaggle Crop Recommendation Dataset distribution analysis
#
# N, P, K: kg/ha (available soil nutrients — SHC interpretation scale)
# temperature: °C
# humidity: % relative humidity
# ph: 0-14 scale
# rainfall: mm per year

CROP_PARAMS = {
    "rice": {
        "N":           (80, 20,  0,  160),
        "P":           (50, 10,  20,  80),
        "K":           (45, 10,  20,  80),
        "temperature": (25, 4,   18,  35),
        "humidity":    (83, 5,   70,  95),
        "ph":          (6.2, 0.5, 5.0, 7.5),
        "rainfall":    (230, 40, 120, 320),
        "samples": 110
    },
    "maize": {
        "N":           (90, 20,  0,  160),
        "P":           (50, 10,  20,  80),
        "K":           (45, 10,  20,  80),
        "temperature": (22, 4,   10,  32),
        "humidity":    (68, 8,   50,  85),
        "ph":          (6.2, 0.6, 5.0, 8.0),
        "rainfall":    (70,  20,  30, 130),
        "samples": 110
    },
    "chickpea": {
        "N":           (20, 10,  0,   60),
        "P":           (60, 10,  30, 100),
        "K":           (25, 8,   5,   55),
        "temperature": (19, 4,   8,   30),
        "humidity":    (18, 4,   8,   30),
        "ph":          (7.0, 0.6, 5.5, 8.5),
        "rainfall":    (70,  18, 30, 110),
        "samples": 110
    },
    "kidneybeans": {
        "N":           (25, 10,  0,   60),
        "P":           (75, 12,  40, 110),
        "K":           (25, 8,   5,   55),
        "temperature": (19, 4,   8,   30),
        "humidity":    (20, 4,   8,   35),
        "ph":          (6.6, 0.6, 5.5, 8.0),
        "rainfall":    (70,  18, 30, 110),
        "samples": 110
    },
    "pigeonpeas": {
        "N":           (25, 8,   0,   60),
        "P":           (70, 12,  30, 110),
        "K":           (25, 8,   5,   55),
        "temperature": (24, 4,   13,  38),
        "humidity":    (52, 8,   35,  70),
        "ph":          (6.2, 0.6, 5.0, 8.0),
        "rainfall":    (85,  22, 40, 140),
        "samples": 110
    },
    "mothbeans": {
        "N":           (25, 8,   0,   55),
        "P":           (50, 10,  25,  80),
        "K":           (25, 8,   5,   55),
        "temperature": (28, 4,   18,  40),
        "humidity":    (53, 8,   35,  72),
        "ph":          (7.4, 0.5, 6.0, 9.0),
        "rainfall":    (48,  10, 25,  75),
        "samples": 110
    },
    "mungbean": {
        "N":           (25, 8,   0,   55),
        "P":           (48, 10,  20,  80),
        "K":           (25, 8,   5,   55),
        "temperature": (30, 4,   20,  40),
        "humidity":    (84, 5,   70,  97),
        "ph":          (6.8, 0.5, 5.5, 8.0),
        "rainfall":    (78,  18, 40, 120),
        "samples": 110
    },
    "blackgram": {
        "N":           (25, 8,   0,   55),
        "P":           (48, 10,  20,  80),
        "K":           (25, 8,   5,   55),
        "temperature": (30, 4,   18,  40),
        "humidity":    (67, 5,   55,  80),
        "ph":          (6.7, 0.5, 5.5, 8.0),
        "rainfall":    (68,  15, 40, 100),
        "samples": 110
    },
    "lentil": {
        "N":           (22, 8,   0,   50),
        "P":           (60, 10,  30,  90),
        "K":           (20, 5,   5,   40),
        "temperature": (24, 4,   10,  35),
        "humidity":    (66, 5,   55,  80),
        "ph":          (6.7, 0.5, 5.5, 8.0),
        "rainfall":    (40,  8,  20,  60),
        "samples": 110
    },
    "pomegranate": {
        "N":           (30, 10,  5,   65),
        "P":           (8,  3,   2,   18),
        "K":           (45, 10,  20,  75),
        "temperature": (30, 4,   18,  42),
        "humidity":    (90, 4,   78,  99),
        "ph":          (6.5, 0.8, 5.0, 8.5),
        "rainfall":    (115, 10, 90, 140),
        "samples": 110
    },
    "banana": {
        "N":           (90, 15,  50, 130),
        "P":           (85, 12,  55, 120),
        "K":           (55, 10,  30,  90),
        "temperature": (28, 3,   18,  38),
        "humidity":    (82, 5,   70,  95),
        "ph":          (6.5, 0.5, 5.5, 8.0),
        "rainfall":    (145, 25, 90, 210),
        "samples": 110
    },
    "mango": {
        "N":           (15, 5,   5,   35),
        "P":           (15, 5,   5,   35),
        "K":           (38, 8,   15,  65),
        "temperature": (25, 2,   18,  35),
        "humidity":    (55, 8,   40,  70),
        "ph":          (6.5, 0.6, 5.0, 8.0),
        "rainfall":    (90,  18, 55, 140),
        "samples": 110
    },
    "grapes": {
        "N":           (15, 5,   5,   35),
        "P":           (12, 4,   4,   25),
        "K":           (220, 20, 160, 270),
        "temperature": (25, 2,   18,  33),
        "humidity":    (82, 4,   70,  92),
        "ph":          (6.2, 0.5, 5.0, 7.5),
        "rainfall":    (60,  10, 40,  85),
        "samples": 110
    },
    "watermelon": {
        "N":           (90, 15,  50, 130),
        "P":           (15, 5,   5,   30),
        "K":           (70, 15,  40, 110),
        "temperature": (25, 2,   18,  33),
        "humidity":    (86, 4,   75,  95),
        "ph":          (6.5, 0.4, 5.5, 7.5),
        "rainfall":    (55,  10, 30,  80),
        "samples": 110
    },
    "muskmelon": {
        "N":           (90, 15,  50, 130),
        "P":           (15, 5,   5,   30),
        "K":           (70, 15,  40, 110),
        "temperature": (30, 2,   22,  38),
        "humidity":    (92, 4,   82,  99),
        "ph":          (6.7, 0.5, 5.5, 8.0),
        "rainfall":    (27,  5,  15,  40),
        "samples": 110
    },
    "apple": {
        "N":           (30, 8,   10,  55),
        "P":           (130, 8,  100, 155),
        "K":           (210, 10, 170, 240),
        "temperature": (22, 2,   14,  28),
        "humidity":    (93, 3,   85,  99),
        "ph":          (5.9, 0.4, 5.0, 7.0),
        "rainfall":    (117, 8,  95, 135),
        "samples": 110
    },
    "orange": {
        "N":           (30, 8,   10,  55),
        "P":           (8,  3,   2,   18),
        "K":           (8,  3,   2,   18),
        "temperature": (12, 3,   5,   22),
        "humidity":    (92, 3,   82,  99),
        "ph":          (6.7, 0.5, 5.5, 8.0),
        "rainfall":    (110, 8,  88, 130),
        "samples": 110
    },
    "papaya": {
        "N":           (55, 8,   30,  80),
        "P":           (20, 6,   8,   40),
        "K":           (55, 8,   30,  80),
        "temperature": (30, 4,   18,  42),
        "humidity":    (93, 3,   82,  99),
        "ph":          (6.2, 0.5, 5.0, 7.5),
        "rainfall":    (145, 8,  120, 170),
        "samples": 110
    },
    "coconut": {
        "N":           (55, 8,   30,  80),
        "P":           (8,  3,   2,   18),
        "K":           (38, 8,   18,  60),
        "temperature": (30, 4,   20,  42),
        "humidity":    (95, 2,   88,  99),
        "ph":          (6.5, 0.8, 5.0, 8.5),
        "rainfall":    (210, 35, 130, 290),
        "samples": 110
    },
    "cotton": {
        "N":           (110, 15, 70,  150),
        "P":           (70,  12, 40,  105),
        "K":           (55,  12, 25,   90),
        "temperature": (25, 4,   16,  36),
        "humidity":    (73, 8,   55,  90),
        "ph":          (7.2, 0.6, 5.5, 8.5),
        "rainfall":    (82,  18, 45,  125),
        "samples": 110
    },
    "jute": {
        "N":           (70, 12,  40,  105),
        "P":           (48, 10,  20,   80),
        "K":           (48, 10,  20,   80),
        "temperature": (29, 4,   18,   40),
        "humidity":    (85, 5,   72,   97),
        "ph":          (6.7, 0.5, 5.5,  8.0),
        "rainfall":    (175, 25, 110,  230),
        "samples": 110
    },
    "coffee": {
        "N":           (110, 12, 80,  145),
        "P":           (10,  4,  2,   22),
        "K":           (35,  8,  15,   60),
        "temperature": (20, 4,   10,   30),
        "humidity":    (92, 3,   82,   99),
        "ph":          (6.2, 0.4, 5.5,  7.0),
        "rainfall":    (200, 30, 130,  270),
        "samples": 110
    }
}


def generate_samples(crop_name: str, params: dict) -> pd.DataFrame:
    """Generate synthetic samples for a crop using truncated normal distributions."""
    n = params.get("samples", 100)
    rows = []
    for _ in range(n):
        row = {"label": crop_name}
        for feat in ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]:
            mean, std, lo, hi = params[feat]
            val = np.random.normal(mean, std)
            val = np.clip(val, lo, hi)
            # Round appropriately
            if feat in ("ph", "temperature"):
                val = round(val, 2)
            elif feat == "humidity":
                val = round(val, 2)
            else:
                val = round(val, 1)
            row[feat] = val
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    print("=" * 60)
    print("FarmFriend AI — Synthetic Dataset Generator")
    print("=" * 60)
    print()
    print("DISCLOSURE: Generating SYNTHETIC/AUGMENTED data.")
    print("Sources: ICAR, TNAU, FAO, Kaggle Crop Recommendation Dataset")
    print()

    dfs = []
    for crop, params in CROP_PARAMS.items():
        df = generate_samples(crop, params)
        dfs.append(df)
        print(f"  Generated {len(df):4d} samples for {crop}")

    full_df = pd.concat(dfs, ignore_index=True)
    
    # Shuffle
    full_df = full_df.sample(frac=1, random_state=SEED).reset_index(drop=True)

    # Reorder columns
    cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "label"]
    full_df = full_df[cols]

    # Save CSV
    output_csv = os.path.join(OUTPUT_DIR, "crop_recommendation_synthetic.csv")
    full_df.to_csv(output_csv, index=False)
    print()
    print(f"Dataset saved to: {output_csv}")
    print(f"Total records: {len(full_df)}")
    print(f"Crops: {full_df['label'].nunique()}")
    print()

    # Class distribution
    print("Class distribution:")
    dist = full_df["label"].value_counts()
    for crop, count in dist.items():
        print(f"  {crop:<20} {count:>4} samples")

    # Save metadata
    metadata = {
        "dataset_name": "FarmFriend AI Crop Recommendation — Synthetic/Augmented",
        "nature": "SYNTHETIC",
        "disclosure": "This dataset is synthetic/augmented data generated from published agricultural literature. It is NOT real field observation data.",
        "generation_date": datetime.now().isoformat(),
        "seed": SEED,
        "total_records": int(len(full_df)),
        "n_crops": int(full_df["label"].nunique()),
        "crops": sorted(full_df["label"].unique().tolist()),
        "features": {
            "N": "Available Nitrogen in soil (kg/ha)",
            "P": "Available Phosphorus in soil (kg/ha)",
            "K": "Available Potassium in soil (kg/ha)",
            "temperature": "Temperature (degrees Celsius)",
            "humidity": "Relative Humidity (%)",
            "ph": "Soil pH (0-14 dimensionless)",
            "rainfall": "Annual Rainfall (mm)"
        },
        "target": "label (crop name)",
        "sources": [
            "ICAR crop production guides (2015-2023)",
            "TNAU crop production technology (2020)",
            "FAO crop requirements database",
            "Kaggle Crop Recommendation Dataset (Atharva Ingle, 2020) — https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset",
            "ICAR-CICR for cotton; ICAR-IIPR for pulses; ICAR-NRC Pomegranate; ICAR-NRC Grapes; Coffee Board of India"
        ],
        "known_limitations": [
            "Synthetic data — does not represent real field variability",
            "No regional breakdown (pan-India generalisation)",
            "Balanced classes (110 samples each) — real agriculture has unequal crop distributions",
            "No missing values — real data typically has missing values",
            "Only 7 features — does not include SHC micronutrients (S, Zn, Fe, Cu, Mn, B, OC, EC)",
            "No variety-level information",
            "No soil type feature in ML model — handled by rule layer"
        ]
    }

    metadata_path = os.path.join(OUTPUT_DIR, "dataset_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print()
    print(f"Metadata saved to: {metadata_path}")
    print()
    print("Dataset generation complete.")


if __name__ == "__main__":
    main()
