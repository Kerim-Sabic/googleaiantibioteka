# Bosnia & Herzegovina Antibiotic Advisor (BAA-2025)

[![Netlify Status](https://img.shields.io/badge/Netlify-Ready-00C7B7?logo=netlify)](https://www.netlify.com)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Clinical%20Use-blue)](LICENSE)

## Executive Summary

The BAA-2025 is a hospital-grade, deterministic clinical decision support system designed specifically for Bosnia and Herzegovina healthcare providers. Unlike probabilistic AI models, this system operates on a **"Closed-World Assumption"** - recommending ONLY medications registered in the **Registar lijekova Bosne i Hercegovine 2025**.

**Key Innovation**: Zero hallucinations. The system automatically substitutes unavailable international drugs (e.g., Nafcillin → Kloksacilin/Syntarpen) without user intervention, bridging the gap between global guidelines and local availability.

## 🚀 Quick Deploy

### Deploy to Netlify (Recommended)

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Kerim-Sabic/googleaiantibioteka)

**Steps:**
1. Click the button above (or manually add the repo in Netlify)
2. Configure build settings:
   - **Publish directory**: `public`
   - **Functions directory**: `netlify/functions`
3. Deploy!

Your site will be live at `https://[your-site-name].netlify.app`

**Full deployment guide**: See [NETLIFY_DEPLOYMENT.md](NETLIFY_DEPLOYMENT.md)

## Key Features

### 🎯 Deterministic, Not Probabilistic
- **Zero hallucinations**: Only recommends drugs actually available in BiH
- **Hard-coded substitutions**: Automatically replaces unavailable international drugs (e.g., Nafcillin → Kloksacilin/Syntarpen)
- **Brand-specific outputs**: Provides exact trade names, manufacturers, and formulations

### 🏥 Hospital-Grade Clinical Logic
- **Regulatory awareness**: Distinguishes between ZU (hospital-only) and Rp (prescription) drugs
- **Automatic dose calculations**: Pediatric weight-based, renal adjustments, hepatic dosing
- **Severity stratification**: Uses Sepsis-3/SOFA criteria for ICU recommendations
- **Supply chain validation**: Ensures every recommendation is executable in BiH hospitals

### 📊 Comprehensive Coverage
- **1000+ registered formulations** from BiH 2025 registry
- **All major drug classes**: β-lactams, fluoroquinolones, carbapenems, antifungals, antivirals
- **Clinical scenarios**: CAP, HAP/VAP, UTI, meningitis, sepsis, pediatric infections, and more

## System Architecture

```
BAA-2025/
├── app/
│   ├── models/          # Data models (Patient, Drug, Prescription)
│   ├── services/        # Clinical decision engine
│   ├── routes/          # API endpoints
│   ├── utils/           # Dose calculators, validators
│   └── templates/       # Web UI
├── data/
│   ├── registry/        # BiH drug database (structured JSON)
│   └── clinical_protocols/  # Decision trees and algorithms
├── tests/               # Clinical scenario test suite
└── config/              # Application configuration
```

## Clinical Logic Philosophy

### The "Hard-Coded" Approach
In clinical settings, **hallucination is malpractice**. The BAA-2025 enforces strict business rules:

1. **Closed-World Pharmacy**: If a drug isn't in the 2025 registry, it doesn't exist
2. **Automatic Substitution**: International guidelines → Local equivalents
3. **Regulatory Compliance**: ZU drugs locked behind hospital pharmacy workflows
4. **Safety-First**: Automatic allergy checking, interaction warnings, dose adjustments

### Example Workflow

**Input:**
- Patient: 35-year-old male, 75kg, CrCl 90 mL/min
- Diagnosis: Community-Acquired Pneumonia (CAP)
- Severity: CURB-65 = 2 (moderate)
- Allergies: None

**Output:**
```
Clinical Assessment: Moderate CAP requiring antibiotic therapy

Primary Recommendation:
Drug: Amoksicilin (Brands: Amoxibos, Sinacillin, Almacin, Hiconcil)
Formulation: 500mg Capsules
Dose & Frequency: 1000mg PO every 8 hours
Duration: 5-7 days
Regulatory Status: Rp (Standard Prescription)

Alternative (if atypical pathogen suspected):
Drug: Azitromicin (Brands: Sumamed, Hemomycin)
Formulation: 500mg Tablets
Dose & Frequency: 500mg PO once daily
Duration: 3 days

Prescription Guide:
☑ Prescribe: Amoksicilin 500mg capsules #21 (7-day course)
☑ Instructions: Take 2 capsules (1000mg) every 8 hours with food
```

## Technology Stack

- **Backend**: Python 3.9+ with Flask
- **Data**: Structured JSON registry + SQLite for session management
- **Clinical Engine**: Pure Python decision trees
- **Frontend**: HTML5, CSS3, JavaScript (no framework dependencies)
- **Deployment**: Docker containerization ready

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize drug database
python scripts/init_database.py

# Run development server
python run.py

# Access at http://localhost:5000
```

## Drug Registry Coverage

### Beta-Lactams (J01C, J01D)
- **Penicillins**: Benzilpenicilin, Amoxicillin, Ampicillin, Co-amoxiclav, Piperacillin/Tazobactam
- **Cephalosporins**: Generations 1-5 (Cefazolin → Ceftazidim/Avibaktam)
- **Carbapenems**: Meropenem, Imipenem, Ertapenem, Imipenem/Relebactam

### Fluoroquinolones (J01M)
- Ciprofloxacin, Levofloxacin, Moxifloxacin, Norfloxacin

### Other Antibacterials
- **Macrolides**: Azithromycin (Sumamed!), Clarithromycin, Erythromycin
- **Aminoglycosides**: Gentamicin, Amikacin, Tobramycin
- **Glycopeptides**: Vancomycin, Teicoplanin
- **Oxazolidinones**: Linezolid
- **Last-line**: Colistin, Tigecycline

### Antifungals (J02)
- Fluconazole, Voriconazole, Caspofungin, Amphotericin B

### Antivirals (J05)
- HIV: TRUVADA, TRIUMEQ, GENVOYA, DOVATO
- HCV: MAVIRET, EPCLUSA
- Influenza: XOFLUZA

## Safety Features

### Automatic Checks
- ✅ Allergy cross-reactivity (β-lactam cross-sensitivity)
- ✅ Renal dose adjustment (CrCl-based)
- ✅ Hepatic dosing (Child-Pugh scoring)
- ✅ Pregnancy category warnings (FDA → BiH mapping)
- ✅ QT prolongation risks (fluoroquinolones, azithromycin)
- ✅ Drug-drug interactions (e.g., statins + clarithromycin)

### Regulatory Safeguards
- **ZU drugs**: Require hospital pharmacy approval
- **Controlled substances**: Flagged for special prescription requirements
- **Restricted antibiotics**: Locked behind microbiology confirmation (e.g., Colistin, Zavicefta)

## Clinical Scenarios Implemented

1. **Respiratory**: CAP, HAP, VAP, acute bronchitis, pneumonia
2. **Urinary**: Uncomplicated cystitis, pyelonephritis, prostatitis
3. **Skin/Soft Tissue**: Cellulitis, abscess, diabetic foot, necrotizing fasciitis
4. **CNS**: Bacterial meningitis, brain abscess
5. **Intra-abdominal**: Peritonitis, cholecystitis, diverticulitis
6. **Sepsis**: SIRS, sepsis, septic shock (Sepsis-3 criteria)
7. **Pediatric**: Otitis media, pharyngitis, UTI
8. **Special Populations**: Neutropenic fever, immunocompromised, pregnancy

## Contribution Guidelines

This is a **data-driven system**. Contributions must:
1. Reference the official Registar lijekova BiH 2025
2. Include clinical evidence (local guidelines or international standards)
3. Provide test cases for new clinical scenarios
4. Maintain the "zero hallucination" principle

## License

**Clinical Use Only**: This system is intended for licensed healthcare providers in Bosnia and Herzegovina. Not for direct patient use.

## Contact & Support

For clinical questions, registry updates, or bug reports, please open an issue on GitHub.

---

**Version**: 1.0.0 (2025-BAA)
**Last Updated**: December 2025
**Registry Base**: Registar lijekova Bosne i Hercegovine 2025
