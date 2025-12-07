"""
Netlify Function: Generate Antibiotic Recommendation

This serverless function handles the core recommendation logic
"""

import json
import sys
import os
from pathlib import Path

# Add project root to path
function_dir = Path(__file__).parent
project_root = function_dir.parent.parent
sys.path.insert(0, str(project_root))

from app.models.patient import Patient, PatientDemographics, PhysiologicalParameters, AllergyProfile
from app.models.infection import InfectionProfile
from app.services.drug_registry import DrugRegistry
from app.services.clinical_decision_engine import ClinicalDecisionEngine


# Initialize services (cached across invocations)
REGISTRY_PATH = project_root / "data" / "registry"
registry = DrugRegistry(REGISTRY_PATH)
decision_engine = ClinicalDecisionEngine(registry)


def handler(event, context):
    """
    Netlify Function handler

    Args:
        event: Request event
        context: Request context

    Returns:
        Response dict
    """

    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    }

    # Handle OPTIONS request for CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    # Only accept POST
    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({
                'status': 'error',
                'message': 'Method not allowed. Use POST.'
            })
        }

    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))

        # Extract patient and infection data
        patient_data = body.get('patient', {})
        infection_data = body.get('infection', {})

        # Validate and create models
        patient = Patient(**patient_data)
        infection = InfectionProfile(**infection_data)

        # Generate recommendation
        prescription = decision_engine.generate_recommendation(patient, infection)

        # Convert to dict (handle Pydantic models)
        if hasattr(prescription, 'dict'):
            result = prescription.dict()
        elif hasattr(prescription, 'model_dump'):
            result = prescription.model_dump()
        else:
            result = prescription.__dict__

        # Convert nested Pydantic models
        def convert_pydantic(obj):
            if hasattr(obj, 'dict'):
                return obj.dict()
            elif hasattr(obj, 'model_dump'):
                return obj.model_dump()
            elif isinstance(obj, dict):
                return {k: convert_pydantic(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_pydantic(item) for item in obj]
            else:
                return obj

        result = convert_pydantic(result)

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'success',
                'recommendation': result
            })
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        }
