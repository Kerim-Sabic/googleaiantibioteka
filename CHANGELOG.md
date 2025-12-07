# Changelog

All notable changes to the BAA-2025 project will be documented in this file.

## [1.0.0] - 2025-12-07

### Added
- **Complete drug registry database** covering 1000+ formulations from BiH 2025 registry
  - Beta-lactams (penicillins, cephalosporins, carbapenems)
  - Fluoroquinolones
  - Macrolides, aminoglycosides, glycopeptides
  - Antifungals (azoles, echinocandins, polyenes)
  - Antivirals (HIV, HCV, influenza agents)

- **Data models** using Pydantic for validation
  - Patient model (demographics, physiology, allergies)
  - Infection profile model (site, severity, resistance patterns)
  - Prescription model (recommendations, dosing, safety warnings)

- **Drug registry service**
  - Query engine for BiH 2025 registry
  - Closed-world assumption enforcement (no hallucinations)
  - Automatic drug substitution mapping (e.g., Nafcillin → Syntarpen)
  - Formulation lookup and availability checking

- **Clinical decision engine** with hard-coded logic trees
  - Community-Acquired Pneumonia (CAP) logic
  - Pyelonephritis logic
  - Ventilator-Associated Pneumonia (VAP) logic
  - Automatic severity stratification
  - MDR risk calculation

- **Dose calculation capabilities**
  - Pediatric weight-based dosing
  - Renal adjustment (Cockcroft-Gault CrCl)
  - Extended infusion recommendations for critically ill patients

- **Safety features**
  - Allergy cross-reactivity checking
  - β-lactam allergy detection and alternative selection
  - QT prolongation warnings
  - Drug interaction alerts

- **Flask web application**
  - RESTful API endpoints
  - HTML/CSS/JavaScript frontend
  - Interactive API testing interface

- **Comprehensive documentation**
  - README with feature overview
  - ARCHITECTURE.md with system design details
  - Example scripts demonstrating usage

### Technical Details
- Python 3.9+ with Flask 3.0
- Pydantic for data validation
- Structured JSON drug registry
- Modular architecture (models, services, routes)

### Registry Coverage
- **Penicillins:** Amoxicillin, Ampicillin, Cloxacillin, Co-amoxiclav, Piperacillin/Tazobactam
- **Cephalosporins:** 1st-5th generation (Cefazolin → Ceftazidim/Avibaktam)
- **Carbapenems:** Meropenem, Imipenem, Ertapenem
- **Fluoroquinolones:** Ciprofloxacin, Levofloxacin, Moxifloxacin
- **Glycopeptides:** Vancomycin, Teicoplanin
- **Macrolides:** Azithromycin (Sumamed), Clarithromycin
- **Aminoglycosides:** Gentamicin, Amikacin, Tobramycin
- **Last-line agents:** Colistin, Linezolid, Tigecycline
- **Antifungals:** Fluconazole, Voriconazole, Caspofungin, Amphotericin B
- **Antivirals:** Complete HIV ART panel, HCV DAAs, Influenza agents

### Clinical Scenarios Implemented
- ✅ Community-Acquired Pneumonia (mild, moderate, severe)
- ✅ Hospital-Acquired Pneumonia / VAP
- ✅ Acute Pyelonephritis
- ⏳ Bacterial Meningitis (partial)
- ⏳ Otitis Media (partial)
- ⏳ Uncomplicated Cystitis (partial)
- ⏳ Cellulitis (partial)

### Known Limitations
- Additional clinical scenarios require implementation
- Pediatric dosing formulas need expansion
- Therapeutic drug monitoring (TDM) targets need integration
- Local antibiogram data not yet integrated

### Future Enhancements
- Extended clinical scenario coverage
- Mobile application development
- EMR/EHR integration (HL7 FHIR)
- Local resistance pattern integration
- Multi-language support (Bosnian, Serbian, Croatian)

---

[1.0.0]: https://github.com/Kerim-Sabic/googleaiantibioteka/releases/tag/v1.0.0
