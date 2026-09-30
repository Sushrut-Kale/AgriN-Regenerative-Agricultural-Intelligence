# 🌐 AgriN — Multilingual & Localization Architecture

> **Document Version:** 1.0.0 (Phase 2.5)  
> **Status:** Active Standard & Implementation Specification  
> **Target Scope:** 12 Official Indian Languages across 28 States & 8 UTs

---

## 1. Core Architectural Principle: Decoupling Knowledge from Language

In multilingual systems, a common anti-pattern is duplicating agronomic rules, threshold tables, and scoring logic for each supported language. This leads to drift, inconsistency, and maintenance failure.

AgriN adheres strictly to:
$$\text{Single Agronomic Source of Truth} \longrightarrow \text{Language-Agnostic Advisory JSON} \longrightarrow \text{Localization Rendering Layer}$$

Agronomic calculations, soil chemistry boundaries, and machine learning inferences execute in a language-neutral domain. **Language is purely a presentation layer concern.**

```text
┌────────────────────────────────────────────────────────┐
│             Agronomic Knowledge & ML Core              │
│       (Language-Agnostic Physics, Chemistry, Code)     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│              Canonical Advisory Object                 │
│         (Structured JSON: reasoning, actions)          │
└──────────────────────────┬─────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌─────────────────────┐             ┌─────────────────────┐
│ String Localization │             │ LLM Multilingual    │
│  (UI Labels, Units, │             │ Natural Language    │
│   Pre-translated    │             │ Rendering (Context- │
│     Glossary)       │             │   Aware Synthesis)  │
└────────┬────────────┘             └────────┬────────────┘
         │                                   │
         └─────────────────┬─────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               Farmer Interface Rendering               │
│ (Hindi / Marathi / Tamil / Telugu / Kannada / Bengali) │
└────────────────────────────────────────────────────────┘
```

---

## 2. Supported Languages Matrix (12 Indian Languages)

| Language | Script | Primary States / UTs | ISO 639-1 / 639-2 |
| :--- | :--- | :--- | :--- |
| **English** | Latin | Pan-India (Technical default) | `en` |
| **Hindi** (हिन्दी) | Devanagari | UP, MP, Rajasthan, Bihar, Haryana, Delhi, HP, Uttarakhand | `hi` |
| **Marathi** (मराठी) | Devanagari | Maharashtra, Goa | `mr` |
| **Tamil** (தமிழ்) | Tamil | Tamil Nadu, Puducherry | `ta` |
| **Telugu** (తెలుగు) | Telugu | Andhra Pradesh, Telangana | `te` |
| **Kannada** (ಕನ್ನಡ) | Kannada | Karnataka | `kn` |
| **Bengali** (বাংলা) | Bengali | West Bengal, Tripura, Assam (Barak Valley) | `bn` |
| **Gujarati** (ગુજરાતી) | Gujarati | Gujarat, Dadra and Nagar Haveli and Daman and Diu | `gu` |
| **Punjabi** (ਪੰਜਾਬੀ) | Gurmukhi | Punjab, Haryana, Chandigarh | `pa` |
| **Malayalam** (മലയാളം)| Malayalam | Kerala, Lakshadweep | `ml` |
| **Odia** (ଓଡ଼ିଆ) | Odia | Odisha | `or` |
| **Assamese** (অসমীয়া) | Bengali-Assamese | Assam | `as` |

---

## 3. Localization Data Structure

### 3.1 Agronomic Terminology Glossary (`knowledge/i18n/glossary.json`)
Maintains official standard terms vetted by State Agricultural Universities (SAUs) and ICAR:

```json
{
  "terms": {
    "available_nitrogen": {
      "en": "Available Nitrogen",
      "hi": "उपलब्ध नाइट्रोजन",
      "mr": "उपलब्ध नत्र",
      "ta": "கிடைக்கும் நைட்ரஜன்",
      "te": "లభ్య నత్రజని",
      "kn": "ಲಭ್ಯವಿರುವ ಸಾರಜನಕ"
    },
    "soil_health_card": {
      "en": "Soil Health Card",
      "hi": "मृदा स्वास्थ्य कार्ड",
      "mr": "मृदा आरोग्य पत्रिका",
      "ta": "மண் வள அட்டை",
      "te": "నేల ఆరోగ్య కార్డు",
      "kn": "ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಕಾರ್ಡ್"
    },
    "crop_rotation": {
      "en": "Crop Rotation",
      "hi": "फसल चक्र",
      "mr": "पीक फेरपालट",
      "ta": "பயிர் சுழற்சி",
      "te": "పంట మార్పిడి",
      "kn": "ಬೆಳೆ ಪರಿವರ್ತನೆ"
    }
  }
}
```

---

## 4. Multi-Modal Audio & Voice Extension (Future Track 4 Readiness)

Over 65% of smallholder farmers in India consume advisories via voice notes or WhatsApp audio clips rather than reading detailed written reports.

The Multilingual Architecture will connect:
1. **Advisory JSON $\rightarrow$ Localized Text (TTS Ready)**
2. **Text-to-Speech (TTS):** Integration with Bhashini (Government of India AI for Bharat open language models) to synthesize regional voice advisories in natural Indian accents.
3. **Voice Queries (STT):** Inbound farmer queries in Hindi, Marathi, or Tamil transcribed via Bhashini ASR before parsing into standard `FarmDataInput`.
