# BAA-2025 System Architecture

## Overview

The Bosnia & Herzegovina Antibiotic Advisor (BAA-2025) is a **deterministic, hard-coded clinical decision support system** designed to recommend antibiotics using ONLY medications registered in the Registar lijekova Bosne i Hercegovine 2025.

## Core Principles

### 1. Closed-World Assumption
- **No hallucinations permitted** - Only drugs in the BiH 2025 registry exist
- If a drug isn't in the registry, it cannot be recommended
- Automatic substitutions for unavailable international drugs (e.g., Nafcillin → Syntarpen)

### 2. Deterministic Logic
- **Hard-coded decision trees**, not probabilistic AI/ML models
- Every recommendation follows explicit clinical guidelines
- Reproducible and auditable decision paths

### 3. Brand-Specific Outputs
- Recommends exact trade names (e.g., "Longaceph", "Sumamed", "Panklav")
- Includes manufacturer information
- Provides specific formulation details (strength, route, etc.)

### 4. Regulatory Compliance
- Enforces BiH regulatory status: **ZU** (hospital-only) vs **Rp** (prescription)
- Warns when restricted antibiotics require special approval
- Prevents outpatient prescription of hospital-only drugs

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     BAA-2025 System                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Web Interface (Flask)                       │  │
│  │  - HTML/CSS/JavaScript frontend                       │  │
│  │  - RESTful API endpoints                              │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │        Clinical Decision Engine                        │  │
│  │  - Hard-coded logic trees                             │  │
│  │  - Scenario-specific algorithms                       │  │
│  │    • CAP Logic                                        │  │
│  │    • HAP/VAP Logic                                    │  │
│  │    • UTI Logic                                        │  │
│  │    • Meningitis Logic                                 │  │
│  │    • Sepsis Logic                                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Drug Registry Service                          │  │
│  │  - Query engine for BiH 2025 registry                │  │
│  │  - Availability checking                              │  │
│  │  - Substitution mapping                               │  │
│  │  - Formulation lookup                                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Drug Registry Database (JSON)                  │  │
│  │  - Beta-lactams (penicillins, cephalosporins)        │  │
│  │  - Carbapenems & fluoroquinolones                     │  │
│  │  - Macrolides, aminoglycosides, glycopeptides         │  │
│  │  - Antifungals & antivirals                           │  │
│  │  Total: 1000+ formulations                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Models

### Patient Model
```python
Patient
├── demographics (age, gender, weight, pregnancy status)
├── physiology (CrCl, liver function, albumin)
└── allergies (drug class, type, severity)
```

### Infection Model
```python
InfectionProfile
├── site (CAP, UTI, meningitis, etc.)
├── acquisition (community vs. hospital)
├── severity (mild, moderate, severe, critical)
├── sepsis_classification (Sepsis-3 criteria)
└── resistance_risk (MDR risk factors)
```

### Prescription Model
```python
Prescription
├── clinical_assessment
├── primary_recommendation
│   ├── generic_name
│   ├── trade_names (BiH brands)
│   ├── formulation
│   ├── dose_calculation
│   │   ├── dose_amount
│   │   ├── frequency
│   │   ├── duration
│   │   └── adjustments (renal, hepatic, pediatric)
│   ├── regulatory_status (ZU/Rp)
│   └── safety_warnings
├── alternative_recommendations
└── follow-up_guidance
```

## Clinical Decision Logic

### Example: Community-Acquired Pneumonia (CAP)

```
INPUT: Patient + Infection Profile
  ↓
CHECK: Severity (mild/moderate vs. severe)
  ↓
IF SEVERE:
  → Hospitalized → IV therapy
  → Primary: Ceftriaxone 2g IV q24h (Brands: Longaceph, Azaran)
  → Add: Azithromycin for atypical coverage
  → Alternative (if β-lactam allergy): Levofloxacin
  ↓
IF MILD-MODERATE:
  → Outpatient → Oral therapy
  → Primary: Amoxicillin 1000mg PO q8h (Brands: Amoxibos, Sinacillin)
  → Alternative (atypical): Azithromycin 500mg daily x3
  → Alternative (allergy): Doxycycline
  ↓
CHECK: BiH Availability
  → Verify all drugs in registry
  → Substitute if necessary
  ↓
CALCULATE DOSES:
  → Pediatric: Weight-based (mg/kg)
  → Renal impairment: CrCl-adjusted
  → Hepatic impairment: Child-Pugh adjusted
  ↓
GENERATE PRESCRIPTION:
  → Exact brand names
  → Formulation details
  → Prescription instructions
  → Patient counseling
  ↓
OUTPUT: Complete Prescription
```

## Drug Registry Structure

### JSON Format
```json
{
  "metadata": {
    "registry_version": "2025",
    "country": "Bosnia and Herzegovina"
  },
  "drugs": {
    "generic_name": "Ceftriakson",
    "trade_name": "LONGACEPH",
    "manufacturer": "Medochemie",
    "atc_code": "J01DD04",
    "regulatory_status": "ZU/Rp",
    "formulations": [
      {
        "type": "powder_for_injection",
        "strength": "1g",
        "route": "intravenous"
      }
    ],
    "indications": ["Meningitis", "CAP", "Pyelonephritis"],
    "clinical_notes": "Meningitis dose: 2g q12h"
  }
}
```

## Safety Features

### 1. Allergy Checking
- Detects β-lactam cross-reactivity
- Differentiates Type I (anaphylaxis) from Type IV (delayed) reactions
- Automatically selects non-cross-reactive alternatives

### 2. Dose Adjustments
- **Renal:** Cockcroft-Gault equation for CrCl
- **Hepatic:** Child-Pugh classification
- **Pediatric:** Weight-based (mg/kg) with age-appropriate formulations
- **Obesity:** Adjusted dosing for aminoglycosides, vancomycin

### 3. Drug Interactions
- QT prolongation (fluoroquinolones + azithromycin)
- Statin interactions (clarithromycin)
- Warfarin interactions

### 4. Regulatory Safeguards
- **ZU drugs:** Locked to hospital pharmacy requisition
- **Reserved antibiotics:** Require microbiology confirmation (e.g., Colistin, Zavicefta)
- **Controlled substances:** Flagged for special prescription requirements

## API Endpoints

### POST /api/recommend
Generate antibiotic recommendation

**Request:**
```json
{
  "patient": {
    "demographics": {...},
    "physiology": {...},
    "allergies": [...]
  },
  "infection": {
    "site": "community_acquired_pneumonia",
    "severity": "moderate"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "recommendation": {
    "diagnosis": "Community-Acquired Pneumonia",
    "primary_recommendation": {
      "generic_name": "Amoksicilin",
      "trade_names": ["Amoxibos", "Sinacillin", "Almacin"],
      "dose": "1000mg PO q8h for 5 days"
    }
  }
}
```

### GET /api/drugs/search?generic={name}
Search drugs by generic name

### GET /api/drugs/antipseudomonal
List all antipseudomonal drugs

### GET /api/drugs/anti-mrsa
List all anti-MRSA drugs

## Deployment

### Requirements
- Python 3.9+
- Flask 3.0+
- Pydantic 2.5+ (data validation)
- 100MB storage (drug registry + code)

### Installation
```bash
pip install -r requirements.txt
python run.py
```

### Production
- Use Gunicorn/uWSGI for production WSGI server
- Nginx reverse proxy
- Docker containerization supported

## Testing

### Unit Tests
- Drug registry queries
- Dose calculations
- Allergy checking

### Integration Tests
- Clinical scenario end-to-end tests
- API endpoint tests

### Clinical Validation
- Scenarios validated against:
  - IDSA/ATS guidelines
  - EAU guidelines
  - Local BiH protocols

## Future Enhancements

1. **Extended Scenarios:** Bone/joint infections, endocarditis, fungal infections
2. **Mobile App:** Native iOS/Android applications
3. **EMR Integration:** HL7 FHIR integration for hospital systems
4. **Antibiogram Integration:** Local resistance pattern data
5. **Multi-language Support:** Bosnian, Serbian, Croatian interfaces

## References

1. Registar lijekova Bosne i Hercegovine 2025
2. IDSA/ATS Community-Acquired Pneumonia Guidelines 2019
3. IDSA/ATS Hospital-Acquired Pneumonia Guidelines 2016
4. IDSA Urinary Tract Infection Guidelines 2011
5. Sepsis-3 Definitions (JAMA 2016)
6. EAU Guidelines on Urological Infections 2024

---

**Version:** 1.0.0
**Last Updated:** December 2025
**Maintained by:** BAA-2025 Development Team
