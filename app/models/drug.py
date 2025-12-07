"""
Drug Data Models

Represents medications from the Registar lijekova Bosne i Hercegovine 2025
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class RegulatoryStatus(str, Enum):
    """BiH regulatory status"""
    RP = "Rp"   # Standard prescription (Recept)
    ZU = "ZU"   # Hospital/Clinical use only (Zdravstvena ustanova)
    RP_ZU = "Rp/ZU"  # Both prescription and hospital use


class ATCClass(str, Enum):
    """Major ATC classifications relevant to antimicrobials"""
    # Antibacterials (J01)
    J01AA = "J01AA"  # Tetracyclines
    J01CA = "J01CA"  # Penicillins with extended spectrum
    J01CE = "J01CE"  # Beta-lactamase sensitive penicillins
    J01CF = "J01CF"  # Beta-lactamase resistant penicillins
    J01CR = "J01CR"  # Combinations of penicillins
    J01DB = "J01DB"  # First-generation cephalosporins
    J01DC = "J01DC"  # Second-generation cephalosporins
    J01DD = "J01DD"  # Third-generation cephalosporins
    J01DE = "J01DE"  # Fourth-generation cephalosporins
    J01DI = "J01DI"  # Other cephalosporins and beta-lactamase inhibitors
    J01DH = "J01DH"  # Carbapenems
    J01FA = "J01FA"  # Macrolides
    J01FF = "J01FF"  # Lincosamides
    J01GB = "J01GB"  # Aminoglycosides
    J01MA = "J01MA"  # Fluoroquinolones
    J01XA = "J01XA"  # Glycopeptides
    J01XB = "J01XB"  # Polymyxins
    J01XD = "J01XD"  # Imidazole derivatives
    J01XX = "J01XX"  # Other antibacterials

    # Antifungals (J02)
    J02AA = "J02AA"  # Antibiotics
    J02AB = "J02AB"  # Imidazole derivatives
    J02AC = "J02AC"  # Triazole derivatives
    J02AX = "J02AX"  # Other antimycotics

    # Antivirals (J05)
    J05AB = "J05AB"  # Nucleoside and nucleotide reverse transcriptase inhibitors
    J05AE = "J05AE"  # Protease inhibitors
    J05AF = "J05AF"  # Nucleoside and nucleotide reverse transcriptase inhibitors
    J05AG = "J05AG"  # Non-nucleoside reverse transcriptase inhibitors
    J05AH = "J05AH"  # Neuraminidase inhibitors
    J05AP = "J05AP"  # Antivirals for treatment of HCV infections
    J05AR = "J05AR"  # Antivirals for treatment of HIV infections, combinations
    J05AX = "J05AX"  # Other antivirals


class FormulationType(str, Enum):
    """Drug formulation types"""
    # Oral
    TABLET = "tablet"
    CAPSULE = "capsule"
    SUSPENSION = "oral_suspension"
    GRANULES = "granules_for_suspension"
    SOLUTION = "oral_solution"
    SACHET = "sachet"

    # Parenteral
    INJECTION_POWDER = "powder_for_injection"
    INFUSION_POWDER = "powder_for_infusion"
    INJECTION_SOLUTION = "solution_for_injection"
    INFUSION_SOLUTION = "solution_for_infusion"
    INFUSION_CONCENTRATE = "concentrate_for_infusion"

    # Topical
    CREAM = "cream"
    OINTMENT = "ointment"
    EYE_DROPS = "eye_drops"


class RouteOfAdministration(str, Enum):
    """Routes of administration"""
    PO = "oral"
    IV = "intravenous"
    IM = "intramuscular"
    SC = "subcutaneous"
    TOPICAL = "topical"
    OPHTHALMIC = "ophthalmic"
    INHALATION = "inhalation"


class DrugFormulation(BaseModel):
    """Specific formulation of a drug"""
    formulation_type: FormulationType
    strength: str = Field(..., description="Strength (e.g., '500mg', '1g', '250mg/5ml')")
    route: RouteOfAdministration
    unit: str = Field(..., description="Unit (e.g., 'mg', 'g', 'IU')")


class Drug(BaseModel):
    """
    Complete drug entry from BiH Registry 2025

    Represents a single trade name product with all its formulations
    """
    # Identification
    generic_name: str = Field(..., description="International Non-proprietary Name (INN)")
    trade_name: str = Field(..., description="Brand name registered in BiH")
    manufacturer: str = Field(..., description="Marketing Authorization Holder")

    # Classification
    atc_code: str = Field(..., description="Anatomical Therapeutic Chemical code")
    atc_class: Optional[ATCClass] = Field(None, description="Major ATC class")

    # Regulatory
    regulatory_status: RegulatoryStatus = Field(..., description="BiH regulatory status (Rp/ZU)")
    registration_number: Optional[str] = Field(None, description="BiH registration number")

    # Formulations
    formulations: List[DrugFormulation] = Field(..., description="Available formulations")

    # Clinical metadata
    is_antipseudomonal: bool = Field(False, description="Active against Pseudomonas aeruginosa")
    is_anti_mrsa: bool = Field(False, description="Active against MRSA")
    is_carbapenem: bool = Field(False, description="Carbapenem class")
    is_reserved: bool = Field(False, description="Reserved/restricted use antibiotic")

    # Pregnancy/Lactation (FDA categories mapped to BiH)
    pregnancy_category: Optional[str] = Field(None, description="FDA pregnancy category")

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


class DrugSubstitution(BaseModel):
    """
    Maps international guideline drugs to BiH equivalents

    Example: Nafcillin (USA) → Kloksacilin/Syntarpen (BiH)
    """
    international_name: str = Field(..., description="Drug name in international guidelines")
    bih_generic: str = Field(..., description="BiH equivalent generic name")
    bih_brands: List[str] = Field(..., description="Available brands in BiH")
    substitution_notes: Optional[str] = Field(None, description="Clinical notes on substitution")
    dose_adjustment_needed: bool = Field(False, description="Whether dose adjustment needed")


# Example drug entries
if __name__ == "__main__":
    # Example: Ceftriaxone (Longaceph) - Hospital workhorse
    ceftriaxone_longaceph = Drug(
        generic_name="Ceftriakson",
        trade_name="LONGACEPH",
        manufacturer="Medochemie",
        atc_code="J01DD04",
        atc_class=ATCClass.J01DD,
        regulatory_status=RegulatoryStatus.RP_ZU,
        formulations=[
            DrugFormulation(
                formulation_type=FormulationType.INJECTION_POWDER,
                strength="1g",
                route=RouteOfAdministration.IV,
                unit="g"
            ),
            DrugFormulation(
                formulation_type=FormulationType.INJECTION_POWDER,
                strength="2g",
                route=RouteOfAdministration.IV,
                unit="g"
            )
        ],
        is_antipseudomonal=False,
        is_anti_mrsa=False,
        is_carbapenem=False,
        is_reserved=False,
        pregnancy_category="B"
    )

    print(f"Drug: {ceftriaxone_longaceph.trade_name}")
    print(f"Generic: {ceftriaxone_longaceph.generic_name}")
    print(f"Status: {ceftriaxone_longaceph.regulatory_status}")
    print(f"Formulations: {len(ceftriaxone_longaceph.formulations)}")

    # Example: Substitution mapping
    nafcillin_sub = DrugSubstitution(
        international_name="Nafcillin",
        bih_generic="Kloksacilin",
        bih_brands=["SYNTARPEN"],
        substitution_notes="Nafcillin unavailable in BiH. Kloksacilin (Syntarpen) is the only beta-lactamase resistant penicillin available.",
        dose_adjustment_needed=False
    )

    print(f"\nSubstitution: {nafcillin_sub.international_name} → {nafcillin_sub.bih_generic}")
    print(f"Available as: {', '.join(nafcillin_sub.bih_brands)}")
