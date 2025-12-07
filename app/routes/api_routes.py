"""
API Routes - JSON Endpoints
"""

from flask import request, jsonify
from app.routes import api_bp
from app.models.patient import Patient, PatientDemographics, PhysiologicalParameters, AllergyProfile
from app.models.infection import InfectionProfile
from app.models.prescription import Prescription
from app.services.drug_registry import DrugRegistry
from app.services.clinical_decision_engine import ClinicalDecisionEngine
from config.config import Config


# Initialize services (singleton pattern)
registry = DrugRegistry(Config.REGISTRY_PATH)
decision_engine = ClinicalDecisionEngine(registry)


@api_bp.route('/recommend', methods=['POST'])
def recommend():
    """
    Generate antibiotic recommendation

    Request body:
    {
        "patient": {...},
        "infection": {...}
    }

    Returns:
    {
        "recommendation": {...}
    }
    """
    try:
        data = request.get_json()

        # Parse patient data
        patient_data = data.get('patient', {})
        patient = Patient(**patient_data)

        # Parse infection data
        infection_data = data.get('infection', {})
        infection = InfectionProfile(**infection_data)

        # Generate recommendation
        prescription = decision_engine.generate_recommendation(patient, infection)

        # Convert to dict (Pydantic model_dump)
        result = prescription.dict() if hasattr(prescription, 'dict') else prescription.__dict__

        return jsonify({
            "status": "success",
            "recommendation": result
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@api_bp.route('/drugs/search', methods=['GET'])
def search_drugs():
    """
    Search drugs by generic name

    Query params:
        generic: Generic drug name

    Returns:
        List of matching drugs
    """
    generic_name = request.args.get('generic', '')

    if not generic_name:
        return jsonify({
            "status": "error",
            "message": "Generic name required"
        }), 400

    drugs = registry.find_by_generic(generic_name)

    return jsonify({
        "status": "success",
        "drugs": drugs,
        "count": len(drugs)
    })


@api_bp.route('/drugs/antipseudomonal', methods=['GET'])
def antipseudomonal_drugs():
    """Get all antipseudomonal drugs"""
    drugs = registry.find_antipseudomonal()

    return jsonify({
        "status": "success",
        "drugs": drugs,
        "count": len(drugs)
    })


@api_bp.route('/drugs/anti-mrsa', methods=['GET'])
def anti_mrsa_drugs():
    """Get all anti-MRSA drugs"""
    drugs = registry.find_anti_mrsa()

    return jsonify({
        "status": "success",
        "drugs": drugs,
        "count": len(drugs)
    })


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "BAA-2025",
        "version": "1.0.0",
        "registry_loaded": len(registry._drugs) > 0
    })
