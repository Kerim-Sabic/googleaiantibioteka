"""
Prescription and Recommendation Models

Represents the output of the antibiotic advisor system
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class DoseUnit(str, Enum):
    """Dose units"""
    MG = "mg"
    G = "g"
    IU = "IU"
    MCG = "mcg"
    MG_KG = "mg/kg"
    IU_KG = "IU/kg"


class FrequencyUnit(str, Enum):
    """Dosing frequency"""
    Q4H = "q4h"   # Every 4 hours
    Q6H = "q6h"   # Every 6 hours
    Q8H = "q8h"   # Every 8 hours
    Q12H = "q12h" # Every 12 hours
    Q24H = "q24h" # Every 24 hours
    QD = "daily"  # Once daily
    BID = "bid"   # Twice daily
    TID = "tid"   # Three times daily
    QID = "qid"   # Four times daily
    ONCE = "once" # Single dose


class DoseAdjustmentReason(str, Enum):
    """Reason for dose adjustment"""
    RENAL_IMPAIRMENT = "renal_impairment"
    HEPATIC_IMPAIRMENT = "hepatic_impairment"
    PEDIATRIC_WEIGHT = "pediatric_weight_based"
    ELDERLY = "elderly_age_adjustment"
    OBESITY = "obesity"
    THERAPEUTIC_MONITORING = "therapeutic_drug_monitoring"


class InfusionType(str, Enum):
    """Type of IV infusion"""
    BOLUS = "iv_bolus"
    SHORT_INFUSION = "short_infusion"   # 30-60 min
    STANDARD_INFUSION = "standard_infusion"  # 1-2 hours
    EXTENDED_INFUSION = "extended_infusion"  # 3-4 hours
    CONTINUOUS_INFUSION = "continuous_infusion"  # 24 hours


class DoseCalculation(BaseModel):
    """
    Detailed dose calculation with rationale
    """
    # Dose parameters
    dose_amount: float = Field(..., description="Calculated dose amount")
    dose_unit: DoseUnit = Field(..., description="Dose unit")
    frequency: FrequencyUnit = Field(..., description="Dosing frequency")
    duration_days: int = Field(..., ge=1, description="Treatment duration in days")

    # Route-specific
    infusion_type: Optional[InfusionType] = Field(None, description="Infusion type for IV drugs")
    infusion_duration_min: Optional[int] = Field(None, description="Infusion duration in minutes")

    # Adjustments
    is_adjusted: bool = Field(False, description="Dose adjusted from standard")
    adjustment_reason: Optional[DoseAdjustmentReason] = Field(None, description="Reason for adjustment")
    adjustment_factor: Optional[float] = Field(None, description="Adjustment factor applied")

    # Calculations
    total_daily_dose: float = Field(..., description="Total daily dose")
    total_course_dose: float = Field(..., description="Total course dose")

    # Rationale
    calculation_notes: Optional[str] = Field(None, description="Notes on dose calculation")

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


class SafetyWarning(BaseModel):
    """Safety warning or caution"""
    severity: str = Field(..., description="Severity: 'critical', 'warning', 'caution'")
    category: str = Field(..., description="Category: 'allergy', 'interaction', 'contraindication', etc.")
    message: str = Field(..., description="Warning message")
    action_required: Optional[str] = Field(None, description="Required action")


class Recommendation(BaseModel):
    """
    Single antibiotic recommendation with complete prescribing information
    """
    # Drug identification
    generic_name: str = Field(..., description="Generic name (INN)")
    trade_names: List[str] = Field(..., description="Available brand names in BiH")
    manufacturer_options: List[str] = Field(default_factory=list, description="Manufacturer options")

    # Formulation
    formulation: str = Field(..., description="Formulation type and strength")
    route: str = Field(..., description="Route of administration")

    # Dosing
    dose_calculation: DoseCalculation = Field(..., description="Complete dose calculation")

    # Regulatory
    regulatory_status: str = Field(..., description="BiH regulatory status (Rp/ZU)")
    prescription_type: str = Field(..., description="Prescription type: 'outpatient', 'hospital', 'restricted'")

    # Clinical rationale
    indication: str = Field(..., description="Clinical indication")
    rationale: str = Field(..., description="Why this drug was selected")
    coverage: List[str] = Field(..., description="Pathogen coverage")

    # Safety
    warnings: List[SafetyWarning] = Field(default_factory=list, description="Safety warnings")
    monitoring_required: List[str] = Field(default_factory=list, description="Required monitoring")

    # Alternatives
    is_primary: bool = Field(True, description="Primary recommendation vs alternative")
    alternative_to: Optional[str] = Field(None, description="Alternative to (if applicable)")
    reason_for_alternative: Optional[str] = Field(None, description="Reason this is alternative")

    # Prescription guide
    prescription_instructions: str = Field(..., description="How to write prescription")
    patient_instructions: str = Field(..., description="Patient counseling points")

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


class Prescription(BaseModel):
    """
    Complete antibiotic prescription package

    This is the final output of the BAA-2025 system
    """
    # Clinical assessment summary
    clinical_assessment: str = Field(..., description="Summary of clinical situation")
    diagnosis: str = Field(..., description="Working diagnosis")
    severity_assessment: str = Field(..., description="Severity assessment")

    # Recommendations
    primary_recommendation: Recommendation = Field(..., description="Primary antibiotic recommendation")
    alternative_recommendations: List[Recommendation] = Field(
        default_factory=list,
        description="Alternative options (allergy, stockout, etc.)"
    )

    # Additional antimicrobials (combination therapy)
    additional_agents: List[Recommendation] = Field(
        default_factory=list,
        description="Additional agents for combination therapy"
    )

    # BiH availability confirmation
    bih_availability_confirmed: bool = Field(True, description="All drugs confirmed in BiH registry 2025")
    registry_notes: Optional[str] = Field(None, description="Notes on drug availability")

    # Safety summary
    critical_warnings: List[SafetyWarning] = Field(default_factory=list, description="Critical safety warnings")

    # Follow-up
    reassessment_timing: str = Field(..., description="When to reassess (e.g., '48-72 hours')")
    culture_guidance: Optional[str] = Field(None, description="Guidance on obtaining cultures")
    deescalation_plan: Optional[str] = Field(None, description="De-escalation plan when cultures available")

    # System metadata
    recommendation_timestamp: Optional[str] = Field(None, description="When recommendation generated")
    guideline_references: List[str] = Field(default_factory=list, description="Guidelines referenced")

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


# Example usage
if __name__ == "__main__":
    # Example: Simple CAP prescription
    dose_calc = DoseCalculation(
        dose_amount=1000,
        dose_unit=DoseUnit.MG,
        frequency=FrequencyUnit.Q8H,
        duration_days=7,
        is_adjusted=False,
        total_daily_dose=3000,
        total_course_dose=21000,
        calculation_notes="Standard adult dose for CAP"
    )

    primary_rec = Recommendation(
        generic_name="Amoksicilin",
        trade_names=["Amoxibos", "Sinacillin", "Almacin", "Hiconcil"],
        manufacturer_options=["Bosnalijek", "Galenika", "Alkaloid", "Krka"],
        formulation="500mg Capsules",
        route="oral",
        dose_calculation=dose_calc,
        regulatory_status="Rp",
        prescription_type="outpatient",
        indication="Community-Acquired Pneumonia (CAP)",
        rationale="First-line therapy for outpatient CAP per BiH guidelines",
        coverage=["Streptococcus pneumoniae", "Haemophilus influenzae"],
        warnings=[],
        monitoring_required=["Clinical response at 48-72 hours"],
        is_primary=True,
        prescription_instructions="Prescribe: Amoksicilin 500mg capsules #21\nSig: Take 2 capsules (1000mg) every 8 hours",
        patient_instructions="Take with food to reduce stomach upset. Complete full course even if feeling better."
    )

    prescription = Prescription(
        clinical_assessment="35-year-old male with moderate CAP (CURB-65=2)",
        diagnosis="Community-Acquired Pneumonia",
        severity_assessment="Moderate severity, outpatient treatment appropriate",
        primary_recommendation=primary_rec,
        bih_availability_confirmed=True,
        reassessment_timing="48-72 hours",
        culture_guidance="Blood cultures not routinely indicated for outpatient CAP",
        guideline_references=["BiH CAP Guidelines 2024", "IDSA/ATS CAP Guidelines"]
    )

    print(f"Diagnosis: {prescription.diagnosis}")
    print(f"Primary drug: {prescription.primary_recommendation.generic_name}")
    print(f"Brands: {', '.join(prescription.primary_recommendation.trade_names)}")
    print(f"Dose: {prescription.primary_recommendation.dose_calculation.dose_amount} {prescription.primary_recommendation.dose_calculation.dose_unit} {prescription.primary_recommendation.dose_calculation.frequency}")
