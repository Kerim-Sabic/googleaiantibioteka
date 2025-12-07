"""
Patient Data Models

Represents patient demographics, physiological parameters, and clinical metadata
required for antibiotic selection and dosing.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
from datetime import date


class Gender(str, Enum):
    """Patient gender"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class PregnancyStatus(str, Enum):
    """Pregnancy status for female patients"""
    NOT_PREGNANT = "not_pregnant"
    PREGNANT = "pregnant"
    LACTATING = "lactating"
    UNKNOWN = "unknown"


class AllergyType(str, Enum):
    """Type of allergic reaction"""
    TYPE_I_ANAPHYLAXIS = "type_i_anaphylaxis"  # IgE-mediated, severe
    TYPE_IV_DELAYED = "type_iv_delayed"        # T-cell mediated, less severe
    INTOLERANCE = "intolerance"                # Non-allergic adverse reaction
    UNKNOWN = "unknown"


class AllergyProfile(BaseModel):
    """Patient allergy information"""
    drug_class: str = Field(..., description="Drug class (e.g., 'penicillin', 'sulfonamide')")
    specific_drug: Optional[str] = Field(None, description="Specific drug name if known")
    allergy_type: AllergyType = Field(..., description="Type of allergic reaction")
    description: Optional[str] = Field(None, description="Clinical description of reaction")


class ChildPughScore(str, Enum):
    """Child-Pugh classification for hepatic function"""
    A = "A"  # Well-compensated
    B = "B"  # Significant functional compromise
    C = "C"  # Decompensated


class PatientDemographics(BaseModel):
    """Patient demographic information"""
    age_years: int = Field(..., ge=0, le=120, description="Patient age in years")
    age_months: Optional[int] = Field(None, ge=0, le=11, description="Additional months for pediatric patients")
    gender: Gender
    weight_kg: float = Field(..., gt=0, le=300, description="Patient weight in kilograms")
    height_cm: Optional[float] = Field(None, gt=0, le=250, description="Patient height in centimeters")
    pregnancy_status: Optional[PregnancyStatus] = Field(None, description="Pregnancy status (female patients)")

    @validator('pregnancy_status')
    def validate_pregnancy(cls, v, values):
        """Pregnancy status only relevant for female patients"""
        if v and v != PregnancyStatus.NOT_PREGNANT:
            if values.get('gender') != Gender.FEMALE:
                raise ValueError("Pregnancy status only applicable to female patients")
        return v

    @property
    def is_pediatric(self) -> bool:
        """Determine if patient is pediatric (< 18 years or < 40kg)"""
        return self.age_years < 18 or self.weight_kg < 40

    @property
    def age_in_months(self) -> int:
        """Total age in months"""
        return self.age_years * 12 + (self.age_months or 0)


class PhysiologicalParameters(BaseModel):
    """Physiological and lab parameters for dose adjustment"""

    # Renal function
    serum_creatinine_mg_dl: Optional[float] = Field(None, gt=0, description="Serum creatinine (mg/dL)")
    creatinine_clearance_ml_min: Optional[float] = Field(None, ge=0, description="Calculated CrCl (mL/min)")

    # Hepatic function
    child_pugh_score: Optional[ChildPughScore] = Field(None, description="Child-Pugh classification")
    ast_u_l: Optional[float] = Field(None, ge=0, description="AST (U/L)")
    alt_u_l: Optional[float] = Field(None, ge=0, description="ALT (U/L)")
    total_bilirubin_mg_dl: Optional[float] = Field(None, ge=0, description="Total bilirubin (mg/dL)")

    # Other parameters
    albumin_g_dl: Optional[float] = Field(None, ge=0, le=10, description="Serum albumin (g/dL)")

    @validator('creatinine_clearance_ml_min')
    def validate_crcl(cls, v):
        """CrCl should be physiologically plausible"""
        if v is not None and v > 200:
            raise ValueError("Creatinine clearance exceeds physiological maximum")
        return v


class Patient(BaseModel):
    """Complete patient model for antibiotic advisor"""

    # Core demographics
    demographics: PatientDemographics

    # Physiological parameters
    physiology: PhysiologicalParameters = Field(default_factory=PhysiologicalParameters)

    # Allergy profile
    allergies: List[AllergyProfile] = Field(default_factory=list)

    # Clinical context
    is_hospitalized: bool = Field(False, description="Currently hospitalized")
    is_icu: bool = Field(False, description="Currently in ICU")
    prior_antibiotics_30d: List[str] = Field(default_factory=list, description="Antibiotics in last 30 days")

    def calculate_creatinine_clearance(self) -> float:
        """
        Calculate creatinine clearance using Cockcroft-Gault equation

        CrCl (mL/min) = [(140 - age) × weight] / (72 × SCr) × 0.85 (if female)

        Returns:
            Estimated creatinine clearance in mL/min
        """
        if self.physiology.creatinine_clearance_ml_min is not None:
            # Use provided value if available
            return self.physiology.creatinine_clearance_ml_min

        if self.physiology.serum_creatinine_mg_dl is None:
            # Cannot calculate without serum creatinine
            return None

        age = self.demographics.age_years
        weight = self.demographics.weight_kg
        scr = self.physiology.serum_creatinine_mg_dl

        crcl = ((140 - age) * weight) / (72 * scr)

        # Adjust for female patients
        if self.demographics.gender == Gender.FEMALE:
            crcl *= 0.85

        return round(crcl, 1)

    def has_penicillin_allergy(self) -> bool:
        """Check if patient has penicillin allergy"""
        return any(
            'penicillin' in allergy.drug_class.lower() or
            'beta-lactam' in allergy.drug_class.lower() or
            'β-lactam' in allergy.drug_class.lower()
            for allergy in self.allergies
        )

    def has_severe_penicillin_allergy(self) -> bool:
        """Check if patient has severe (Type I) penicillin allergy"""
        return any(
            ('penicillin' in allergy.drug_class.lower() or 'beta-lactam' in allergy.drug_class.lower()) and
            allergy.allergy_type == AllergyType.TYPE_I_ANAPHYLAXIS
            for allergy in self.allergies
        )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


# Example usage
if __name__ == "__main__":
    # Example: 35-year-old male with moderate renal impairment
    patient = Patient(
        demographics=PatientDemographics(
            age_years=35,
            gender=Gender.MALE,
            weight_kg=75,
            height_cm=175
        ),
        physiology=PhysiologicalParameters(
            serum_creatinine_mg_dl=1.8,
            albumin_g_dl=3.5
        ),
        allergies=[
            AllergyProfile(
                drug_class="sulfonamide",
                allergy_type=AllergyType.INTOLERANCE,
                description="Mild rash"
            )
        ]
    )

    print(f"Patient CrCl: {patient.calculate_creatinine_clearance()} mL/min")
    print(f"Is pediatric: {patient.demographics.is_pediatric}")
    print(f"Has penicillin allergy: {patient.has_penicillin_allergy()}")
