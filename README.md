# 🌾 AgriN — Regenerative Agricultural Intelligence

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_19_+_Vite-61DAFB.svg?style=flat&logo=react)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-F7931E.svg?style=flat&logo=scikit-learn)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-134%20Passed-brightgreen.svg)]()
[![BRICS Interoperability](https://img.shields.io/badge/BRICS_Track_4-Hardened-blueviolet.svg)]()
[![Pan-India](https://img.shields.io/badge/Coverage-28%20States%20%2B%208%20UTs-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()

> **"BRICS Track 4 — AgriN & Regenerative Agricultural Intelligence Network."**  
> An end-to-end, scientifically honest agronomic decision-support platform designed for localized agricultural intelligence across all 28 Indian States and 8 Union Territories (15 ICAR Agro-Climatic Zones), integrating satellite-derived vegetation indicators, Soil Health Card diagnostics, multi-source weather telemetry, plant pathology triage, and multi-horizon regenerative practices with a canonical country-neutral data exchange architecture for BRICS agricultural cooperation.

## 🧭 About

AgriN is a regenerative agricultural intelligence platform built to help farmers, agronomists, and institutions make better crop and soil decisions with evidence-backed insights. The system combines agronomic rules, climate and soil diagnostics, live weather data, and machine learning to recommend suitable crops, identify limiting factors, and suggest practical action plans for healthier and more resilient farming systems.

At its core, AgriN focuses on accessible, explainable agricultural intelligence for India’s diverse agro-climatic regions. It supports location-aware assessments, field-level soil testing, feasibility checks, climate simulations, and regenerative practice recommendations — while keeping recommendations grounded in scientific reasoning and transparent decision support rather than opaque black-box outputs.

---

## 📑 Table of Contents
- [About](#-about)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Pan-India Geographic Hierarchy](#-pan-india-geographic-hierarchy)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Quick Start Guide](#-quick-start-guide)
  - [Prerequisites](#prerequisites)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Frontend Setup](#2-frontend-setup)
  - [3. Running the Application](#3-running-the-application)
- [Machine Learning & Explainability](#-machine-learning--explainability)
- [API Reference](#-api-reference)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Documentation Directory](#-documentation-directory)
- [Disclaimer](#-disclaimer)

---

## ✨ Key Features

1. **🌾 Pan-India Location-Aware Farm Assessment Wizard**:
   - Hierarchy: **India → State/UT (36) → District → Sub-District (Taluka/Tehsil/Block) → Village → Farm**.
   - 📍 **GPS Geolocation**: 1-click detection resolving coordinates, nearest district, state, and Agro-Climatic Zone.
   - Soil Health Card (SHC) test parameters (N, P, K, pH, EC, OC, Micronutrients: Zn, Fe, Cu, Mn, B, S).
   - Dynamic real-time weather & seasonal rainfall telemetry via Open-Meteo API for any Indian coordinate.

2. **📊 Multi-Crop Suitability Scoring & ML Predictions**:
   - Multi-class Random Forest model recommending top suitable crops for the farmer's specific conditions.
   - Dual-layer validation: Machine Learning probability blended with deterministic Agronomic Rule-Based feasibility filters (ICAR/TNAU).

3. **🔍 Transparent Explainable AI (SHAP & Factor Breakdown)**:
   - Visual SHAP feature importance breakdown explaining *why* a crop was recommended or rejected.
   - Clear identification of **Supporting Factors** (e.g., optimal potassium, favorable temperature) vs. **Limiting Factors** (e.g., low nitrogen, alkaline pH).
   - Actionable fertilizer and soil amendment advice tailored to the exact field deficit.

4. **🎯 "I Want To Grow" Crop Feasibility Checker**:
   - Allows farmers to select any specific target crop (e.g., Cotton, Soybean, Chickpea, Rice, Coffee) to evaluate its feasibility against their farm's current soil & climate.
   - Provides an immediate feasibility gauge, limiting factor alerts, and remedy recommendations.

5. **⚡ Interactive "What-If" Soil & Climate Simulator**:
   - Dynamic real-time sliders allowing farmers to simulate changes (e.g., *"What if I apply 50 kg/ha more Nitrogen?"* or *"What if rainfall drops by 20%?"*).
   - Instant delta score recalculation and sensitivity analysis.

6. **📈 Telemetry & Analytics Dashboard**:
   - Tracks total analyses, feasibility assessments, and what-if experiments.
   - Displays ML model metrics (Accuracy, Precision, Recall, F1-score) and side-by-side benchmark comparisons against baseline algorithms.

7. **💬 Ground-Truth Feedback Loop**:
   - In-app farmer feedback collection to track real-world crop outcomes and continuously refine models.

---

## 🏛 System Architecture
