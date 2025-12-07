"""
Infection Profile Models

Represents infection site, severity, and clinical context for antibiotic selection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class InfectionSite(str, Enum):
    """Anatomical site of infection"""
    # Respiratory
    PHARYNGITIS = "pharyngitis"
    OTITIS_MEDIA = "otitis_media"
    SINUSITIS = "sinusitis"
    ACUTE_BRONCHITIS = "acute_bronchitis"
    CAP = "community_acquired_pneumonia"
    HAP = "hospital_acquired_pneumonia"
    VAP = "ventilator_associated_pneumonia"

    # Urinary
    CYSTITIS_UNCOMPLICATED = "cystitis_uncomplicated"
    CYSTITIS_COMPLICATED = "cystitis_complicated"
    PYELONEPHRITIS = "pyelonephritis"
    PROSTATITIS = "prostatitis"

    # Skin/Soft Tissue
    IMPETIGO = "impetigo"
    CELLULITIS = "cellulitis"
    ERYSIPELAS = "erysipelas"
    ABSCESS = "abscess"
    DIABETIC_FOOT = "diabetic_foot_infection"
    NECROTIZING_FASCIITIS = "necrotizing_fasciitis"

    # CNS
    MENINGITIS = "bacterial_meningitis"
    BRAIN_ABSCESS = "brain_abscess"

    # Intra-abdominal
    PERITONITIS = "peritonitis"
    CHOLECYSTITIS = "cholecystitis"
    DIVERTICULITIS = "diverticulitis"
    INTRA_ABDOMINAL_ABSCESS = "intra_abdominal_abscess"

    # Bone/Joint
    OSTEOMYELITIS = "osteomyelitis"
    SEPTIC_ARTHRITIS = "septic_arthritis"

    # Cardiovascular
    ENDOCARDITIS_NATIVE = "endocarditis_native_valve"
    ENDOCARDITIS_PROSTHETIC = "endocarditis_prosthetic_valve"
    CATHETER_RELATED_BSI = "catheter_related_bloodstream_infection"

    # Systemic
    SEPSIS = "sepsis"
    SEPTIC_SHOCK = "septic_shock"
    NEUTROPENIC_FEVER = "neutropenic_fever"

    # STIs
    GONORRHEA = "gonorrhea"
    SYPHILIS = "syphilis"
    CHLAMYDIA = "chlamydia"

    # Other
    CLOSTRIDIOIDES_DIFFICILE = "clostridioides_difficile"
    OTHER = "other"


class InfectionAcquisition(str, Enum):
    """Where infection was acquired"""
    COMMUNITY = "community_acquired"
    HOSPITAL = "hospital_acquired"
    HEALTHCARE_ASSOCIATED = "healthcare_associated"


class InfectionSeverity(str, Enum):
    """Clinical severity assessment"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class SepsisClassification(str, Enum):
    """Sepsis-3 classification"""
    NO_SEPSIS = "no_sepsis"
    SIRS = "sirs"
    SEPSIS = "sepsis"
    SEPTIC_SHOCK = "septic_shock"


class PathogenClass(str, Enum):
    """Expected pathogen classes"""
    GRAM_POSITIVE = "gram_positive"
    GRAM_NEGATIVE = "gram_negative"
    ANAEROBIC = "anaerobic"
    ATYPICAL = "atypical"
    FUNGAL = "fungal"
    MIXED = "mixed"


class ResistancePattern(str, Enum):
    """Known or suspected resistance patterns"""
    NONE = "none"
    MRSA = "mrsa"
    ESBL = "esbl"
    CRE = "cre"
    MDR_PSEUDOMONAS = "mdr_pseudomonas"
    VRE = "vre"


class InfectionProfile(BaseModel):
    """
    Complete infection characterization for antibiotic selection
    """
    # Core identification
    site: InfectionSite = Field(..., description="Anatomical site of infection")
    acquisition: InfectionAcquisition = Field(..., description="Where infection acquired")
    severity: InfectionSeverity = Field(..., description="Clinical severity")

    # Sepsis assessment
    sepsis_classification: Optional[SepsisClassification] = Field(None, description="Sepsis-3 classification")
    sofa_score: Optional[int] = Field(None, ge=0, le=24, description="Sequential Organ Failure Assessment score")
    qsofa_score: Optional[int] = Field(None, ge=0, le=3, description="Quick SOFA score")

    # Microbiology
    suspected_pathogens: List[PathogenClass] = Field(default_factory=list, description="Suspected pathogen classes")
    culture_obtained: bool = Field(False, description="Culture specimens obtained")
    culture_results: Optional[str] = Field(None, description="Culture results if available")
    antibiogram_available: bool = Field(False, description="Antibiogram available")

    # Resistance
    suspected_resistance: ResistancePattern = Field(default=ResistancePattern.NONE, description="Suspected resistance")
    prior_colonization: List[ResistancePattern] = Field(default_factory=list, description="Prior colonization history")

    # Risk factors
    recent_hospitalization: bool = Field(False, description="Hospitalized in last 90 days")
    recent_antibiotics: bool = Field(False, description="Antibiotics in last 30 days")
    immunocompromised: bool = Field(False, description="Immunocompromised status")
    chronic_dialysis: bool = Field(False, description="Chronic hemodialysis")
    indwelling_devices: List[str] = Field(default_factory=list, description="Indwelling devices (catheters, etc.)")

    # Clinical presentation
    duration_days: Optional[int] = Field(None, ge=0, description="Duration of symptoms in days")
    fever_present: bool = Field(False, description="Fever documented")
    max_temperature_c: Optional[float] = Field(None, ge=35.0, le=43.0, description="Maximum temperature (°C)")
    hypotension: bool = Field(False, description="Hypotension present")
    altered_mental_status: bool = Field(False, description="Altered mental status")

    def calculate_mdr_risk(self) -> str:
        """
        Calculate multidrug-resistant organism risk

        Returns:
            Risk level: "low", "moderate", "high"
        """
        risk_factors = 0

        if self.acquisition in [InfectionAcquisition.HOSPITAL, InfectionAcquisition.HEALTHCARE_ASSOCIATED]:
            risk_factors += 2

        if self.recent_hospitalization:
            risk_factors += 1

        if self.recent_antibiotics:
            risk_factors += 1

        if self.chronic_dialysis:
            risk_factors += 1

        if self.immunocompromised:
            risk_factors += 1

        if len(self.indwelling_devices) > 0:
            risk_factors += 1

        if self.suspected_resistance != ResistancePattern.NONE:
            risk_factors += 2

        if risk_factors == 0:
            return "low"
        elif risk_factors <= 2:
            return "moderate"
        else:
            return "high"

    def is_septic(self) -> bool:
        """Determine if patient meets sepsis criteria"""
        return self.sepsis_classification in [SepsisClassification.SEPSIS, SepsisClassification.SEPTIC_SHOCK]

    def requires_broad_spectrum(self) -> bool:
        """Determine if broad-spectrum empiric therapy indicated"""
        return (
            self.severity in [InfectionSeverity.SEVERE, InfectionSeverity.CRITICAL] or
            self.is_septic() or
            self.calculate_mdr_risk() == "high" or
            self.immunocompromised
        )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


# Example usage
if __name__ == "__main__":
    # Example: Severe CAP with sepsis
    infection = InfectionProfile(
        site=InfectionSite.CAP,
        acquisition=InfectionAcquisition.COMMUNITY,
        severity=InfectionSeverity.SEVERE,
        sepsis_classification=SepsisClassification.SEPSIS,
        sofa_score=4,
        qsofa_score=2,
        suspected_pathogens=[PathogenClass.GRAM_POSITIVE, PathogenClass.ATYPICAL],
        culture_obtained=True,
        fever_present=True,
        max_temperature_c=39.5,
        duration_days=3
    )

    print(f"Infection: {infection.site}")
    print(f"MDR Risk: {infection.calculate_mdr_risk()}")
    print(f"Is septic: {infection.is_septic()}")
    print(f"Requires broad spectrum: {infection.requires_broad_spectrum()}")
