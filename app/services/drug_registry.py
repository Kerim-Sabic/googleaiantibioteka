"""
Drug Registry Service

Loads and queries the BiH 2025 drug registry
Implements the "Closed-World Assumption" - only registered drugs exist
"""

import json
from pathlib import Path
from typing import List, Optional, Dict
from app.models.drug import Drug, DrugSubstitution


class DrugRegistry:
    """
    Central repository of all drugs registered in BiH 2025

    This class implements the "hard-coded" pharmacy - no hallucinations allowed.
    """

    def __init__(self, registry_path: Path):
        """
        Initialize drug registry from JSON files

        Args:
            registry_path: Path to registry JSON files
        """
        self.registry_path = Path(registry_path)
        self._drugs: Dict[str, List[Drug]] = {}
        self._load_registry()

    def _load_registry(self):
        """Load all registry JSON files"""
        registry_files = [
            "antibacterials_beta_lactams.json",
            "cephalosporins.json",
            "carbapenems_fluoroquinolones.json",
            "other_antibacterials.json",
            "antifungals_antivirals.json"
        ]

        for filename in registry_files:
            filepath = self.registry_path / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._parse_registry_file(data)

    def _parse_registry_file(self, data: dict):
        """Parse registry JSON and extract drugs"""
        # Skip metadata
        for key, value in data.items():
            if key == "metadata":
                continue
            if isinstance(value, dict):
                self._extract_drugs_recursive(value)

    def _extract_drugs_recursive(self, data: dict):
        """Recursively extract drug entries from nested structure"""
        for key, value in data.items():
            if isinstance(value, list):
                # This is a list of drugs
                for drug_data in value:
                    if "generic_name" in drug_data:
                        generic = drug_data["generic_name"].lower()
                        if generic not in self._drugs:
                            self._drugs[generic] = []
                        self._drugs[generic].append(drug_data)
            elif isinstance(value, dict):
                self._extract_drugs_recursive(value)

    def find_by_generic(self, generic_name: str) -> List[Dict]:
        """
        Find all brands for a given generic name

        Args:
            generic_name: Generic drug name (INN)

        Returns:
            List of drug entries (all brands)
        """
        generic_normalized = generic_name.lower().strip()
        return self._drugs.get(generic_normalized, [])

    def find_by_trade_name(self, trade_name: str) -> Optional[Dict]:
        """
        Find drug by trade name

        Args:
            trade_name: Brand name

        Returns:
            Drug entry if found, None otherwise
        """
        trade_normalized = trade_name.upper().strip()
        for generic, drugs in self._drugs.items():
            for drug in drugs:
                if drug.get("trade_name", "").upper() == trade_normalized:
                    return drug
        return None

    def find_by_atc(self, atc_code: str) -> List[Dict]:
        """
        Find all drugs with a specific ATC code

        Args:
            atc_code: ATC classification code

        Returns:
            List of drug entries
        """
        results = []
        for generic, drugs in self._drugs.items():
            for drug in drugs:
                if drug.get("atc_code", "").startswith(atc_code):
                    results.append(drug)
        return results

    def find_antipseudomonal(self) -> List[Dict]:
        """Find all drugs with antipseudomonal activity"""
        results = []
        for generic, drugs in self._drugs.items():
            for drug in drugs:
                if drug.get("is_antipseudomonal", False):
                    results.append(drug)
        return results

    def find_anti_mrsa(self) -> List[Dict]:
        """Find all drugs with anti-MRSA activity"""
        results = []
        for generic, drugs in self._drugs.items():
            for drug in drugs:
                if drug.get("is_anti_mrsa", False):
                    results.append(drug)
        return results

    def find_by_regulatory_status(self, status: str) -> List[Dict]:
        """
        Find drugs by regulatory status

        Args:
            status: "Rp" (prescription) or "ZU" (hospital-only)

        Returns:
            List of drug entries
        """
        results = []
        for generic, drugs in self._drugs.items():
            for drug in drugs:
                reg_status = drug.get("regulatory_status", "")
                if status in reg_status:
                    results.append(drug)
        return results

    def is_available(self, generic_name: str) -> bool:
        """
        Check if a drug is available in BiH registry

        This is the "Closed-World" check - critical for preventing hallucinations

        Args:
            generic_name: Generic drug name

        Returns:
            True if drug exists in registry, False otherwise
        """
        return len(self.find_by_generic(generic_name)) > 0

    def get_substitution(self, international_name: str) -> Optional[str]:
        """
        Get BiH substitute for an international guideline drug

        Example: Nafcillin → Kloksacilin

        Args:
            international_name: Drug name from international guidelines

        Returns:
            BiH generic name if substitute exists, None otherwise
        """
        # Hard-coded substitution map
        substitution_map = {
            "nafcillin": "kloksacilin",
            "oxacillin": "kloksacilin",
            "flucloxacillin": "kloksacilin",
            "dicloxacillin": "kloksacilin",
            "oseltamivir": "baloxavir marboxil",  # Xofluza available
            "tamiflu": "baloxavir marboxil"
        }

        normalized = international_name.lower().strip()
        return substitution_map.get(normalized)

    def get_all_brands(self, generic_name: str) -> List[str]:
        """
        Get all trade names for a generic drug

        Args:
            generic_name: Generic drug name

        Returns:
            List of brand names
        """
        drugs = self.find_by_generic(generic_name)
        return [drug["trade_name"] for drug in drugs]

    def get_formulations(self, generic_name: str, trade_name: Optional[str] = None) -> List[Dict]:
        """
        Get available formulations for a drug

        Args:
            generic_name: Generic drug name
            trade_name: Specific brand (optional)

        Returns:
            List of formulations
        """
        if trade_name:
            drug = self.find_by_trade_name(trade_name)
            return drug.get("formulations", []) if drug else []
        else:
            # Get formulations from first brand
            drugs = self.find_by_generic(generic_name)
            if drugs:
                return drugs[0].get("formulations", [])
            return []


# Example usage
if __name__ == "__main__":
    from config.config import Config

    registry = DrugRegistry(Config.REGISTRY_PATH)

    # Test: Find amoxicillin
    amox_brands = registry.find_by_generic("amoksicilin")
    print(f"Amoxicillin brands: {[d['trade_name'] for d in amox_brands]}")

    # Test: Check if Nafcillin is available (should be False)
    print(f"Nafcillin available: {registry.is_available('nafcillin')}")

    # Test: Get substitution
    sub = registry.get_substitution("nafcillin")
    print(f"Nafcillin → {sub}")

    # Test: Find antipseudomonal drugs
    pseudo_drugs = registry.find_antipseudomonal()
    print(f"Antipseudomonal drugs: {len(pseudo_drugs)} found")

    # Test: Find MRSA-active drugs
    mrsa_drugs = registry.find_anti_mrsa()
    print(f"Anti-MRSA drugs: {len(mrsa_drugs)} found")
