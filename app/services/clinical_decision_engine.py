"""
Clinical Decision Engine

Hard-coded logic trees for antibiotic selection based on infection site,
patient demographics, and clinical severity.

This is the "intelligence" of BAA-2025 - deterministic, not probabilistic.
"""

from typing import List, Dict, Optional
from app.models.patient import Patient
from app.models.infection import InfectionProfile, InfectionSite, InfectionSeverity, InfectionAcquisition
from app.models.prescription import Prescription, Recommendation, DoseCalculation, SafetyWarning
from app.services.drug_registry import DrugRegistry


class ClinicalDecisionEngine:
    """
    Implements hard-coded clinical decision trees for antibiotic selection

    Each method represents a specific clinical scenario with explicit logic
    """

    def __init__(self, registry: DrugRegistry):
        """
        Initialize decision engine

        Args:
            registry: Drug registry for availability checking
        """
        self.registry = registry

    def generate_recommendation(
        self,
        patient: Patient,
        infection: InfectionProfile
    ) -> Prescription:
        """
        Main entry point: Generate antibiotic recommendation

        Args:
            patient: Patient demographics and physiology
            infection: Infection characterization

        Returns:
            Complete prescription with primary and alternative recommendations
        """
        # Route to specific scenario handler
        if infection.site == InfectionSite.CAP:
            return self._cap_logic(patient, infection)
        elif infection.site == InfectionSite.PYELONEPHRITIS:
            return self._pyelonephritis_logic(patient, infection)
        elif infection.site == InfectionSite.VAP:
            return self._vap_logic(patient, infection)
        elif infection.site == InfectionSite.MENINGITIS:
            return self._meningitis_logic(patient, infection)
        elif infection.site == InfectionSite.OTITIS_MEDIA:
            return self._otitis_media_logic(patient, infection)
        elif infection.site == InfectionSite.CYSTITIS_UNCOMPLICATED:
            return self._uncomplicated_cystitis_logic(patient, infection)
        elif infection.site == InfectionSite.CELLULITIS:
            return self._cellulitis_logic(patient, infection)
        else:
            # Fallback for unimplemented scenarios
            return self._generic_recommendation(patient, infection)

    def _cap_logic(self, patient: Patient, infection: InfectionProfile) -> Prescription:
        """
        Community-Acquired Pneumonia (CAP) Logic

        Implements IDSA/ATS guidelines adapted for BiH availability
        """
        clinical_assessment = f"Community-Acquired Pneumonia in {patient.demographics.age_years}-year-old {patient.demographics.gender}"

        # Severity stratification
        if infection.severity in [InfectionSeverity.SEVERE, InfectionSeverity.CRITICAL] or infection.is_septic():
            # Severe CAP → Hospital admission
            severity_assessment = "Severe CAP requiring hospitalization"

            # Primary: Ceftriaxone (BiH hospital workhorse)
            primary = self._build_ceftriaxone_recommendation(
                patient=patient,
                indication="Severe Community-Acquired Pneumonia",
                dose_g=2.0,
                frequency="q24h",
                duration_days=7,
                is_primary=True
            )

            # Alternative for beta-lactam allergy
            alternatives = []
            if patient.has_severe_penicillin_allergy():
                # Severe allergy → Fluoroquinolone
                levo_rec = self._build_levofloxacin_recommendation(
                    patient=patient,
                    indication="Severe CAP (beta-lactam allergy)",
                    alternative_to="Ceftriaxone",
                    reason="Severe penicillin allergy"
                )
                alternatives.append(levo_rec)
            else:
                # Consider adding macrolide for atypical coverage
                azithro_rec = self._build_azithromycin_recommendation(
                    patient=patient,
                    indication="Atypical coverage (add to beta-lactam)",
                    is_additional=True
                )
                alternatives.append(azithro_rec)

            return Prescription(
                clinical_assessment=clinical_assessment,
                diagnosis="Community-Acquired Pneumonia (Severe)",
                severity_assessment=severity_assessment,
                primary_recommendation=primary,
                alternative_recommendations=alternatives,
                bih_availability_confirmed=True,
                reassessment_timing="48-72 hours",
                culture_guidance="Blood cultures recommended before antibiotics",
                deescalation_plan="De-escalate to oral therapy when clinically stable and afebrile for 24-48 hours",
                guideline_references=["IDSA/ATS CAP Guidelines 2019", "BiH CAP Protocol 2024"]
            )

        else:
            # Mild-Moderate CAP → Outpatient
            severity_assessment = "Mild-moderate CAP appropriate for outpatient treatment"

            # Primary: Amoxicillin (first-line outpatient)
            amox_drugs = self.registry.find_by_generic("amoksicilin")
            brands = [d["trade_name"] for d in amox_drugs]

            dose_calc = DoseCalculation(
                dose_amount=1000,
                dose_unit="mg",
                frequency="q8h",
                duration_days=5,
                total_daily_dose=3000,
                total_course_dose=15000,
                calculation_notes="Standard adult dose for CAP"
            )

            primary = Recommendation(
                generic_name="Amoksicilin",
                trade_names=brands,
                manufacturer_options=[d["manufacturer"] for d in amox_drugs],
                formulation="500mg Capsules",
                route="oral",
                dose_calculation=dose_calc,
                regulatory_status="Rp",
                prescription_type="outpatient",
                indication="Community-Acquired Pneumonia",
                rationale="First-line therapy for outpatient CAP per BiH guidelines. Excellent pneumococcal coverage.",
                coverage=["Streptococcus pneumoniae", "Haemophilus influenzae", "Moraxella catarrhalis"],
                warnings=[],
                monitoring_required=["Clinical response at 48-72 hours"],
                is_primary=True,
                prescription_instructions=f"Prescribe: Amoksicilin 500mg capsules #30\\nSig: Take 2 capsules (1000mg) every 8 hours for 5 days",
                patient_instructions="Take with food to reduce stomach upset. Complete full 5-day course even if feeling better. Return if fever persists >3 days or worsening symptoms."
            )

            # Alternative: Azithromycin (for atypical or macrolide preference)
            azithro_rec = self._build_azithromycin_recommendation(
                patient=patient,
                indication="CAP (alternative - atypical coverage)",
                alternative_to="Amoxicillin",
                reason="Suspicion of atypical pathogen (Mycoplasma, Chlamydophila) or penicillin intolerance"
            )

            # Alternative: Doxycycline (for allergy)
            doxy_drugs = self.registry.find_by_generic("doksiciklin")
            doxy_brands = [d["trade_name"] for d in doxy_drugs]

            doxy_dose = DoseCalculation(
                dose_amount=100,
                dose_unit="mg",
                frequency="q12h",
                duration_days=7,
                total_daily_dose=200,
                total_course_dose=1400,
                calculation_notes="Standard doxycycline dosing for CAP"
            )

            doxy_rec = Recommendation(
                generic_name="Doksiciklin",
                trade_names=doxy_brands,
                manufacturer_options=[d["manufacturer"] for d in doxy_drugs],
                formulation="100mg Capsules",
                route="oral",
                dose_calculation=doxy_dose,
                regulatory_status="Rp",
                prescription_type="outpatient",
                indication="CAP (penicillin allergy)",
                rationale="Alternative for patients with penicillin allergy",
                coverage=["Streptococcus pneumoniae", "Atypical pathogens"],
                warnings=[
                    SafetyWarning(
                        severity="warning",
                        category="contraindication",
                        message="Contraindicated in pregnancy (Category D) and children <8 years",
                        action_required="Verify not pregnant and age >8 years"
                    )
                ],
                monitoring_required=["Clinical response"],
                is_primary=False,
                alternative_to="Amoksicilin",
                reason_for_alternative="Penicillin allergy",
                prescription_instructions=f"Prescribe: Doksiciklin 100mg capsules #14\\nSig: Take 1 capsule every 12 hours for 7 days",
                patient_instructions="Take with full glass of water. Avoid lying down for 30 minutes after dose. Photosensitivity risk - use sunscreen."
            )

            return Prescription(
                clinical_assessment=clinical_assessment,
                diagnosis="Community-Acquired Pneumonia (Mild-Moderate)",
                severity_assessment=severity_assessment,
                primary_recommendation=primary,
                alternative_recommendations=[azithro_rec, doxy_rec],
                bih_availability_confirmed=True,
                reassessment_timing="48-72 hours",
                culture_guidance="Blood cultures not routinely indicated for outpatient CAP",
                deescalation_plan="N/A (oral therapy from start)",
                guideline_references=["IDSA/ATS CAP Guidelines 2019"]
            )

    def _pyelonephritis_logic(self, patient: Patient, infection: InfectionProfile) -> Prescription:
        """
        Acute Pyelonephritis Logic
        """
        clinical_assessment = f"Acute pyelonephritis in {patient.demographics.age_years}-year-old {patient.demographics.gender}"

        if patient.is_hospitalized or infection.severity in [InfectionSeverity.SEVERE, InfectionSeverity.CRITICAL]:
            # Hospitalized → IV therapy
            severity_assessment = "Severe pyelonephritis requiring hospitalization and IV antibiotics"

            # Primary: Ceftriaxone 2g IV q24h
            primary = self._build_ceftriaxone_recommendation(
                patient=patient,
                indication="Acute Pyelonephritis",
                dose_g=2.0,
                frequency="q24h",
                duration_days=14,
                is_primary=True
            )

            # Alternative: Ciprofloxacin IV (if fluoroquinolone resistance <10%)
            cipro_rec = self._build_ciprofloxacin_iv_recommendation(
                patient=patient,
                indication="Pyelonephritis (alternative)",
                alternative_to="Ceftriaxone",
                reason="Beta-lactam allergy or ceftriaxone unavailable"
            )

            return Prescription(
                clinical_assessment=clinical_assessment,
                diagnosis="Acute Pyelonephritis (Severe)",
                severity_assessment=severity_assessment,
                primary_recommendation=primary,
                alternative_recommendations=[cipro_rec],
                bih_availability_confirmed=True,
                reassessment_timing="48-72 hours",
                culture_guidance="Urine culture MANDATORY before antibiotics. Blood cultures if septic.",
                deescalation_plan="Switch to oral therapy (cefixime or ciprofloxacin) when afebrile and clinically improving. Complete 14 days total.",
                guideline_references=["IDSA UTI Guidelines 2011", "EAU Guidelines 2024"]
            )
        else:
            # Outpatient → Oral therapy
            severity_assessment = "Uncomplicated pyelonephritis appropriate for outpatient oral therapy"

            # Primary: Ciprofloxacin PO (if local resistance <10%)
            cipro_drugs = self.registry.find_by_generic("ciprofloksacin")
            oral_cipro = [d for d in cipro_drugs if any(f["route"] == "oral" for f in d.get("formulations", []))]
            brands = [d["trade_name"] for d in oral_cipro]

            cipro_dose = DoseCalculation(
                dose_amount=500,
                dose_unit="mg",
                frequency="q12h",
                duration_days=7,
                total_daily_dose=1000,
                total_course_dose=7000,
                calculation_notes="Standard ciprofloxacin dosing for pyelonephritis"
            )

            primary = Recommendation(
                generic_name="Ciprofloksacin",
                trade_names=brands,
                manufacturer_options=[d["manufacturer"] for d in oral_cipro],
                formulation="500mg Tablets",
                route="oral",
                dose_calculation=cipro_dose,
                regulatory_status="Rp",
                prescription_type="outpatient",
                indication="Acute Pyelonephritis",
                rationale="First-line for outpatient pyelonephritis (if local E. coli resistance <10%)",
                coverage=["E. coli", "Klebsiella pneumoniae", "Proteus mirabilis"],
                warnings=[
                    SafetyWarning(
                        severity="warning",
                        category="side_effect",
                        message="Fluoroquinolone warnings: Tendon rupture risk, QT prolongation, peripheral neuropathy",
                        action_required="Counsel patient on warning signs. Avoid if history of tendon disorders."
                    ),
                    SafetyWarning(
                        severity="caution",
                        category="resistance",
                        message="E. coli fluoroquinolone resistance may exceed 30% in some BiH regions",
                        action_required="Obtain urine culture before treatment. Adjust based on sensitivity."
                    )
                ],
                monitoring_required=["Clinical response at 48-72 hours", "Urine culture results"],
                is_primary=True,
                prescription_instructions="Prescribe: Ciprofloksacin 500mg tablets #14\\nSig: Take 1 tablet every 12 hours for 7 days",
                patient_instructions="Take on empty stomach (1 hour before or 2 hours after meals) for best absorption. Drink plenty of fluids. Avoid dairy products and antacids within 2 hours of dose."
            )

            return Prescription(
                clinical_assessment=clinical_assessment,
                diagnosis="Acute Pyelonephritis (Uncomplicated)",
                severity_assessment=severity_assessment,
                primary_recommendation=primary,
                alternative_recommendations=[],
                bih_availability_confirmed=True,
                reassessment_timing="48-72 hours",
                culture_guidance="Urine culture MANDATORY before antibiotics",
                deescalation_plan="Adjust antibiotic based on culture results if no improvement by 48-72 hours",
                guideline_references=["IDSA UTI Guidelines 2011"]
            )

    def _vap_logic(self, patient: Patient, infection: InfectionProfile) -> Prescription:
        """
        Ventilator-Associated Pneumonia (VAP) Logic

        High MDR risk → Broad-spectrum empiric therapy
        """
        clinical_assessment = f"Ventilator-Associated Pneumonia in ICU patient (intubated >{infection.duration_days or 'unknown'} days)"
        severity_assessment = "High-risk HAP/VAP requiring broad-spectrum empiric therapy with double Pseudomonas coverage and MRSA coverage"

        # Backbone: Antipseudomonal beta-lactam
        # Option 1: Meropenem (preferred if high ESBL risk)
        # Option 2: Piperacillin/Tazobactam

        mero_drugs = self.registry.find_by_generic("meropenem")
        mero_brands = [d["trade_name"] for d in mero_drugs]

        mero_dose = DoseCalculation(
            dose_amount=1000,
            dose_unit="mg",
            frequency="q8h",
            duration_days=8,
            infusion_type="extended_infusion",
            infusion_duration_min=180,
            total_daily_dose=3000,
            total_course_dose=24000,
            calculation_notes="Extended infusion (3-hour) for optimal Time>MIC in critically ill patients"
        )

        backbone_rec = Recommendation(
            generic_name="Meropenem",
            trade_names=mero_brands,
            manufacturer_options=[d["manufacturer"] for d in mero_drugs],
            formulation="1g Powder for Injection",
            route="intravenous",
            dose_calculation=mero_dose,
            regulatory_status="ZU",
            prescription_type="hospital",
            indication="Ventilator-Associated Pneumonia (empiric therapy)",
            rationale="Broad-spectrum carbapenem with excellent Pseudomonas and ESBL coverage. Extended infusion optimizes PK/PD.",
            coverage=["Pseudomonas aeruginosa", "ESBL-producing Enterobacteriaceae", "Acinetobacter baumannii"],
            warnings=[
                SafetyWarning(
                    severity="critical",
                    category="stewardship",
                    message="CARBAPENEM - RESERVED ANTIBIOTIC. Use only for high-risk HAP/VAP or documented resistance.",
                    action_required="Obtain respiratory cultures (BAL/mini-BAL) before initiation. De-escalate based on culture results."
                )
            ],
            monitoring_required=["Daily clinical assessment", "Respiratory culture results", "Renal function"],
            is_primary=True,
            prescription_instructions="Order: Meropenem 1g IV q8h via extended infusion (3 hours)\\nHospital pharmacy will prepare and deliver",
            patient_instructions="N/A (intubated patient)"
        )

        # Additional agent 1: Aminoglycoside (double Pseudomonas coverage)
        amikacin_drugs = self.registry.find_by_generic("amikacin")
        amikacin_brands = [d["trade_name"] for d in amikacin_drugs]

        amikacin_dose = DoseCalculation(
            dose_amount=patient.demographics.weight_kg * 15,  # 15 mg/kg
            dose_unit="mg",
            frequency="q24h",
            duration_days=5,
            total_daily_dose=patient.demographics.weight_kg * 15,
            total_course_dose=patient.demographics.weight_kg * 15 * 5,
            calculation_notes=f"Weight-based dosing: 15 mg/kg (patient weight: {patient.demographics.weight_kg}kg). Once-daily dosing. Limit to 5-7 days to reduce nephrotoxicity."
        )

        amikacin_rec = Recommendation(
            generic_name="Amikacin",
            trade_names=amikacin_brands,
            manufacturer_options=[d["manufacturer"] for d in amikacin_drugs],
            formulation="500mg/2mL Solution for Injection",
            route="intravenous",
            dose_calculation=amikacin_dose,
            regulatory_status="ZU",
            prescription_type="hospital",
            indication="VAP - Double Pseudomonas coverage",
            rationale="Aminoglycoside for synergistic double coverage of Pseudomonas. Once-daily dosing reduces toxicity.",
            coverage=["Pseudomonas aeruginosa", "Acinetobacter baumannii"],
            warnings=[
                SafetyWarning(
                    severity="critical",
                    category="toxicity",
                    message="NEPHROTOXIC and OTOTOXIC. Limit duration to 5-7 days.",
                    action_required="Monitor: Daily SCr, trough level (target <5 mcg/mL), consider audiometry if prolonged use"
                )
            ],
            monitoring_required=["Trough levels (before 3rd dose)", "Daily renal function", "Consider therapeutic drug monitoring"],
            is_primary=False,
            prescription_instructions=f"Order: Amikacin {int(amikacin_dose.dose_amount)}mg IV once daily\\nMonitor trough levels",
            patient_instructions="N/A (intubated patient)"
        )

        # Additional agent 2: Vancomycin (MRSA coverage)
        vanco_rec = self._build_vancomycin_recommendation(
            patient=patient,
            indication="VAP - MRSA coverage",
            is_additional=True
        )

        return Prescription(
            clinical_assessment=clinical_assessment,
            diagnosis="Ventilator-Associated Pneumonia",
            severity_assessment=severity_assessment,
            primary_recommendation=backbone_rec,
            additional_agents=[amikacin_rec, vanco_rec],
            alternative_recommendations=[],
            critical_warnings=[
                SafetyWarning(
                    severity="critical",
                    category="stewardship",
                    message="TRIPLE ANTIBIOTIC THERAPY - De-escalation MANDATORY based on culture results",
                    action_required="Review therapy at 48-72 hours. Discontinue unnecessary agents based on culture/clinical response."
                )
            ],
            bih_availability_confirmed=True,
            reassessment_timing="Daily assessment. Formal de-escalation review at 48-72 hours.",
            culture_guidance="OBTAIN respiratory cultures (BAL/mini-BAL) BEFORE antibiotics. Blood cultures if septic.",
            deescalation_plan="De-escalate to narrowest-spectrum agent based on culture results. If no growth and clinical improvement, consider stopping antibiotics at 7-8 days.",
            guideline_references=["IDSA/ATS HAP/VAP Guidelines 2016"]
        )

    def _meningitis_logic(self, patient: Patient, infection: InfectionProfile) -> Prescription:
        """
        Bacterial Meningitis Logic

        EMERGENCY - Immediate high-dose therapy
        """
        # ... implementation
        # Similar pattern to above
        pass

    def _otitis_media_logic(self, patient: Patient, infection: InfectionProfile) -> Prescription:
        """
        Pediatric Otitis Media Logic

        High-dose amoxicillin with precise volume calculations
        """
        # ... implementation
        pass

    def _uncomplicated_cystitis_logic(self, patient: Patient, infection: InfectionProfile) -> Prescription:
        """
        Uncomplicated Cystitis Logic

        Fosfomycin first-line for females
        """
        # ... implementation
        pass

    def _cellulitis_logic(self, patient: Patient, infection: InfectionProfile) -> Prescription:
        """
        Cellulitis Logic

        Beta-lactam coverage for Strep/Staph
        """
        # ... implementation
        pass

    def _generic_recommendation(self, patient: Patient, infection: InfectionProfile) -> Prescription:
        """
        Generic fallback recommendation
        """
        return Prescription(
            clinical_assessment=f"Clinical scenario: {infection.site}",
            diagnosis=infection.site.value,
            severity_assessment="Scenario not yet implemented in BAA-2025",
            primary_recommendation=None,  # Would need to build a basic recommendation
            bih_availability_confirmed=True,
            reassessment_timing="48-72 hours",
            guideline_references=[]
        )

    # Helper methods to build recommendations
    def _build_ceftriaxone_recommendation(
        self,
        patient: Patient,
        indication: str,
        dose_g: float,
        frequency: str,
        duration_days: int,
        is_primary: bool = True
    ) -> Recommendation:
        """Build Ceftriaxone recommendation (common hospital drug)"""
        cef_drugs = self.registry.find_by_generic("ceftriakson")
        brands = [d["trade_name"] for d in cef_drugs]

        dose_calc = DoseCalculation(
            dose_amount=dose_g,
            dose_unit="g",
            frequency=frequency,
            duration_days=duration_days,
            total_daily_dose=dose_g if frequency == "q24h" else dose_g * 2,
            total_course_dose=dose_g * duration_days if frequency == "q24h" else dose_g * 2 * duration_days,
            calculation_notes=f"Standard adult ceftriaxone dosing for {indication}"
        )

        return Recommendation(
            generic_name="Ceftriakson",
            trade_names=brands,
            manufacturer_options=[d["manufacturer"] for d in cef_drugs],
            formulation=f"{int(dose_g)}g Powder for Injection",
            route="intravenous",
            dose_calculation=dose_calc,
            regulatory_status="ZU/Rp",
            prescription_type="hospital",
            indication=indication,
            rationale="Third-generation cephalosporin - BiH hospital workhorse. Excellent Gram-negative and pneumococcal coverage.",
            coverage=["Streptococcus pneumoniae", "Haemophilus influenzae", "Moraxella catarrhalis", "E. coli", "Klebsiella"],
            warnings=[],
            monitoring_required=["Clinical response", "Renal function"],
            is_primary=is_primary,
            prescription_instructions=f"Order: Ceftriakson {dose_g}g IV {frequency} for {duration_days} days\\nHospital pharmacy will prepare",
            patient_instructions="Administered by nursing staff"
        )

    def _build_azithromycin_recommendation(
        self,
        patient: Patient,
        indication: str,
        alternative_to: str = None,
        reason: str = None,
        is_additional: bool = False
    ) -> Recommendation:
        """Build Azithromycin recommendation"""
        azithro_drugs = self.registry.find_by_generic("azitromicin")
        brands = [d["trade_name"] for d in azithro_drugs]

        dose_calc = DoseCalculation(
            dose_amount=500,
            dose_unit="mg",
            frequency="daily",
            duration_days=3,
            total_daily_dose=500,
            total_course_dose=1500,
            calculation_notes="Standard azithromycin 3-day course"
        )

        return Recommendation(
            generic_name="Azitromicin",
            trade_names=brands,
            manufacturer_options=[d["manufacturer"] for d in azithro_drugs],
            formulation="500mg Tablets",
            route="oral",
            dose_calculation=dose_calc,
            regulatory_status="Rp",
            prescription_type="outpatient",
            indication=indication,
            rationale="Macrolide with excellent atypical pathogen coverage (Mycoplasma, Chlamydophila, Legionella)",
            coverage=["Mycoplasma pneumoniae", "Chlamydophila pneumoniae", "Legionella pneumophila", "Streptococcus pneumoniae"],
            warnings=[
                SafetyWarning(
                    severity="warning",
                    category="cardiac",
                    message="QT prolongation risk - especially with other QT-prolonging drugs",
                    action_required="Review medication list for QT-prolonging drugs. Use caution in cardiac patients."
                )
            ],
            monitoring_required=["Clinical response"],
            is_primary=not alternative_to and not is_additional,
            alternative_to=alternative_to,
            reason_for_alternative=reason,
            prescription_instructions="Prescribe: Azitromicin 500mg tablets #3\\nSig: Take 1 tablet once daily for 3 days",
            patient_instructions="Take on empty stomach. Complete full 3-day course. SUMAMED is the most commonly used brand in BiH."
        )

    def _build_ciprofloxacin_iv_recommendation(
        self,
        patient: Patient,
        indication: str,
        alternative_to: str = None,
        reason: str = None
    ) -> Recommendation:
        """Build IV Ciprofloxacin recommendation"""
        # Implementation similar to above
        pass

    def _build_levofloxacin_recommendation(
        self,
        patient: Patient,
        indication: str,
        alternative_to: str = None,
        reason: str = None
    ) -> Recommendation:
        """Build Levofloxacin recommendation"""
        # Implementation similar to above
        pass

    def _build_vancomycin_recommendation(
        self,
        patient: Patient,
        indication: str,
        is_additional: bool = False
    ) -> Recommendation:
        """Build Vancomycin recommendation for MRSA coverage"""
        # Implementation similar to above
        pass
